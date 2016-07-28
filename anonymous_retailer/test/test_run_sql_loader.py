import unittest, os, csv, gzip, sys, subprocess
import pandas as pd
sys.path.append('../py')
from run_sql_loader import run_sql_loader
from sql_utils import *

import R2_connection
reload(R2_connection)
from R2_connection import *

class TestRunSQLLoader(unittest.TestCase):
    
    def setUp(self):
        sql = ('CREATE TABLE test_sql_loader ('
               '    var1  NUMBER NOT NULL,'
               '    var2  NUMBER NOT NULL,'
               '    var3  NUMBER NOT NULL'
               ')')

        with R2_connection() as cxn:
            print cxn.schema
            cxn.execute(sql)

        fh = open('../temp/test_sql.log', mode = 'wb')
        fh.close()

    def tearDown(self):
        with R2_connection() as cxn:
            cxn.execute("DROP TABLE test_sql_loader PURGE")

    def test_basic_function(self):
        log = '../temp/test_sql.log'
        prog = './input/test_sql_loader.ctl'
        run_sql_loader(program=prog, log=log)

        with R2_connection() as cxn:
            table = cxn.execute("SELECT * FROM test_sql_loader").fetchall()
        table = [n for row in table for n in row]

        with open('./input/test_sql_loader.csv', 'rb') as fh:
            reader = csv.reader(fh)
            reader.next()
            expected = [float(elt) for row in reader for elt in row]

        for t,e in zip(table, expected):
            self.assertAlmostEqual(t, e)

        with open(log, mode = 'rc') as fh:
            logfile = fh.read()
        self.assertTrue('Rows not loaded due to data errors' in logfile)
        self.assertFalse(os.path.exists('../temp/test_sql_loader.log'))

    def test_optional_params(self):
        log = '../temp/test_sql.log'
        prog = './input/test_sql_loader.ctl'
        run_sql_loader(program = prog, log=log, options = {'errors' : '20'})

        with open(log, mode = 'rc') as fh:
            logfile = fh.read()
        self.assertTrue('Errors allowed: 20' in logfile)

    def test_input_stream(self):
        log = '../temp/test_sql.log'
        gunzip_stream = 'gunzip -c ./input/test_sql_loader.csv.gz'
        stream_prog = './input/test_sql_loader_stream.ctl'
        run_sql_loader(program = stream_prog, log = log, stream = gunzip_stream)

        with R2_connection() as cxn:
            table = cxn.execute("SELECT * FROM test_sql_loader").fetchall()
        table = [n for row in table for n in row]

        with gzip.open('./input/test_sql_loader.csv.gz', 'rb') as fh:
            reader = csv.reader(fh)
            reader.next()
            expected = [float(elt) for row in reader for elt in row]

        for t,e in zip(table, expected):
            self.assertAlmostEqual(t, e)

    def test_alternate_schema(self):
        cxn = R2_connection('contact_history', connect=False)
        clear_tables(['test_sql_loader'], cxn.cxn_string)
        
        with R2_connection('contact_history') as cxn:
            cxn.execute('CREATE TABLE test_sql_loader ('
                        '    var1  NUMBER NOT NULL,'
                        '    var2  NUMBER NOT NULL,'
                        '    var3  NUMBER NOT NULL'
                        ')')

        log = '../temp/test_sql.log'   
        prog = './input/test_sql_loader.ctl'
        loader_opts = {'userid' : '{}/{}'.format(cxn.schema, cxn.password)}
        run_sql_loader(program=prog, log=log, options=loader_opts)

        with R2_connection('contact_history') as cxn:
            table = cxn.execute("SELECT * FROM test_sql_loader").fetchall()
        table = [n for row in table for n in row]

        with open('./input/test_sql_loader.csv', 'rb') as fh:
            reader = csv.reader(fh)
            reader.next()
            expected = [float(elt) for row in reader for elt in row]

        for t,e in zip(table, expected):
            self.assertAlmostEqual(t, e)

        with R2_connection('contact_history') as cxn:
            cxn.execute("DROP TABLE test_sql_loader PURGE")

    def test_exceptions(self):
        log = '../temp/test_sql.log'   
        prog = './input/test_sql_loader.ctl'

        with self.assertRaises(subprocess.CalledProcessError):
            run_sql_loader(program = prog, log = log, options = {'potatoes' : 'tasty'})
        with self.assertRaises(subprocess.CalledProcessError):
            run_sql_loader(program = 'potatoes_are_tasty.ctl', log = log)
        with self.assertRaises(subprocess.CalledProcessError):
            run_sql_loader(program = './input/test_bad_sql_loader.ctl', log = log)

if __name__=='__main__':
    unittest.main()