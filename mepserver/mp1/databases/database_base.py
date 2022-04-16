from abc import ABC, abstractmethod


class DatabaseBase(ABC):
    """
    Specification if at some point there is a decision to change to another database (this by no means totally enforces
    the structure of a database connection. It serves as a sort of guideline)
    """

    @abstractmethod
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.client = None

    @abstractmethod
    def connect(self, thread_index: int):
        """
        Connect to the database

        :param thread_index: CherryPy Thread_Index (used to avoid overloading the database when cherrypy creates it's threads)
        :type thread_index: int
        :return: Instance of DatabaseBase
        :rtype: DatabaseBase
        """
        pass

    @abstractmethod
    def disconnect(self):
        """
        Disconnect from the database
        :return: None
        """
        pass

    """
    The rest of the methods are database dependent
    """
