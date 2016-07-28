import unittest
import os
import sys
import numpy as np
import pandas as pd
sys.path.append('../py')

import save_table
reload(save_table)
from save_table import *

import R2_connection
reload(R2_connection)
from R2_connection import *

np.random.seed(32989)

class TestSaveTable(unittest.TestCase):

    def setUp(self):
        person_id = pd.DataFrame(data = {
                        'person_id' : np.kron(np.arange(1,10), np.ones(10, dtype = np.int))
                    })
        person_name = pd.DataFrame(data = {
                          'person_name' : np.array(['Vivaldi','Bach','Handel','Lully','Chopin'
                                                    'Hayden','Scarlatti','Monteverdi','Telemann',
                                                    'Rostropovitch']),
                          'person_id'   : np.arange(1,10)
                      })
        test_table = pd.merge(person_id, person_name)

        toucan_purchase_date = np.random.choice(
                                    pd.date_range('2003-04-02', '2009-02-04').values,
                                    len(test_table.index),
                                    replace = False
                               )
        
        test_table.loc[:,'toucan_purchase_date'] = pd.DatetimeIndex(toucan_purchase_date)
        test_table.loc[:,'toucan_weight'] = np.random.normal(12, 2, len(test_table.index))
        test_table.loc[:,'num_toucans'] = np.random.randint(3, 80, len(test_table.index))

        create_table_stmt = """CREATE TABLE test_save_table (
                                   person_id            NUMBER(3),
                                   toucan_purchase_date DATE,
                                   person_name          VARCHAR2(30),
                                   toucan_weight        NUMBER,
                                   num_toucans          NUMBER(2)
                                )
                             """
        insert_row_stmt = """INSERT INTO test_save_table 
                                 (person_id, toucan_purchase_date, person_name, 
                                  toucan_weight, num_toucans) VALUES
                                 (%person_id%, TO_DATE('%purchase_date%', 'YYYY-MM-DD'), 
                                  '%person_name%', %toucan_weight%, %num_toucans%)
                          """

        with R2_connection() as cxn:
            cxn.execute(create_table_stmt)
            for row in test_table.iterrows():
                person_id, person_name, toucan_weight, \
                purchase_date, num_toucans = self.parse_row(row[1])
                cxn.execute(insert_row_stmt, verbose=False)

        self.test_table = test_table

    def tearDown(self):
        with R2_connection() as cxn:
            cxn.execute("DROP TABLE test_save_table PURGE")
        if os.path.exists('../temp/data_file_manifest.log'):
            os.unlink('../temp/data_file_manifest.log')

    def parse_row(self, table_row):
            return (table_row['person_id'], table_row['person_name'], table_row['toucan_weight'],
                    str(table_row['toucan_purchase_date'])[:10], table_row['num_toucans'])

    def test_basic_functionality(self):
        key = ['person_id','toucan_purchase_date']
        logfile = '../temp/data_file_manifest.log'
        cxn_string = R2_connection(connect=False).cxn_string
        table_summary = save_table('test_save_table', key, cxn_string, log = logfile)

        # verify that a log file was produced
        self.assertTrue(os.path.exists(logfile))

        # check that the returned summary stats are correct
        stats = self.test_table.describe()
        table_summary = table_summary.set_index('Variable')
        for varname in ['NUM_TOUCANS','TOUCAN_WEIGHT','PERSON_ID']:
            self.assertAlmostEqual(table_summary.ix[varname, 'COUNT'], 
                                   stats.ix['count', varname.lower()])
            self.assertAlmostEqual(table_summary.ix[varname, 'AVG'],
                                   stats.ix['mean', varname.lower()])
            self.assertAlmostEqual(table_summary.ix[varname, 'STDDEV'],
                                   stats.ix['std', varname.lower()])
            self.assertAlmostEqual(table_summary.ix[varname, 'MIN'],
                                   stats.ix['min', varname.lower()])
            self.assertAlmostEqual(table_summary.ix[varname, 'MAX'],
                                   stats.ix['max', varname.lower()])

        self.assertEqual(table_summary.ix['TOUCAN_PURCHASE_DATE', 'MIN'],
                         self.test_table['toucan_purchase_date'].min().to_datetime())
        self.assertEqual(table_summary.ix['TOUCAN_PURCHASE_DATE', 'MAX'],
                         self.test_table['toucan_purchase_date'].max().to_datetime())

    def get_pk_info(self):
        sql = """SELECT cols.table_name, cols.column_name,
                        const.status, const.constraint_name
                   FROM all_constraints const, all_cons_columns cols
                  WHERE cols.table_name = 'TEST_SAVE_TABLE' AND 
                        const.constraint_type = 'P'         AND
                        const.constraint_name = cols.constraint_name
              """
        with R2_connection() as cxn:
            cursor = cxn.execute(sql)
            pk_info = cursor.fetchall()
        return pk_info

    def test_optional_arguments(self):
        table = 'test_save_table'
        key = ['person_id','toucan_purchase_date']
        log = '../temp/data_file_manifest.log'
        cxn_string = R2_connection(connect=False).cxn_string
        
        # table with statsonly does not produce a primary key
        save_table(table, key, cxn_string, log=None, stats_only=True)
        
        pk_info = self.get_pk_info()
        self.assertTrue(pk_info == [])
        self.assertFalse(os.path.exists(log))

        # table with stats_only still makes a log if specified
        save_table(table, key, cxn_string, log=log, stats_only=True)

        pk_info = self.get_pk_info()
        self.assertTrue(pk_info == [])
        self.assertTrue(os.path.exists(log))
        curr_log_size = os.stat(log).st_size

        # check that key name can be changed and that log writing mode can be changed
        save_table(table, key, cxn_string, log=log, key_name='seven_salubrious_seals', mode = 'wb')
        pk_info = self.get_pk_info()

        self.assertTrue(os.stat(log).st_size <= curr_log_size)
        self.assertTrue(pk_info[0][3] == 'SEVEN_SALUBRIOUS_SEALS')

    def test_single_column_key(self):
        with R2_connection() as cxn:
            cxn.execute('ALTER TABLE test_save_table ADD contrived_key NUMBER(2)')
            cxn.execute('UPDATE test_save_table SET contrived_key = ROWNUM')
            cxn_string = cxn.cxn_string

        log = '../temp/data_file_manifest.log'
        save_table('test_save_table', 'contrived_key', cxn_string, log=log)

        pk_info = self.get_pk_info()
        self.assertTrue(pk_info[0][1] == 'CONTRIVED_KEY')

    def test_no_compression(self):
        table = 'test_save_table'
        key = ['person_id','toucan_purchase_date']
        log = '../temp/data_file_manifest.log'
        cxn_string = R2_connection(connect=False).cxn_string
        save_table(table, key, cxn_string, log=log, compress=False)

    def test_bad_table(self):
        with self.assertRaises(pyodbc.ProgrammingError):
            save_table('no_such_table', 'potato', 'DSN=HASTINGS')

    def test_bad_key(self):
        table = 'test_save_table'
        key = ['person_id','toucan_purchase_date']
        log = '../temp/data_file_manifest.log'
        cxn_string = R2_connection(connect=False).cxn_string

        with self.assertRaises(pyodbc.Error):
            save_table(table, 'person_id', cxn_string, log=log)

        with self.assertRaises(pyodbc.ProgrammingError):
            save_table(table, 'no_such_column', cxn_string, log=log)

        with R2_connection() as cxn:
            cxn.execute("UPDATE test_save_table SET person_id = NULL WHERE ROWNUM < 2")

        with self.assertRaises(pyodbc.Error):
            save_table(table, key, cxn_string, log=log)

if __name__=='__main__':
    unittest.main()
