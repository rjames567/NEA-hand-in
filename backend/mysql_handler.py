# ------------------------------------------------------------------------------
# Standard Python library imports
# ------------------------------------------------------------------------------
import time

# ------------------------------------------------------------------------------
# Third party Python library imports
# ------------------------------------------------------------------------------
import mysql.connector

# ------------------------------------------------------------------------------
# Classes
# ------------------------------------------------------------------------------
class Connection:
    def __init__(self, user, password, schema, host):
        self._user = user
        self._password = password
        self._schema = schema
        self._host = host
        self._connect() # Establish database connection
        self._query_time = None

    def _connect(self):
        self._connection = mysql.connector.connect(
            user=self._user,
            password=self._password,
            host=self._host,
            database=self._schema
        )

        self._cursor = self._connection.cursor()

    def query(self, query):
        start_time = time.time() # Changes this first incase multi-threading is
            # used in the future - a query may be made in a different thread.
        self._query_time = None

        try:
            self._cursor.execute(query)
        except mysql.connector.Error:
            self._connect() # Some databases specifies connections close after
                # certain amount of time inactive. This repoens the connection
                # if a timeout occurs
            self._cursor.execute(query)

        try:
            result = self._cursor.fetchall() # Needs to come before the if
                # statement as otherwise can result in 'unread result found' error
        except mysql.connector.errors.InterfaceError:
            result = [] # Incase the method does not provide any result, like
                # INSERT

        self._connection.commit() # Applies changes from the query to the db

        self._query_time = time.time() - start_time

        return result # Use tuples as they are faster


    @property
    def query_time(self):
        return self._query_time

    def __del__(self):
        self._connection.close()
