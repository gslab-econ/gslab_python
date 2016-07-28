import unittest, os, sys, pyodbc, inspect
import pandas as pd
sys.path.append('../py')
from sql_exceptions import *
from sql_utils import *

import R2_connection
reload(R2_connection)
from R2_connection import *

GLOBAL_PARAM = 3.14159

class TestR2Connection(unittest.TestCase):

    def test_r2_connection_context_manager(self):
            with R2_connection() as cxn:
                clear_tables('test_r2_connection', cxn.cxn_string)
                cxn.execute("CREATE TABLE test_r2_connection (person_name VARCHAR2(30))")
                person_name = "Scarlatti"
                cxn.execute("INSERT INTO test_r2_connection (person_name) VALUES ('%person_name%')")
                person_name = "Rachmaninoff"
                cxn.execute("INSERT INTO test_r2_connection (person_name) VALUES ('%person_name%')")

            with R2_connection() as cxn:
                cursor = cxn.execute("SELECT * FROM test_r2_connection")
                results = cursor.fetchall()
                cxn.execute("DROP TABLE test_r2_connection PURGE")

            results = map(lambda x: x[0], results)
            self.assertTrue(results == ['Scarlatti', 'Rachmaninoff'])

    def test_parameter_substitution(self):
        local_param = 8.2702
        with R2_connection() as cxn:
            cxn.execute(("CREATE TABLE test_r2_connection "  
                         "(scope VARCHAR2(30), value NUMBER)"))
            cxn.execute(("INSERT INTO test_r2_connection (scope, value) "
                         "VALUES ('global', %GLOBAL_PARAM%)"))
            cxn.execute(("INSERT INTO test_r2_connection (scope, value)"
                         "VALUES ('local', %local_param%)"))
            local_param = 5.3298
            cxn.execute(("INSERT INTO test_r2_connection (scope, value) "
                         "VALUES ('localer', %local_param%)"))
            cursor = cxn.execute("SELECT * FROM test_r2_connection")
            results = cursor.fetchall()
            cxn.execute("DROP TABLE test_r2_connection PURGE")

        results = {r[0] : r[1] for r in results}
        self.assertTrue(results['global'] == 3.14159)
        self.assertTrue(results['local'] == 8.2702)
        self.assertTrue(results['localer'] == 5.3298)

    def test_R2_connection_basic(self):
        me = pyodbc.connect("DSN=HASTINGS").cursor(
                 ).execute("SELECT USER FROM DUAL").fetchall()[0][0]
        cxn = R2_connection()
        self.assertTrue(cxn.schema == me)
        self.assertTrue(cxn.password == '/')
        self.assertTrue(cxn.cxn_string == 'DSN=HASTINGS')

        cxn = R2_connection('/')
        self.assertTrue(cxn.schema == me)
        self.assertTrue(cxn.password == '/')
        self.assertTrue(cxn.cxn_string == 'DSN=HASTINGS')

        sql = "CREATE TABLE test_r2_connection (person_id NUMBER(2))"
        cxn.execute(sql)

        # test that parameters are substituted into strings
        person_id = 1
        sql = "INSERT INTO test_r2_connection (person_id) VALUES (%person_id%)"
        cxn.execute(sql)
        person_id += 1
        cxn.execute(sql)

        # test that results were as expected
        cursor = cxn.execute("SELECT * FROM test_r2_connection")
        results = map(lambda x: x[0], cursor.fetchall())
        self.assertTrue(results == [1,2])

        cxn.execute('DROP TABLE test_r2_connection PURGE')
        cxn.close()

    def test_set_default_connection(self):
        R2_connection.default_schema = 'retailer2'
        
        with R2_connection() as cxn:
            result = cxn.execute("SELECT USER FROM DUAL").fetchall()
        self.assertTrue(result[0][0] == 'RETAILER2')

        with R2_connection('contact_history') as cxn:
            result = cxn.execute("SELECT USER FROM DUAL").fetchall()
        self.assertTrue(result[0][0] == 'CONTACT_HISTORY')

        with R2_connection() as cxn:
            result = cxn.execute("SELECT USER FROM DUAL").fetchall()
        self.assertTrue(result[0][0] == 'RETAILER2')

    def test_r2_connection_exceptions(self):
        cxn = R2_connection()
        cxn.close()
        with self.assertRaises(IllegalStateException):
            cxn.execute("SELECT USER FROM DUAL")

        cxn = R2_connection(connect=False)
        with self.assertRaises(IllegalStateException):
            cxn.execute("SELECT USER FROM DUAL")

        with self.assertRaises(AuthenticationError):
            cxn = R2_connection('potatoes')

        with self.assertRaises(NameError):
            with R2_connection() as cxn:
                cxn.execute("SELECT * FROM %POTATOES%")

if __name__=='__main__':
    unittest.main()