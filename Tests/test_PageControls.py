'''
    test_PageControls.py

    Tests that the base PageControls function as expected

    Copyright (C) 2013  Timothy Edmund Crosley

    This program is free software; you can redistribute it and/or
    modify it under the terms of the GNU General Public License
    as published by the Free Software Foundation; either version 2
    of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
'''

from WebElements.Base import WebElement
from WebElements.Display import Label
from WebElements import UITemplate
from DynamicForm import HTTP
from DynamicForm.RequestHandler import RequestHandler
from DynamicForm import PageControls


class TestControl(PageControls.PageControl):
    def renderResponse(self, request):
        return "Heyyyy!"


class BasicElementControl(PageControls.ElementControl):
    def buildUI(self, request):
        return self.buildElement("label", properties={'text':'This is a label'})


class BasicTemplateControl(PageControls.TemplateControl):
    template = UITemplate.fromSHPAML("> label@label text=TemplateLabel")


class TestPageControl(object):
    """
        Tests all publicly accessible functions of the base page control object
    """
    testControl = TestControl()

    def test_create(self):
        assert self.testControl.name == "testControl"
        assert self.testControl.id == "testControl"
        assert isinstance(self.testControl, WebElement)
        assert isinstance(self.testControl, RequestHandler)
        assert "testControl:Loading" in self.testControl._loading
        assert self.testControl.loadingText() in self.testControl._loading

    def test_toHTML(self):
        assert self.testControl.content() in self.testControl.toHTML()
        assert self.testControl._loading in self.testControl.toHTML()

    def test_content(self):
        assert "Heyyyy!" in self.testControl.content()

        class TestControlNoAutoLoad(TestControl):
            autoLoad = False
        testNoAutoLoad = TestControlNoAutoLoad()

        assert not "Heyyyy!" in testNoAutoLoad.content()

    def test_buildElement(self):
        testElement = self.testControl.buildElement("label", "myLabel", properties={'text':'labelText'})
        assert type(testElement) == Label
        assert testElement.id == "myLabel"
        assert testElement.name == "myLabel"
        assert testElement.text() == "labelText"


class TestElementControl(object):
    """
        Tests all publicly accessible functions of the base element control object
    """
    testControl = BasicElementControl()

    def test_create(self):
        assert self.testControl.name == "basicElementControl"
        assert isinstance(self.testControl, WebElement)
        assert isinstance(self.testControl, RequestHandler)

    def test_buildUI(self):
        assert type(self.testControl.buildUI(HTTP.Request())) == Label
        assert self.testControl.buildUI(HTTP.Request()).toHTML() in self.testControl.renderResponse(HTTP.Request())

    def test_initUI(self):
        class MyElementControl(BasicElementControl):
            def initUI(self, ui, request):
                ui += self.buildElement("label", properties={'text':'New Text'})

        myElementControl = MyElementControl()
        response = myElementControl.renderResponse(HTTP.Request())
        assert "New Text" in response
        assert "This is a label" in response

    def test_setUIData(self):
        class MyElementControl(BasicElementControl):
            def setUIData(self, ui, request):
                ui.setText("New Text")

        myElementControl = MyElementControl()
        response = myElementControl.renderResponse(HTTP.Request())
        assert "New Text" in response
        assert not "This is a label" in response


class TestTemplateControl(object):
    """
        Tests all publicly accessible functions of the base template control object
    """
    testControl = BasicTemplateControl()

    def test_create(self):
        assert self.testControl.name == "basicTemplateControl"
        assert isinstance(self.testControl, WebElement)
        assert isinstance(self.testControl, RequestHandler)

    def test_buildUI(self):
        ui = self.testControl.buildUI(HTTP.Request())
        assert isinstance(ui.label, Label)
        assert ui.label.text() == "TemplateLabel"
        assert ui.toHTML() in self.testControl.renderResponse(HTTP.Request())


