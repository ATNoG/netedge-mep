from .database_base import DatabaseBase
from pymongo import MongoClient
import cherrypy
import time
from threading import Lock

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

    def query_col(self,col:str, query:dict):
        """
        For a given collection return the results that match the query
        :param col: collection
        :param query: query to match one or more parameters of the data to queried
        :return: document removed from database
        """
        pass

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