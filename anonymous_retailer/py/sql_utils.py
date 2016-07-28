import os
import re
import pyodbc
from R2_connection import R2_connection
from sql_exceptions import *

def grant_permissions(tables=None, cxn_string="DSN=HASTINGS", 
                      permissions='SELECT', to='retailer2_user', 
                      all_dim_tables=False):
    
    if (all_dim_tables is True) and (tables is not None):
        raise SyntaxError("Can only set one of 'tables' or 'all_dim_tables'")
    if (all_dim_tables is False) and (tables is None):
        raise SyntaxError("Must set either 'all_dim_tables")
    if (tables is not None):
        if type(tables) is str:
            tables = [tables]
        if not isinstance(tables,list):
            raise TypeError("Argument 'tables' must be list")

    connection = pyodbc.connect(cxn_string)
    cursor = connection.cursor() if (all_dim_tables is False) else R2_connection('dim')

    if (all_dim_tables is True):
        res = cursor.execute("SELECT TABLE_NAME FROM USER_TABLES").fetchall()
        tables = map(lambda x: x[0], res)

    for t in tables:
        print "GRANT %s ON %s TO %s\n" %(permissions, t, to)
        cursor.execute(
            "GRANT " + permissions + " ON " + t + " TO " + to +";"
        )
    if (all_dim_tables is True):
        cursor.close()
    else:
        connection.commit()
    connection.close()

def clear_tables(tables, cxn_string='DSN=HASTINGS', cascade_constraints=True):
    if type(tables) is str:
        tables = [tables]
    if not isinstance(tables,list):
        raise TypeError("Argument 'tables' must be list")

    options = 'CASCADE CONSTRAINTS ' if (cascade_constraints) else ' '
    connection = pyodbc.connect(cxn_string)
    for t in tables:
        print "Clearing table: %s" %t
        cursor = connection.cursor()
        try:
            cursor.execute("DROP TABLE " + t + " {}PURGE".format(options))
            connection.commit()
        except pyodbc.ProgrammingError as rc:
            if rc[0] != '42S02':
                raise rc
    connection.close()

def normalize(table="", column="", add_cols="", key=None, out_table_name=None, schema=None):
    if (out_table_name is None):
        out_table_name = column
    if (key is None):
        key = column + '_key'

    if '.' not in table:
        table = R2_connection.default_schema + '.' + table
    table_schema = table.split('.')[0]

    if (schema is not None) and (schema != table_schema):
        with R2_connection() as cxn:
            cxn.execute("GRANT SELECT ON %table% TO %schema%")

    select_cols = column if add_cols == "" else column + ", " + add_cols
    with R2_connection(schema=schema) as cxn:
        clear_tables(out_table_name, cxn.cxn_string)
        cxn.execute("""
            CREATE TABLE %out_table_name% AS (
                SELECT %select_cols%, DENSE_RANK() OVER (
                    ORDER BY %column%) AS %key%
                  FROM %table%
                 WHERE %column% IS NOT NULL
                 GROUP BY %select_cols%
            )
        """)
        if (schema is not None):
            cxn.execute("GRANT SELECT, REFERENCES ON %out_table_name% TO %table_schema%")
    
    return (column, key)