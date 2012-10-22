"""
    Tests that the main DynamicForm object reacts as expected
"""

from DynamicForm.DynamicForm import DynamicForm
from DynamicForm import HTTP


blankRequest = HTTP.Request()

class TestDynamicForm(object):
    """
        Tests all publicly accessible methods of the DynamicForm object
    """
    testForm = DynamicForm()

    def test_create(self):
        assert(type(self.testForm) == DynamicForm)

    def test_modifyDocument(self):
        class FakeDynamicForm(DynamicForm):
            def modifyDocument(self, document, response):
                document.setProperty('title', "Heyyyy!")
        fake = FakeDynamicForm()
        assert "Heyyyy!" in fake.renderResponse(blankRequest)

    def test_title(self):
        assert self.testForm.title(blankRequest) == "DynamicForm"
        assert self.testForm.title(blankRequest) in self.testForm.renderResponse(blankRequest)

    def test_favicon(self):
        assert self.testForm.favicon(blankRequest) == "images/favicon.png"
        assert self.testForm.favicon(blankRequest) in self.testForm.renderResponse(blankRequest)

    def test_resourceFiles(self):
        assert self.testForm.resourceFiles(blankRequest) == ['javascript/CommonJavascript.js',
                                                             'stylesheets/CommonStyleSheet.css']
        for resource in self.testForm.resourceFiles(blankRequest):
            assert resource in self.testForm.renderResponse(blankRequest)

    def test_renderResponse(self):
        assert "DOCTYPE" in self.testForm.renderResponse(blankRequest)
