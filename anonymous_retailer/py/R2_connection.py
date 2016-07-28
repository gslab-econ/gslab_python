import os
import re
import pyodbc
import inspect
from sql_exceptions import *

class R2_connection():

    _user_schema   = pyodbc.connect(
        "DSN=HASTINGS").cursor().execute("SELECT USER FROM DUAL").fetchall()[0][0]
    default_schema = _user_schema

    def __init__(self, schema=None, connect=True):
        if ((schema is None) or (schema == '/')) and (self.default_schema is self._user_schema):
            self.schema = self._user_schema
            self.cxn_string = 'DSN=HASTINGS'
            self.password = '/'
            self.userid = '/'
        elif (schema is None) and (self.default_schema is not self._user_schema):
            self.schema = self.default_schema
            self.cxn_string = None
            self.password = None
            self._set_conn_attrs()
        else:
            self.schema = schema
            self.cxn_string = None
            self.password = None
            self._set_conn_attrs()

        self._connection = None
        if (connect is True):
            self._connection = pyodbc.connect(self.cxn_string)

    def _die_if_not_connected(self):
        if (self._connection is None):
            raise IllegalStateException("Action is not possible without a connection")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, value, traceback):
        self.close()

    def close(self):
        self._die_if_not_connected()
        try:
            self._connection.close()
            self._connection = None
        except pyodbc.ProgrammingError:
            pass

    def _set_conn_attrs(self):
        sql_auth_path = os.getenv('SQL_AUTH_PATH')
        if (sql_auth_path is None):
            raise AuthenticationError('Must set the environment variable SQL_AUTH_PATH')

        with open(sql_auth_path, 'rb') as fh:
            sql_auth = fh.read()
        sql_auth = sql_auth.split('\n')

        for schema in sql_auth:
            attrs = schema.split('\t')
            if not (len(attrs) == 3):
                raise AuthenticationError(
                    "SQL authentication file {} was not specified correctly".format(sql_auth_path)
                )
            if attrs[0] == self.schema:
                self.password = attrs[1]
                self.userid = '{}/{}'.format(self.schema, self.password)
                self.cxn_string = attrs[2]
        if (self.password is None):
            raise AuthenticationError("Schema {} not found in file {}".format(
                self.schema, sql_auth_path))

    def execute(self, sql, commit=True, verbose=True):
        self._die_if_not_connected()

        cursor = self._connection.cursor()
        sql = self._prepare_sql(sql)
        if (verbose is True):
            print sql
        cursor.execute(sql)
        if (commit is True): 
            self._connection.commit()
        return cursor 

    # a helper method which can be used to automate the process of pasting parameter values into 
    # SQL queries
    def _prepare_sql(self, sql):
        params = re.findall('(\%\w+\%)', sql)
        params = map(lambda x: x.replace('%', ''), params)

        # IMPORTANT NOTE: If the nesting depth of _prepare_sql is changed the indexing on the
        # calling stack -must- be updated 
        calling_frame = inspect.stack()[2][0]
        caller_locals = calling_frame.f_locals
        caller_globals = calling_frame.f_globals
        vals = [self._get_param_value(x, caller_locals, caller_globals) for x in params]

        param_tuples = zip(params, vals)
        for p,v in param_tuples:
            sql = sql.replace('%'+p+'%', str(v))
        return sql

    def _get_param_value(self, param, caller_locals, caller_globals):
        if param in caller_locals:
            return caller_locals[param]
        if param in caller_globals:
            return caller_globals[param]
        raise NameError("Object {} not found".format(param))