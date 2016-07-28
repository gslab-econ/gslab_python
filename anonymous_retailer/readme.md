#################################################################################################
# Readme for sql_utils.py, run_sql_loader.py, and save_table.py
#################################################################################################

--------------------------------------------------------------
sql_utils.py
--------------------------------------------------------------

sql_utils.py is a python module which contains tools for interacting with SQL databases. Contents:

    clear_tables(tables, [cxn_string])

Clear tables deletes each table in the list 'tables' from the database connection specified 
in 'cxn_string'. If 'cxn_string' is not specified it defaults to "DSN=HASTINGS". See the 
documentation for PyODBC for more information on connection strings.

    grant_permissions(tables, [cxn_string [, permissions [, to]]])

Grant permissions grants the table access/modification permissions specified in 'permissions' to 
the list of tables in 'tables' from the database connection specified in 'cxn_string' for the user 
specified in 'to'. The group 'retail2_user' will encompass all GSLab RAs on the retailer VM. 
If 'cxn_string' is not specified it defaults to "DSN=HASTINGS", if 'permissions' is not specified 
it defaults to 'SELECT', if 'to' is not specified it defaults to 'retail2_user'.

    class R2_connection([schema [, connect])
        Arguments:
            schema  -> string  : the schema to connect to. Defaults to default_schema.
            connect -> boolean : whether or not to open a connection. Defaults to True
        Attributes:
            schema     -> string : the name of the schema to which the instance is connected
            cxn_string -> string : an ODBC connection string which can be passed to ODBC drivers
            password   -> string : the password associated with the connection
        Methods:
            close   void   -> None          : closes the current connection. 
            execute string -> pyodbc.cursor : execute the string as a SQL command. 
                                              See note on parameter substitution.
        Options:
            default_schema -> string : the schema to connect to if no schema is passed explicitly.
                                       defaults to the user's schema.

R2_connection parses the text file specified in the environment variable "SQL_AUTH_PATH" and sets
the attributes 'cxn_string', and 'password' according to the database schema specified in the
construction argument 'schema'. By default, an ODBC connection to the schema is opened.

The R2_connection object may used as a context manager. When used as a context manager, database
connections are automatically closed even in the event of an unhandled exception. For this reason,
it is recommended that R2_connections be opened using the "with ... as ..." keyword.

The 'execute()' method to R2_connection can automatically paste parameters into SQL statements.
Parameter names must be enclosed in '%' signs and the parameter must resolve to a defined variable.
The execute method first searches for a parameter in the calling frame's local variables. If no
matching parameter is found, the calling frame's global variables are searched. If no matching
parameter is found a NameError is raised.

Example:
    
    >>> R2_connection.default_schema = 'MyDbSchema'
    >>> with R2_connection() as cxn:
    ...     max_spend = 10000
    ...     cxn.execute('SELECT * FROM table WHERE spend <= %max_spend%')

    The string 'SELECT * FROM table WHERE spend <= %max_spend%' will resolve to
    'SELECT * FROM table WHERE spend <= 10000' when executed.

Description of 'cxn_file':

cxn_file is a tab delimited text file containing the login information associated with a specific
schema in the database. It is structured as follows: schema \t password \t connection string \n

--------------------------------------------------------------
run_sql_loader.py
--------------------------------------------------------------

run_sql_loader.py provides gslab_make style interfaces to the Oracle SQLLoader command line utility

    run_sql_loader(program, [, log [, options [, stream]]])

run_sql_loader runs the SQLLoader control file specified in 'program', optionally redirecting 
output of 'stream' to input of 'program'. Command line options to SQLLoader can be specified as 
a dictionary using the argument 'options'. The log file produced by SQLLoader is copied to the 
path specified in 'log'. If 'log' is not specified it defaults to '../output/make.log'. If 'options' 
is unspecified the following defaults for command line options are used:

    log    : '../temp/' + program + '.log'
    bad    : '../temp/' + program + '.bad'
    userid : '/'

If 'stream' is unspecified it defaults to None and the path specified in the loader control file 
is used as input.

--------------------------------------------------------------
save_table.py
--------------------------------------------------------------

save_table.py provides a 'save_data' analog for tables produced in the database.

    save_table(table, key, cxn_string, [**kwargs])

save_table optionally builds a primary key index on the database table specified in 'table' using 
the columns specified in 'key'. The columns of 'key' must be uniquely identifying and non-null
else an exception is raised. A table of summary statistics describing the table is printed
to the stdout of the calling program and optionally to a text file. The following are valid
keyword arguments to save_table:
    
    log           -> string :  a path to which summary statistics will be printed. 
                               Defaults to '../output/data_file_manifest.log'
    mode          -> string  : the mode in which the log file will be opened. 
                               Defaults to 'ab' (append).
    stats_only    -> boolean : controls whether a primary key will be built. Defaults to False.
    key_name      -> string  : the name of the primary key to be built. Defaults to pk_{table}.
    compress      -> boolean : controls whether the primary key will be compressed. Defaults to True
                               if more than one variable is passed as a primary key and False 
                               otherwise.
    index_options -> string  : a string to pass to the command which builds the primary key. Can
                               be used to control the Oracle parameters used in constructing the 
                               key. Defaults to "COMPRESS ADVANCED LOW PARALLEL" if compress=True 
                               and an empty string otherwise. 

examples:

    >>> from anonymous_retailer.py.sql_utils import *
    >>> from anonymous_retailer.py.run_sql_loader import *
    >>> from anonymous_retailer.py.save_table import save_table
    >>>
    >>> cxn = R2_connection('schema', connect=False)
    >>> clear_tables(['table'], cxn.cxn_string)
    >>> run_sql_loader(program = 'import_data.ctl', options = {'userid' : cxn.userid}, 
    ...     stream = 'gunzip -c ../external/data/data.csv.gz')
    >>> grant_permissions(['table'], cxn_string = cxn.cxn_string)
    >>>
    >>> max_valid_amount = 8
    >>> sql = """CREATE TABLE new_table AS SELECT * 
    ...          FROM table WHERE amount < %max_valid_amount%"""
    >>> with R2_connection() as cxn:
    ...     cxn.execute(sql)
    ...     cxn_string = cxn.cxn_string
    >>> save_table('new_table','key_variable',cxn_string)
