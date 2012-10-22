"""
    Tests the classes that make up the basic HTTP utilities (fields, request, response)
"""

from DynamicForm import HTTP


class TestCookie(object):
    """
        Tests all public instance methods of the Cookie object
    """
    def test_create(self):
        cookie = HTTP.Cookie("TestCookie", "TestValue", None, None, '/', None, False, False)
        assert type(cookie) == HTTP.Cookie
        assert cookie.key == "TestCookie"
        assert cookie.value == "TestValue"
        assert cookie.maxAge == None
        assert cookie.expires == None
        assert cookie.path == "/"
        assert cookie.domain == None
        assert cookie.secure == False
        assert cookie.httpOnly == False


class TestFieldDict(object):
    """
        Tests all public instance methods of the FieldDict object
    """
    testDict = HTTP.FieldDict({'string':'SOMETHING', 'nonUniqueList':["A", "B", "B"],
                               'uniqueList':["A", "B", "C"]})

    def test_create(self):
        basic = HTTP.FieldDict()
        assert type(basic) == HTTP.FieldDict
        assert isinstance(basic, dict)

    def test_get(self):
        assert self.testDict.get('string') == "SOMETHING"
        assert self.testDict.get('notSet') == ""
        assert self.testDict.get('nonUniqueList') == ["A", "B", "B"]
        assert self.testDict.get('uniqueList') == ["A", "B", "C"]

    def test_getSet(self):
        assert self.testDict.getSet('string') == set(["SOMETHING"])
        assert self.testDict.getSet('notSet') == set([])
        assert self.testDict.getSet('nonUniqueList') == set(["A", "B"])
        assert self.testDict.getSet('uniqueList') == set(["A", "B", "C"])

    def test_getList(self):
        assert self.testDict.getList('string') == ["SOMETHING"]
        assert self.testDict.getList('notSet') == []
        assert self.testDict.getList('nonUniqueList') == ["A", "B", "B"]
        assert self.testDict.getList('uniqueList') == ["A", "B", "C"]

    def test_first(self):
        assert self.testDict.first('string') == "SOMETHING"
        assert self.testDict.first('notSet') == ""
        assert self.testDict.first('nonUniqueList') == "A"
        assert self.testDict.first('uniqueList') == "A"

    def test_last(self):
        assert self.testDict.last('string') == "SOMETHING"
        assert self.testDict.last('notSet') == ""
        assert self.testDict.last('nonUniqueList') == "B"
        assert self.testDict.last('uniqueList') == "C"

    def test_subset(self):
        subset = self.testDict.subset(['nonUniqueList', 'uniqueList'])
        assert subset.keys() == ['nonUniqueList', 'uniqueList']
        assert subset.get('string') == ""
        assert subset.get('notSet') == ""
        assert subset.get('nonUniqueList') == ["A", "B", "B"]
        assert subset.get('uniqueList') == ["A", "B", "C"]

    def test_queryString(self):
        assert self.testDict.queryString() == ("nonUniqueList=A&nonUniqueList=B&nonUniqueList=B&string=SOMETHING&"
                                               "uniqueList=A&uniqueList=B&uniqueList=C")


class TestRequest(object):
    """
        Tests all public instance methods of the Request object
    """
    def test_create(self):
        basic = HTTP.Request()
        assert type(basic) == HTTP.Request
        assert type(basic.fields) == HTTP.FieldDict
        assert type(basic.meta) == HTTP.FieldDict
        assert type(basic.cookies) == HTTP.FieldDict
        assert type(basic.files) == HTTP.FieldDict
        assert type(basic.response) == HTTP.Response

    def test_isAjax(self):
        assert HTTP.Request().isAjax() == False
        assert HTTP.Request(meta={'HTTP_X_REQUESTED_WITH':'XMLHttpRequest'}).isAjax() == True

    def test_copy(self):
        firstRequest = HTTP.Request(fields={'field':'data'}, method="POST")
        secondRequest = firstRequest.copy()
        assert type(secondRequest) == type(firstRequest)
        assert firstRequest != secondRequest
        assert secondRequest.method == "POST"
        assert secondRequest.fields['field'] == "data"

        #assert making a change to the copy does not effect the original
        secondRequest.method = "GET"
        secondRequest.fields['field'] = "newData"
        assert secondRequest.method == "GET"
        assert secondRequest.fields['field'] == "newData"
        assert firstRequest.method == "POST"
        assert firstRequest.fields['field'] == "data"


class TestResponse(object):
    """
        Tests all public instance methods of the Response object
    """
    def test_create(self):
        testResponse = HTTP.Response()
        assert type(testResponse) == HTTP.Response
        assert testResponse.content == ""
        assert testResponse.contentType == HTTP.Response.ContentType.HTML
        assert testResponse.status == HTTP.Response.Status.OK

    def test_get(self):
        testResponse = HTTP.Response("MyResponse")
        testResponse['header'] = "value"
        assert testResponse['header'] == "value"
        assert testResponse.get('header') == "value"
        del testResponse['header']
        assert testResponse.get('header') == None
        assert testResponse.get('header', '') == ""

    def test_setCookie(self):
        testResponse = HTTP.Response("MyResponse")
        newCookie = testResponse.setCookie("myCookieName", "myCookieValue")
        assert len(testResponse.cookies) == 1
        assert testResponse.cookies["myCookieName"] == newCookie
        assert newCookie.key == "myCookieName"
        assert newCookie.value == "myCookieValue"

    def test_serialize(self):
        testResponse = HTTP.Response(content="'hey'", contentType=HTTP.Response.ContentType.JSON,
                                     status=HTTP.Response.Status.NON_AUTHORITAVE)
        assert testResponse.serialize() == {'responseText':"'hey'", 'contentType':HTTP.Response.ContentType.JSON,
                                            'status':HTTP.Response.Status.NON_AUTHORITAVE}

    def test_toDjangoResponse(self):
        class fakeDjangoResponse(HTTP.Response):
            def set_cookie(self, *args):
                self.setCookie(*args)

        testResponse = HTTP.Response("MyResponse")
        newCookie = testResponse.setCookie("myCookieName", "myCookieValue")
        testConvert = testResponse.toDjangoResponse(fakeDjangoResponse)
        assert type(testConvert) == fakeDjangoResponse
        assert len(testConvert.cookies) == 1
        assert testConvert.content == "MyResponse"
        assert testConvert.status == HTTP.Response.Status.OK
