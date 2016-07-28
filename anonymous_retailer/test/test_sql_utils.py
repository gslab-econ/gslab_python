import unittest, os, sys, pyodbc, inspect
import pandas as pd
sys.path.append('../py')

import sql_utils
reload(sql_utils)
from sql_utils import *

import R2_connection
reload(R2_connection)
from R2_connection import *

class TestSQLUtils(unittest.TestCase):

        def test_clear_tables(self):
            with R2_connection() as cxn:
                cxn.execute("CREATE TABLE test_clear_tablesA (varname NUMBER(1));")
                cxn.execute("CREATE TABLE test_clear_tablesB (varname NUMBER(1));")

            clear_tables(['test_clear_tablesA','test_clear_tablesB'])
            conn = pyodbc.connect("DSN=HASTINGS")
            cursor = conn.cursor()

            with R2_connection() as cxn:
                with self.assertRaises(pyodbc.ProgrammingError):
                    cxn.execute("DROP TABLE test_clear_tablesA PURGE;")

        def test_clear_tables_casecade(self):
            rivers = ['Columbia','Yukon','Platte','Colorado']
            with R2_connection() as cxn:
                cxn.execute("CREATE TABLE test_clear_tablesA (rivers VARCHAR2(30))")
                for river in rivers:
                    cxn.execute("INSERT INTO test_clear_tablesA (rivers) VALUES ('%river%')")
                cxn.execute("""
                        ALTER TABLE test_clear_tablesA ADD CONSTRAINT pk_test_clear_tablesA
                            PRIMARY KEY (rivers) 
                    """)

                cxn.execute("CREATE TABLE test_clear_tablesB (river_name VARCHAR2(30))")
                for river in rivers[:2]:
                    cxn.execute("INSERT INTO test_clear_tablesB (river_name) VALUES ('%river%')")
                cxn.execute("""
                        ALTER TABLE test_clear_tablesB ADD CONSTRAINT fk_river_name
                            FOREIGN KEY (river_name) REFERENCES test_clear_tablesA (rivers)
                    """)

            clear_tables('test_clear_tablesA', cxn.cxn_string)
            with R2_connection() as cxn:
                constraints = cxn.execute("""
                        SELECT * FROM USER_CONSTRAINTS WHERE TABLE_NAME = 'TEST_CLEAR_TABLESB'
                    """).fetchall()

            self.assertTrue(constraints == [])
            clear_tables('test_clear_tablesB', cxn.cxn_string)

        def test_grant_permissions(self):
            with R2_connection() as cxn:
                me = cxn.execute("SELECT USER FROM DUAL").fetchall()[0][0]

            with R2_connection('contact_history') as cxn:
                cxn.execute("CREATE TABLE test_grant_permissions (person_name VARCHAR2(30))")
                cxn.execute("INSERT INTO test_grant_permissions (person_name) VALUES ('Chopin')")
                grant_permissions('test_grant_permissions', cxn.cxn_string, to=me)

            with R2_connection() as cxn:
                cursor = cxn.execute("SELECT * FROM contact_history.test_grant_permissions")
                results = cursor.fetchall()[0][0]
            self.assertTrue(results == 'Chopin')

            with R2_connection('dim') as cxn:
                cxn.execute("CREATE TABLE permissionsA (var NUMBER)")
                cxn.execute("CREATE TABLE permissionsB (var NUMBER)")

            grant_permissions(all_dim_tables=True, to=me)

            with R2_connection() as cxn:
                cxn.execute("SELECT * FROM dim.permissionsA")
                cxn.execute("SELECT * FROM dim.permissionsB")

            with self.assertRaises(pyodbc.Error):
                clear_tables(['test_clear_tablesA'], "DSN=no_such_name")

            with self.assertRaises(SyntaxError):
                grant_permissions(tables=['test_grant_permissions'], all_dim_tables=True)

            with self.assertRaises(SyntaxError):
                grant_permissions()

            with R2_connection('contact_history') as cxn:
                cxn.execute("DROP TABLE test_grant_permissions PURGE")

            with R2_connection('dim') as cxn:
                cxn.execute("DROP TABLE permissionsA PURGE")
                cxn.execute("DROP TABLE permissionsB PURGE")

        def test_normalize_string_col(self):
            rivers = ['Columbia','Yukon','Platte','Colorado']
            with R2_connection() as cxn:
                cxn.execute("CREATE TABLE rivers (river VARCHAR2(30))")
                for river in rivers:
                    cxn.execute("INSERT INTO rivers (river) VALUES ('%river%')")

            normalize(table='rivers', column='river')
            normalize(table='rivers', column='river', schema='dim')
            normalize(table='rivers', column='river', key='river_int', out_table_name='rivers_dim')
            
            with R2_connection() as cxn:
                r1 = cxn.execute("SELECT river, river_key FROM river").fetchall()
                r2 = cxn.execute("SELECT river, river_key FROM dim.river").fetchall()
                r3 = cxn.execute("SELECT river, river_int FROM rivers_dim").fetchall()

                cxn.execute("DROP TABLE river PURGE")
                cxn.execute("DROP TABLE rivers_dim PURGE")
                cxn.execute("DROP TABLE rivers PURGE")

            as_list = lambda x: list(x)
            expected = zip(sorted(rivers), range(1,5))

            for result in [r1, r2, r3]:
                self.assertEqual(map(as_list, expected), map(as_list, result))

            with R2_connection('dim') as cxn:
                cxn.execute("DROP TABLE river PURGE")


if __name__=='__main__':
    unittest.main()
