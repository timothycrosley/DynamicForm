'''
    test_DynamicForm.py

    Tests that the main DynamicForm object reacts as expected

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
        assert self.testForm.resourceFiles == ('js/WebBot.js', 'stylesheets/Site.css')
        for resource in self.testForm.resourceFiles:
            assert resource in self.testForm.renderResponse(blankRequest)

    def test_renderResponse(self):
        assert "DOCTYPE" in self.testForm.renderResponse(blankRequest)
