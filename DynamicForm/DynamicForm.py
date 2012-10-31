"""
    Defines the DynamicForm concept (a page made up entirely of page controls / requests handlers so that
    any part of the page can be updated independently
"""

from WebElements.All import Factory
from WebElements import UITemplate
from WebElements.HiddenInputs import HiddenValue
import PageControls
from RequestHandler import RequestHandler
from WebElements.Resources import ResourceFile, ScriptContainer

try:
    from django.core.context_processors import csrf
except ImportError:
    csrf = False


class DynamicForm(RequestHandler):
    """
        Defines the base dynamic form  - a page made where any section can be updated independently from the rest
    """
    template = UITemplate.fromSHPAML("> document")
    elementFactory = Factory
    formatted = False
    if csrf:
        sharedFields = ('csrfmiddlewaretoken', )

    def renderResponse(self, request):
        """
            Override the response rendering to render the main document structure of the page
        """
        document = self.elementFactory.buildFromTemplate(self.template)
        request.response.scripts =  ScriptContainer()
        request.response.scripts.addScript("\n".join(self.initScripts))
        document.setScriptContainer(request.response.scripts)
        document.setProperty('title', self.title(request))
        document.addChildElement(ResourceFile()).setProperty("file", self.favicon(request))
        for resourceFile in self.resourceFiles(request):
            document.addChildElement(ResourceFile()).setProperty("file", resourceFile)

        if csrf:
            token = document.body.addChildElement(HiddenValue('csrfmiddlewaretoken'))
            token.setValue(csrf(request.native)['csrf_token'])
        document.body += self.mainControl
        document.body += request.response.scripts

        self.modifyDocument(document, request)

        return document.toHtml(formatted=self.formatted, request=request)

    def modifyDocument(self, document, request):
        """
            Override to change the structure of the base document
        """
        pass

    def title(self, request):
        """
            Returns the title of the page - by default this is the class name of the DynamicForm subclass
            override this method to change that
        """
        return self.__class__.__name__

    def favicon(self, request):
        """
            Returns the title of the page - by default this is the class name of the DynamicForm subclass
            override this method to change that
        """
        return "images/favicon.png"

    def resourceFiles(self, request):
        """
            Returns the resource files that should be loaded with this page - override this method to change
        """
        return ['javascript/CommonJavascript.js', 'stylesheets/CommonStyleSheet.css']

    class MainControl(PageControls.PageControl):
        """
            Override this controller to define how the body of the page should render
        """
        pass
