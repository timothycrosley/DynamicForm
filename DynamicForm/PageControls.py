"""
    Defines the most basic PageControls that can be subclassed to control sections of a page
"""

import HTTP
from RequestHandler import RequestHandler
from WebElements import UITemplate
from WebElements.All import Factory
from WebElements.Base import WebElement, TemplateElement
from WebElements.Layout import Center, Horizontal
from WebElements.Display import Image, Empty, Label
from WebElements.Resources import ScriptContainer
from WebElements import ClientSide

class PageControl(RequestHandler, WebElement):
    """
        Defines the concept of a page control: The merger of a request handler and a WebElement
    """
    properties = WebElement.properties.copy()
    properties['autoLoad'] = {'action':'classAttribute', 'type':'bool'}
    tagName = "section"
    autoLoad = True
    autoReload = False
    elementFactory = Factory
    _loading = None

    class ClientSide(WebElement.ClientSide):

        def getAll(self, controls, silent=False, params=None, timeout=None):
            return ClientSide.call("DynamicForm.get", controls, silent, params, timout)

        def get(self, silent=False, params=None, timeout=None):
            return ClientSide.call("DynamicForm.get", self, silent, params, timeout)

        def postAll(self, controls, silent=False, params=None, timeout=None):
            return ClientSide.call("DynamicForm.post", controls, silent, params, timout)

        def post(self, silent=False, params=None, timeout=None):
            return ClientSide.call("DynamicForm.post", self, silent, params, timeout)

        def putAll(self, controls, silent=False, params=None, timeout=None):
            return ClientSide.call("DynamicForm.put", controls, silent, params, timout)

        def put(self, silent=False, params=None, timeout=None):
            return ClientSide.call("DynamicForm.put", self, silent, params, timeout)

        def delteAll(self, controls, silent=False, params=None, timeout=None):
            return ClientSide.call("DynamicForm.get", controls, silent, params, timout)

        def delete(self, silent=False, params=None, timeout=None):
            return ClientSide.call("DynamicForm.delete", self, silent, params, timeout)

    class Loading(Center):
        """
            Defines how the element will look like while an AJAX call is being performed (unless silent loading is used)
            NOTE: you can override this whole class to modify the appearance - just replace with a different WebElement
        """
        def __init__(self, id, name, parent, **kwargs):
            Center.__init__(self, id, name, parent, **kwargs)
            self.addClass("WLoading")

            layout = self.addChildElement(Horizontal())
            layout.addClass("WContent")
            layout.addChildElement(Image(src="images/throbber.gif"))
            label = layout.addChildElement(Label())
            label.setText(self.parent.loadingText())

    def __init__(self, id=None, name=None, parent=None, parentHandler=None, initScripts=None, **kwargs):
        if parentHandler:
            self.elementFactory = parentHandler.elementFactory

        RequestHandler.__init__(self, parentHandler=parentHandler, initScripts=initScripts)
        WebElement.__init__(self, id=id or self.accessor, name=name, parent=None, **kwargs)
        self.attributes['handler'] = self.accessor

        if not self._loading:
            loading = self.Loading(self.id + ":Loading", self.name + ":Loading", parent=self)
            loading.hide()
            self.__class__._loading = loading.toHtml()

        self.initScripts.append(self.setScriptContainer(ScriptContainer()).content())

    def loadingText(self):
        """
            Defines the default text to display while this controller is loading
        """
        return "Loading %s..." % (str(self), )

    def toHtml(self, formatted=False, *args, **kwargs):
        """
            Override toHtml to draw loading section in addition to controller placement
        """
        return "".join([self._loading, WebElement.toHtml(self, formatted, *args, **kwargs)])

    def buildElement(self, className, id=None, name=None, parent=None, properties=None, scriptContainer=None):
        """
            Builds a WebElement using the factory attached to this controller
        """
        element = self.elementFactory.build(className, id, name, parent)
        if scriptContainer != None:
            element.setScriptContainer(scriptContainer)
        if properties:
            element.setProperties(properties)

        return element

    def content(self, formatted=False, request=None, *args, **kwargs):
        """
            Overrides the WebElement content to include an initial response if autoLoad is set to true
        """
        request = request or HTTP.Request()
        if self.autoLoad == "AJAX":
            request.response.scripts.addScript("DynamicForm.get('%s');" % self.fullId())
        elif self.autoLoad is True:
            return self.renderResponse(request)

        return ""

    def __str__(self):
        """
            Use the RequestHandler str implementation
        """
        return RequestHandler.__str__(self)


class ElementControl(PageControl):
    """
        Defines a PageControl that is rendered using WebElements
    """
    def buildUI(self, request):
        return Empty()

    def initUI(self, ui, request):
        return

    def setUIData(self, ui, request):
        return

    def renderResponse(self, request):
        ui = self.buildUI(request)
        self.initUI(ui, request)
        self.setUIData(ui, request)
        if not request.response.scripts:
            request.response.scripts = ScriptContainer()
            ui.setScriptContainer(request.response.scripts)
            return ui.toHtml(request=request) + request.response.scripts.toHtml(request=request)
        else:
            ui.setScriptContainer(request.response.scripts)
            return ui.toHtml(request=request)


class TemplateControl(ElementControl):
    """
        Defines an ElementControl that is rendered from a WUI Template
        NOTE: When subclassing set the template attribute - aka template = UITemplate.fromFile("myFile.wui")
    """
    template = UITemplate.Template("empty")

    def buildUI(self, request):
        return TemplateElement(template=self.template, factory=self.elementFactory)
