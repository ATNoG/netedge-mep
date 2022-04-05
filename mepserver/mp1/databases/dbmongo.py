from .database_base import DatabaseBase
from ..utils import mongodb_query_replace,NestedEncoder
from pymongo import MongoClient
from typing import Union
import cherrypy
import json

class MongoDb(DatabaseBase):
    def __init__(self,ip,port,database):
        self.ip = ip
        self.port = port
        self.database = database
        self.client = None

    def connect(self,thread_index):
        # Create database connection
        self.client = MongoClient(self.ip,self.port)[self.database]
        # Add database to each thread (https://github.com/cherrypy/tools/blob/master/Databases)
        cherrypy.thread_data.db = self

    def disconnect(self):
        # Disconnects from the database
        self.client.close()

    def create(self,col: str, indata: dict):
        """
        Add a new entry at database
        :param col: collection
        :param indata: content to be added
        :return: database id of the inserted element.
        """

        # Get the collection
        collection = self.client[col]
        data = collection.insert_one(indata)
        return data.inserted_id

    def remove(self, col:str, query: dict):
        """
        Remove a document from the database
        :param col: collection
        :param query: query to match one or more parameters of the data to be removed
        :return: document removed from database
        """
        # Get the collection
        collection = self.client[col]
        data_to_be_removed = collection.delete_one(query)
        return data_to_be_removed

    def query_col(self, col:str, query: Union[dict,object,str], fields=None, find_one = False):
        """
        For a given collection return the results that match the query
        :param col: collection to be queried
        :type col: str
        :param query: query to match one or more parameters of the data to queried
        :type query: Either a predefined query in dict format, a json serializable class or a str
        :param fields: fields to be obtained (according to the mongodb documentation)
        :type fields: dict
        :return: document removed from database
        """
        # Get the collection
        if fields is None:
            fields = {}

        collection = self.client[col]
        # Verify if query is a string or  dict/object
        if isinstance(query,str):
            query = json.loads(query)
        else:
            # Dump the object to a string and then reload it as a dict (this deals with the nested objects)
            # This way it works for both Object with objects and Dicts with objects
            query = json.loads(json.dumps(query,cls=NestedEncoder))
        # Removes the default values None to a wildcard query match in order to properly query mongodb
        # the wildcard is {$exists:true}
        # Adds $in operator if the query contains a list
        query = mongodb_query_replace(query)
        # Query the collection according to query and obtain the fields specified in fields
        if find_one:
            data = collection.find_one(query,{"_id":0}|fields)
        else:
            data = collection.find(query,{"_id":0}|fields)
        return data

    def count_documents(self,col:str,query:dict):
        """
        For a given collection return the results that match the query
        :param col: collection
        :param query: query to match one or more parameters of the data to queried
        :return: number of documents that match the query
        """
        # Get the collection
        collection = self.client[col]
        return collection.count_documents(query)