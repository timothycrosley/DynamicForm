'''
    test_RequestHandler.py

    Tests the base RequestHandler logic

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

from DynamicForm import HTTP
from DynamicForm.RequestHandler import RequestHandler

class Frame(RequestHandler):
    sharedFields = ["field2"]
    sharedForms = ["form2"]
    grabFields = ["field1"]
    grabForms = ["form1"]

    def renderResponse(self, trip):
        return '<html><body><div id="frame.content"></div></body></html>'

    class Content(RequestHandler):
        grabFields = ["field3"]
        grabForms = ["form3"]

        def renderResponse(self, trip):
            return "<data></data>"

    class ExceptionThrower(RequestHandler):

        def renderResponse(self, trip):
            raise ValueError("Error")

        def makeConnections(self):
            self.makeConnectionsWasCalled = True

class TestRequestHandler(object):
    """
        Tests all public methods on the RequestHandler class
    """
    testFrame = Frame()

    def test_create(self):
        assert type(self.testFrame) == Frame
        assert isinstance(self.testFrame, RequestHandler)

        assert len(self.testFrame.childHandlers) == 2
        assert self.testFrame.childHandlers['content'] == self.testFrame.content
        assert self.testFrame.childHandlers['exceptionThrower'] == self.testFrame.exceptionThrower
        assert len(self.testFrame.content.childHandlers) == 0
        assert len(self.testFrame.exceptionThrower.childHandlers) == 0

        assert self.testFrame.grabFields == ["field1"]
        assert self.testFrame.grabForms == ["form1"]
        assert self.testFrame.sharedFields == ["field2"]
        assert self.testFrame.sharedForms == ["form2"]

        assert self.testFrame.content.grabFields == set(["field2", "field3"])
        assert self.testFrame.content.grabForms == set(["form2", "form3"])

        assert self.testFrame.exceptionThrower.grabFields == set(["field2"])
        assert self.testFrame.exceptionThrower.grabForms == set(["form2"])

    def test_handleRequest(self):
        blankResponse = self.testFrame.handleRequest(HTTP.Request({'requestHandler':''}))
        assert blankResponse.content == '<html><body><div id="frame.content"></div></body></html>'
        assert blankResponse.status == HTTP.Response.Status.OK

        frameResponse = self.testFrame.handleRequest(HTTP.Request({'requestHandler':'frame'}))
        assert frameResponse.content == '<html><body><div id="frame.content"></div></body></html>'
        assert frameResponse.status == HTTP.Response.Status.OK

        contentResponse = self.testFrame.handleRequest(HTTP.Request({'requestHandler':'frame.content'}))
        assert contentResponse.content == '<data></data>'
        assert contentResponse.status == HTTP.Response.Status.OK

        contentResponse = self.testFrame.handleRequest(HTTP.Request({'requestHandler':'frame.exceptionThrower'}))
        assert contentResponse.content.startswith('Internal Server Error: Error')
        assert contentResponse.status == HTTP.Response.Status.INTERNAL_SERVER_ERROR

        badHandlerResponse = self.testFrame.handleRequest(HTTP.Request({'requestHandler':'nonExistent'}))
        assert badHandlerResponse.content == 'Error: nonExistent was not found.'
        assert badHandlerResponse.status == HTTP.Response.Status.NOT_FOUND

    def test_renderResponse(self):
        frameRequest = HTTP.Request()
        assert self.testFrame.renderResponse(frameRequest) == '<html><body><div id="frame.content"></div></body></html>'
        assert frameRequest.response.status == HTTP.Response.Status.OK

        contentRequest = HTTP.Request()
        assert self.testFrame.content.renderResponse(contentRequest)
        assert contentRequest.response.status == HTTP.Response.Status.OK

    def test_allHandlers(self):
        assert self.testFrame.allHandlers() == [self.testFrame, self.testFrame.content, self.testFrame.exceptionThrower]

    def test_makeConnections(self):
        assert self.testFrame.exceptionThrower.makeConnectionsWasCalled == True

    def test_str(self):
        assert str(self.testFrame) == "Frame"
        assert str(self.testFrame.content) == "Frame Content"
        assert str(self.testFrame.exceptionThrower) == "Frame ExceptionThrower"
