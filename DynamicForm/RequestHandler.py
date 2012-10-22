"""
    Defines the basic concept of a request handler
"""

import types
import json

import HTTP

class RequestHandler(object):
    """
        Defines the base request handler that supports responding itself or allowing one of its child classes to
        respond
    """
    grabFields = () # fields not part of this controller which will be passed in when this controller is requested
    grabForms = () # forms not part of this controller which will be passed in when this controller is requested
    sharedFields = ()  # fields that are part of this controller & will be passed into all childHandlers when requested
    sharedForms = () # forms that are part of this controller  & will be passed into all childHandlers when requested

    def __init__(self, parentHandler=None, initScripts=None):
        self.parentHandler = parentHandler
        self.baseName = self.__class__.__name__[0].lower() + self.__class__.__name__[1:]
        self.accessor = self.baseName
        self.childHandlers = {}
        self.initScripts = initScripts or []

        grabFields = self.grabFields
        grabForms = self.grabForms
        if parentHandler:
            self.accessor = self.parentHandler.accessor + "." + self.accessor
            self.grabFields = set(self.grabFields).union(parentHandler.sharedFields)
            self.grabForms = set(self.grabForms).union(parentHandler.sharedForms)
            self.sharedFields = set(self.sharedFields).union(parentHandler.sharedFields)
            self.sharedForms = set(self.sharedFields).union(parentHandler.sharedFields)

        self.initScripts.append("DynamicForm.handlers['%s'] = {};" % self.accessor)
        self.initScripts.append("DynamicForm.handlers['%s'].grabFields = %s;" %
                                (self.accessor, json.dumps(list(self.grabFields))))
        self.initScripts.append("DynamicForm.handlers['%s'].grabForms = %s;" %
                                (self.accessor, json.dumps(list(self.grabForms))))

        self._registerChildren()

        if not parentHandler:
            for handler in self.allHandlers():
                handler.makeConnections()

    def __str__(self):
        return " ".join([string[0].upper() + string[1:] for string in self.accessor.split(".")])

    def _registerChildren(self):
        for attribute in (getattr(self, attribute, None) for attribute in dir(self) if attribute not in ('__class__',)):
            if type(attribute) == type and \
               issubclass(attribute, RequestHandler) and not attribute.__name__.startswith("Abstract"):
                instance = attribute(parentHandler=self, initScripts=self.initScripts)
                self.childHandlers[instance.baseName] = instance
                self.__setattr__(instance.baseName, instance)

    @classmethod
    def djangoView(cls):
        """
            Creates a django view form the request handler object
        """
        return cls().handleDjangoRequest

    def handleDjangoRequest(self, request):
        """
            Handles a django request - returning a django response
        """
        return self.handleRequest(HTTP.Request.fromDjangoRequest(request)).toDjangoResponse()

    def handleRequest(self, request, handlers=None):
        """
            handles a single request returning a response object
        """
        if not handlers:
            handlers = request.fields.get('requestHandler', '')
            if type(handlers) in (list, set, tuple):
                result = [self.handleRequest(request.copy(), handler.split(".")).serialize() for handler in handlers]
                request.response.status = HTTP.Response.Status.MULTI_STATUS
                request.response.contentType = HTTP.Response.ContentType.JSON
                request.response.content = json.dumps(result)
                return request.response

            handlers = handlers.split(".")

        if not handlers.pop(0) in (self.baseName, ""): # Ensure the handler is either the current handler or not spec.
            request.response.status = HTTP.Response.Status.NOT_FOUND
            request.response.content = self.renderNotFound(request, request.fields.get('requestHandler', ''))
        elif handlers:
            handler = self.childHandlers.get(handlers[0], None)
            if not handler:
                request.response.status = HTTP.Response.Status.NOT_FOUND
                request.response.content = self.renderNotFound(request, request.fields.get('requestHandler', ''))
            return handler.handleRequest(request, handlers)
        else:
            try:
                request.response.content = self.renderResponse(request)
            except Exception, e:
                request.response.status = HTTP.Response.Status.INTERNAL_SERVER_ERROR
                request.response.content = self.renderInternalError(request, e)

        return request.response

    def allHandlers(self, handlerList=None):
        """
            Returns itself and all child handlers
        """
        if handlerList is None:
            handlerList = []

        handlerList.append(self)
        for child in self.childHandlers.values():
            child.allHandlers(handlerList)
        return handlerList

    def makeConnections(self):
        """
            A safe post instantiation place to make connections between child handlers
        """
        pass

    def renderResponse(self, request):
        """
            Defines the response given by the handler (should be overridden by concrete handlers)
        """
        return ""

    def renderNotFound(self, request, resource):
        """
            Defines the response given when a handler is not found (should be overridden by concrete handlers)
        """
        return "Error: %s was not found." % resource

    def renderInternalError(self, request, exception):
        """
            Defines the response when an exception is thrown during handling (should be overridden by concrete handlers)
        """
        return "Internal Server Error: " + str(exception)

