import enum
from json import JSONEncoder
import json
from enum import Enum
from .mep_exceptions import *
import cherrypy
import validators
from validators import ValidationFailure
from typing import List

from abc import ABC, abstractmethod

def validate_uri(href: str) -> str:
    valid_href = validators.url(href)
    if isinstance(valid_href, ValidationFailure):
        raise TypeError
    return href


def pick_identifier(data: dict, possible_identifiers: List[str]) -> str:
    """
    From the three possible identifiers picks the first it finds in the post value

    :param possible_identifiers: List of possible identifiers
    :type possible_identifiers: List[String]
    :return: Picked Identifier
    :rtype: String

    Mutable List as default parameter warning can be ignored since it is only used internally and never altered

    Raises InvalidIdentifier if no identifier is specified
    """
    available_data_keys = list(data.keys())
    for identifier in possible_identifiers:
        if identifier in available_data_keys:
            return identifier


def ignore_none_value(data: dict) -> dict:
    """
    Removes keys that have None value from the dictionary

    :param data: Dictionary containing data to be returned
    :type data: dict
    :return: Initial Dictionary but without keys that have None value
    :rtype: dict
    """
    return {key: val for key, val in data.items() if val is not None}


# Decorator that receives a CLS to encode the json
def json_out(cls):
    def json_out_wrapper(func):
        def inner(*args, **kwargs):
            object_to_be_serialized = func(*args, **kwargs)
            cherrypy.response.headers["Content-Type"] = "application/json"
            return json.dumps(object_to_be_serialized, cls=cls).encode("utf-8")
        return inner
    return json_out_wrapper

class NestedEncoder(JSONEncoder):
    def default(self, obj):
        # If it is a class we created and is having trouble using json_dumps use our to_json class
        if hasattr(obj, "to_json"):
            return obj.to_json()
        # If it is a subclass of Enum just call the name value
        elif isinstance(obj, Enum):
            return obj.name
        else:
            return json.JSONEncoder.default(self, obj)

class UrlQueryValidator(ABC):

    @staticmethod
    @abstractmethod
    def get_required_fields():
        """
        function used by validate to obtain the required fields
        a function is used instead of a parameter inside the validate function (i.e validate(**kwargs,required_fields=[a,b])
        due to python only validating the function defaults on function definition
        having mutable default arguments can lead to improper usage thus by defining the usage of the UrlQueryValidator
        in this manner we "guide" the programmer to use the classes and methods properly
        """
        pass

    @staticmethod
    @abstractmethod
    def validate(**kwargs):
        """
        function that validates the arguments passed in an urlquery according to mec 011
        """
        pass

class ServicesQueryValidator(UrlQueryValidator):

    @staticmethod
    def validate(**kwargs):
        return True

    @staticmethod
    def get_required_fields():
        pass

def url_query_validator(cls):
    def inner_wrapper(func):
        def inner(*args,**kwargs):
            # Args is the class (self arg)
            # Kwargs are the actual function arguments that come after the self

            # Check if the cls is a subclass of the abstract class QueryValidator
            # This forces any new interface using the query_validator
            if issubclass(cls,UrlQueryValidator):
                if cls.validate(**kwargs):
                    return func(*args, **kwargs)
                raise InvalidQuery("Class needs to be subclass of UrlQueryValidator")
            raise TypeError
        return inner
    return inner_wrapper

def object_to_mongodb_dict(obj)->dict:
    """
    Takes any object and transforms it into a mongodb acceptable record

    This process may seem weird due to the fact that we are dumping and then loading
    The thought process is that we have classes that naturally give guarantees in terms of object structure and
    validation, but this comes with the drawback that we don't have a dict to send to mongodb
    For this process we use our existing NestedEncoder that properly generates a json string and then load said string,
    allowing us to have a validated python dictionary that is a 1 to 1 representation of the underlying class
    """
    return json.loads(json.dumps(obj,cls=NestedEncoder))