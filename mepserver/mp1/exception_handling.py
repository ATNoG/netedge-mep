import functools

from .models import ProblemDetails
from jsonschema import ValidationError
from cherrypy._cperror import NotFound
from .utils import NestedEncoder,json_out
import cherrypy
import re

def exception_handling(default_status=200):
    """
    Decorator to be used for exception handling and setting return HTTP Status Code
    Error 404 is dealt in the CherryPy config (by calling the function http_404_handling due to it not even reaching our function

    Only returns the first error - If user has multiple errors it will need to attempt various times

    :param default_status: Default Status Code if nothing wrong happens
    :return: Return of the called function
    """
    # TODO VALIDATE THAT ALL CONDITIONS ARE VALIDATED HERE
    # TODO not quite sure if this is what they want for instance
    # Instance "A URI reference that identifies the specific occurrence of the problem"
    def wrapper(func):
        """
        Func is the func to be called
        """
        @functools.wraps(func)
        def inner_function(*args,**kwargs):
            cherrypy.response.headers["Content-Type"] = "application/json"
            cherrypy.response.status = default_status
            try:
                return func(*args,**kwargs)
            except ValidationError as e:
                # Error thus we set status to 400
                cherrypy.response.status = 400
                # Based on the JSONSchema Error obtain the error
                # JSONSchema object has various properties but sometimes it shows various properties not specifying which
                # was improperly validated but it shows what is wrong in the message
                # Example: Additional properties are not allowed ('ola' was unexpected)
                # Thus, we can use this message to obtain the values we want and transform them into a ProblemDetails obj
                query_url = cherrypy.url(qs=cherrypy.request.query_string, relative='server')
                if e.validator == "additionalProperties":
                    property = re.search("'(.+?)'",e.message).group(1)
                    problemDetails = ProblemDetails(title="Invalid property",
                                                    status=400,
                                                    detail=f"The property {property} is not a valid property",
                                                    instance=f"The query URI instance was {query_url}")
                elif e.validator == "type":
                    property =  e.relative_path.pop()
                    type = e.validator_value
                    problemDetails = ProblemDetails(title="Invalid Type",
                                                    status=400,
                                                    detail=f"The property {property} should be of type {type}",
                                                    instance=f"The query URI instance was {query_url}")
                elif e.validator == "enum":
                    property = e.relative_path.pop()
                    type = e.validator_value
                    problemDetails = ProblemDetails(title="Invalid Type",
                                                    status=400,
                                                    detail=f"The property {property} should be one of: {','.join(type)}",
                                                    instance=f"The query URI instance was {query_url}")
                elif e.validator == "required":
                    property = re.search("'(.+?)'", e.message).group(1)
                    problemDetails = ProblemDetails(title="Missing required property",
                                                    status=400,
                                                    detail=f"The {property} property is a required property",
                                                    instance=f"The query URI instance was {query_url}")
                return problemDetails
                # TODO AUTH VALIDATION
        return inner_function
    return wrapper

@json_out(cls=NestedEncoder)
def http_404_handling(status,message,traceback,version):
    """
    Function to deal with the CherryPy thrown error when an invalid path/method is provided
    """
    cherrypy.response.headers["Content-Type"] = "application/json"
    method = cherrypy.request.method
    query_url = cherrypy.url(qs=cherrypy.request.query_string, relative='server')
    # TODO add type  - IETF RFC 3986
    problemDetails = ProblemDetails(title="Invalid Path",
                                    status=404,
                                    detail=f"The method {method} is not valid for the specified query url.",
                                    instance=f"The query URI instance was {query_url}")
    return problemDetails