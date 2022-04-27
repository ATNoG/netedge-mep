# Copyright 2022 Instituto de Telecomunicações - Aveiro
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
import functools
from json import JSONEncoder
import json
from enum import Enum
from .mep_exceptions import *
import cherrypy
import validators
from validators import ValidationFailure
from typing import List
import argparse
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
    Removes keys that have None or empty dict value from the dictionary

    :param data: Dictionary containing data to be returned
    :type data: dict
    :return: Initial Dictionary but without keys that have None value
    :rtype: dict
    """
    return {key: val for key, val in data.items() if val is not None}

def mongodb_query_replace(query:dict)->dict:
    """
    Replaces the None values (i.e default values) of Url Query Parameters to wildcard mongodb query
    This allows for easy and queries in the mongodb database
    Due to nested queries we need to user dot notation and that implies playing with strings
    Replaces list parameters with the $in operator
    Works for any type of json document (i.e various layers of nested documents)

    Yes, this may seem overkill if we think in terms of mongodb, but since this is used by various types of queries,
    where we don't actually know if the value is going to be None or not it's easier to parse it like this instead of
    validating each and every type of class and then only sending the ones needed to the query
    """
    new_query = {}
    for key,value in query.items():
        if isinstance(value, dict):
            new_dict = mongodb_query_replace(value)
            # example: {"serCategory:{"id":"uuid"}}
            # query must be find({"serCategory.id":"uuid"})
            for new_key,value in new_dict.items():
                # Exists is an operator that is used inside a new dict but shouldn't be appended
                if new_key == "$exists":
                    new_query[key] = {new_key:value}
                else:
                    new_query[f"{key}.{new_key}"] = value
        # the operator $or and $and use a list as value that shouldn't be transformed into the $in operator
        # Maintain the list property but re-check the inner json
        elif key=="$or" or key=="$and":
            new_query[key] = [mongodb_query_replace(val) for val in value]
        elif isinstance(value,list):
            new_query[key] = {"$in":value}
        elif value is None:
            new_query[key] = {'$regex': '.*', '$options': 's'}
        else:
            new_query[key] = value
    return new_query

# Decorator that receives a CLS to encode the json
def json_out(cls):
    def json_out_wrapper(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            object_to_be_serialized = func(*args, **kwargs)
            cherrypy.response.headers["Content-Type"] = "application/json"
            return json.dumps(object_to_be_serialized, cls=cls).encode("utf-8")
        return inner
    return json_out_wrapper

class NestedEncoder(JSONEncoder):
    def default(self, obj):
        # If it is a class we created and it is having trouble using json_dumps use our to_json class
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
        """
        appInstanceId: List[str]
        ser_instance_id: List[str]
        ser_name: List[str]
        ser_category_id: List[str]
        consumed_local_only: bool
        is_local: bool
        scope_of_locality: str
        """
        # Used for scope_of_locality and is_local to transform the url query data to actual python values
        # if there is no value for the query we will query for both of the possible boolean values
        bool_converter = {"true":True,"false":False,None:[True,False]}

        ser_category_id = kwargs.get("ser_category_id")
        ser_instance_id = kwargs.get("ser_instance_id")
        ser_name = kwargs.get("ser_name")
        # If 2 are none means only one is set and thus the mutual exclusive attribute is valid so we can move on
        # with the validation
        # If there are 3 it means there wasn't any query parameter
        mutual_exclusive = {"ser_category_id": ser_category_id, "ser_instance_id": ser_instance_id, "ser_name": ser_name}
        if list(mutual_exclusive.values()).count(None) >= 2:
            # Get the parameter that isn't None
            mutually_exclusive_param = [key for key in mutual_exclusive if mutual_exclusive[key] is not None]
            # If no parameter is None it means there wasn't any mutually exclusive parameter thus no need to split
            if len(mutually_exclusive_param) > 0:
                # Parameter is a List of string so we want to split it in order to query in the next phase
                kwargs[mutually_exclusive_param[0]] = kwargs[mutually_exclusive_param[0]].split(",")
            # Validate the rest of the parameters against their supposed values
            consumed_local_only = kwargs.get("consumed_local_only")
            is_local = kwargs.get("is_local")
            scope_of_locality = kwargs.get("scope_of_locality")
            if consumed_local_only == "true" or "false" or None:
                kwargs["consumed_local_only"] = bool_converter[consumed_local_only]
                if is_local == "true" or "false" or None:
                    kwargs["is_local"] = bool_converter[is_local]
                    if (scope_of_locality is not None and not scope_of_locality.isdigit()) or scope_of_locality is None:
                        return kwargs
        raise InvalidQuery


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
                new_kwargs = cls.validate(**kwargs)
                return func(*args, **new_kwargs)
            raise TypeError
        return inner
    return inner_wrapper

def object_to_mongodb_dict(obj, extra: dict = None)->dict:
    """
    :param obj: Data to be transformed from python class to json
    :type obj: Python Class

    :param extra: Extra data to be added to mongo (i.e appinstanceid or another parameter to allow mapping)
    :type dict:

    Takes any object and transforms it into a mongodb acceptable record

    This process may seem weird due to the fact that we are dumping and then loading
    The thought process is that we have classes that naturally give guarantees in terms of object structure and
    validation, but this comes with the drawback that we don't have a dict to send to mongodb
    For this process we use our existing NestedEncoder that properly generates a json string and then load said string,
    allowing us to have a validated python dictionary that is a 1 to 1 representation of the underlying class

    Usage needs to thought since we can be overwriting or inserting improper data
    """

    # Append the extra dict to the data before sending it to mongodb
    return_data = json.loads(json.dumps(obj, cls=NestedEncoder))
    if extra is not None:
        return_data = return_data | extra
    return return_data


def check_port(port, base=1024):
    """
    Check if an int port number is valid
    Valid is bigger than base port number

    :param port: Port number
    :type port: integer
    :param base: Base port number (i.e lower limit)
    :type base: integer
    """
    value = int(port)
    if value <= base:
        raise argparse.ArgumentTypeError('%s is an invalid positive int value' % value)
    return value