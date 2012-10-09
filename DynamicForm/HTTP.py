"""
    Basic classes that define HTTP requests and responses
"""

from collections import namedtuple

Cookie = namedtuple('Cookie', ['key', 'value', 'maxAge', 'expires', 'path', 'domain', 'secure', 'httpOnly'])

class FieldDict(dict):
    """
        Adds convenience methods to the basic python dictionary specific to HTTP field dictionaries
    """

    def get(self, field, default=''):
        """
            Overwrites dict behavior to return empty string by default - to be more consistent with browser behavior
        """
        return self.get(field, default)

    def getSet(self, field):
        """
            Returns a set version of a value (independent to it's form in the dictionary)
        """
        field = self.get(field)
        if not field:
            return set([])
        if type(field) != list:
            return set([field])
        else:
            return set(field)

    def getList(self, field):
        """
            Returns a list version of a value (independent to it's form in the dictionary)
        """
        field = self.get(field)
        if not field:
            return []
        if type(field) != list:
            return [field]
        else:
            return field

    def first(self, fieldName, defaultValue=''):
        """
            Returns the first item if the value is a list otherwise returns the whole value
        """
        field = self.get(fieldName, defaultValue)
        if type(field) == list:
            if field:
                return field[0]
            return defaultValue
        return field

    def last(self, fieldName, defaultValue=''):
        """
            Returns the last item if the value is a list otherwise returns the whole value
        """
        field = self.get(fieldName, defaultValue)
        if type(field) == list:
            if field:
                return field[-1]
            return defaultValue
        return field

    def subset(self, fields, default=''):
        """
            Returns a subset of itself based on a list of fields
        """
        fieldDict = self.__class__()
        for field in fields:
            fieldDict[field] = self.get(field, default)

        return fieldDict


class Request(object):
    """
        Defines the abstract concept of an HTTP request
    """
    __slots__ = ('fields', 'body', 'cookies', 'meta', 'files', 'path', 'method', 'data', 'native', 'user')

    def __init__(self, fields=None, body="", cookies=None, meta=None, files=None, path=None, method=None, user=None,
                 native=None):
        self.fields = FieldDict(fields) or FieldDict()
        self.body = body
        self.cookies = FieldDict(cookies) or FieldDict()
        self.meta = FieldDict(meta) or FieldDict()
        self.files = FieldDict(files) or FieldDict()
        self.path = path or ""
        self.user = user
        self.native = native

     def isAjax(self):
        """
            Returns true if the request is explicely flagged as using an XMLHttpRequest
        """
        return self.meta.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

    @classmethod
    def fromDjangoRequest(cls, djangoRequest):
        """
            Creates a new request object from a Django request object
        """
        fields = dict(djangoRequest.POST)
        fields.update(dict(djangoRequest.GET))
        return cls(fields, djangoRequest.body, djangoRequest.COOKIES, djangoRequest.META, djangoRequest.FILES,
                   djangoRequest.path, djangoRequest.method, djangoRequest)


class Response(object):
    """
        Defines the abstract concept of an HTTP response
    """
    __slots__ = ('content', 'status', 'contentType', '_headers', '_cookies')

    class Status(object):
        """
            A mapping of all HTTP response codes to their English meaning

            see: http://en.wikipedia.org/wiki/List_of_HTTP_status_codes
        """
        #Informational
        CONTINUE = 100
        SWITCHING_PROTOCOLS = 101
        PROCESSING = 102

        #Success
        OK = 200
        CREATED = 201
        ACCEPTED = 202
        NON_AUTHORITAVE = 203 #Information returned but might may not be owned by server
        NO_CONTENT = 204
        RESET_CONTENT = 205 #The requester made a reset response and it was successful
        PARTIAL_CONTENT = 206
        MULTI_STATUS = 207
        ALREADY_REPORTED = 208

        #Redirection
        MULTIPLE_CHOICES = 300
        MOVED = 301
        FOUND = 302
        SEE_OTHER = 303
        NOT_MODIFIED = 304
        USE_PROXY = 305
        TEMPORARY_REDIRECT = 307
        PERMANENT_REDIRECT = 308

        #Client error
        BAD_REQUEST = 400
        UNAUTHORIZED = 401
        PAYMENT_REQUIRED = 402
        FORBIDDEN = 403
        NOT_FOUND = 404
        NOT_ALLOWED = 405
        NOT_ACCEPTABLE = 406
        PROXY_AUTHENTICATION_REQUIRED = 407
        REQUEST_TIMEOUT = 408
        CONFLICT = 409
        GONE = 410
        LENGTH_REQUIRED = 411
        PRECONDITION_FAILED = 412
        REQUEST_ENTITY_TOO_LARGE = 413
        REQUEST_URI_TOO_LONG = 414
        UNSUPPORTED_MEDIA_TYPE = 415
        REQUESTED_RANGE_NOT_SATISFIABLE = 416
        EXPECTATION_FAILED = 417
        IM_A_TEAPOT = 418
        UNPROCESSABLE_ENTITY = 422
        LOCKED = 423
        FAILED_DEPENDENCY = 424
        METHOD_FAILURE = 424
        UNORDERED_COLLECTION = 425
        UPGRADE_REQUIRED = 426
        PRECONDITION_REQUIRED = 428
        TOO_MANY_REQUESTS = 429
        HEADER_FIELDS_TOO_LARGE = 431
        UNAVAILABLE_FOR_LEGAL_REASONS = 451

        #Server error
        INTERNAL_SERVER_ERROR = 500
        NOT_IMPLEMENTED = 501
        BAD_GATEWAY = 502
        SERVICE_UNAVAILABLE = 503
        GATEWAY_TIMEOUT = 504
        HTTP_VERSION_NOT_SUPPORTED = 505
        CIRCULAR_REFERENCE = 506
        INSUFFICIENT_STORAGE = 507
        INFINITE_LOOP = 508
        BANDWIDTH_LIMIT_EXCEEDED = 509
        NOT_EXTENDED = 510
        NETWORK_AUTHENTICATION_REQUIRED = 511

    def __init__(self, content='', contentType="text/html;charset=UTF-8", status=None, isDynamic=True):
        self.content = content
        self.contentType = contentType
        self.status = status or self.Status.OK
        self._headers = {}
        self._cookies = {}
        if isDynamic: #If content is dynamically generated (and it almost always is) don't let the browser cache
            self['Cache-Control'] = 'no-cache, must-revalidate'
            self['Pragma'] = 'no-cache'
            self['Expires'] = 'Thu, 01 DEC 1994 01:00:00 GMT' #Some time in the past

        def get(self, header, default=None):
            """
                Returns header value if it exists or default
            """
            return self._headers.get(header, default)

        def __setitem__(self, header, value):
            self._headers[header] = value

        def __delitem__(self, header):
            try:
                del self._headers[header]
            except KeyError:
                pass

        def __getitem__(self, header):
            return self._headers[header]

        def setCookie(self, key, value='', maxAge=None, expires=None, path='/', domain=None, secure=False,
                      httpOnly=False):
            """
                Sets a cookie
            """
            self._cookies[key] = Cookie(key, value, maxAge, expires, path, domain, secure, httpOnly)

        def toDjangoResponse(self, cls):
            """
                Converts the given response to the Django HTTPResponse object
                cls - the django HTTPResponse class or compatible object type
            """
            djangoResponse = cls(self.content, self.contentType, self.status)
            for header, value in self.iteritems():
                djangoResponse[header] = value

            for cookie in self._cookies.itervalues():
                djangoResponse.set_cookie(*cookie)

            return djangoResponse
