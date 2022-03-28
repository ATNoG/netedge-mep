import enum
from json import JSONEncoder
import json
from enum import Enum

import cherrypy
import validators
from validators import ValidationFailure
from typing import List


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
