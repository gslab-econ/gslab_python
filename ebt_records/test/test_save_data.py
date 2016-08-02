import unittest
import os
import sys
import re
import shutil
import StringIO
import hashlib
import pandas as pd
import numpy  as np
sys.path.append('../py')
from save_data import save_data

np.random.seed(1398205)

class test(unittest.TestCase):

    def setUp(self):
        if os.path.exists('../output'): shutil.rmtree('../output')
        os.mkdir('../output')

        if os.path.exists('../temp'): shutil.rmtree('../temp')
        os.mkdir('../temp')

        self.DataFrame = pd.DataFrame(np.random.rand(10,3))
        self.DataFrame.columns = ['var1', 'var2', 'var3']
        self.DataFrame['id1'] = (['A']*5) + (['B']*5)
        self.DataFrame['id2'] = range(5)*2
        self.DataFrame['non_unique_key'] = 1
        self.DataFrame['key_with_nas'] = self.DataFrame['id2']
        self.DataFrame.ix[range(0,10,2), 'key_with_nas'] = np.nan

        DataFrame = pd.DataFrame(np.random.rand(10,3))
        DataFrame.columns = ['var1', 'var2', 'var3']
        DataFrame['id1'] = (['A']*5) + (['B']*5)
        DataFrame['id2'] = range(5)*2
        DataFrame['non_unique_key'] = 1
        DataFrame['key_with_nas'] = DataFrame['id2']
        DataFrame.ix[range(0,10,2), 'key_with_nas'] = np.nan

    def tearDown(self):
        shutil.rmtree('../output')

    def test_good(self):
        DataFrame = self.DataFrame

        # test expected behavior
        size_orig = DataFrame.size
        frame = save_data(
                    DataFrame, 
                    filename = '../output/test_good.csv',
                    data_key = ['id1', 'id2'],
                    return_object = True,
                    index = False
                )
        self.assertTrue(os.path.exists('../output/test_good.csv'))
        self.assertTrue(os.path.exists('../output/data_file_manifest.log'))
        self.assertTrue(size_orig == frame.size)

        expected_varorder = ['id1','id2','var1','var2','var3','non_unique_key','key_with_nas']
        self.assertTrue(frame.columns.tolist() == expected_varorder)

        frame_from_disk = pd.read_csv('../output/test_good.csv')
        self.assertTrue(size_orig == frame_from_disk.size)
        self.assertTrue(frame_from_disk.columns.tolist() == expected_varorder)

        # test using different manifest name
        frame = save_data(
                    DataFrame,
                    filename = '../output/test_good.csv',
                    data_key = ['id1','id2'],
                    return_object = True,
                    log = '../output/new_log_name.log'
                )
        self.assertTrue(os.path.exists('../output/new_log_name.log'))

        # test HDF format
        frame = save_data(
                    DataFrame,
                    filename = '../output/test_good.h5',
                    data_key = ['id1','id2'],
                    ftype = 'hdf5',
                    key = 'test_hdf',
                    compression = 9,
                    return_object = True,
                    complib = 'blosc'
                )

        frame_from_disk = pd.read_hdf('../output/test_good.h5', key = 'test_hdf')
        self.assertTrue(frame_from_disk.equals(frame))
        self.assertTrue(frame_from_disk.columns.tolist() == expected_varorder)

        # test the writing to temp does not produce manifest log
        os.unlink('../output/data_file_manifest.log')
        
        save_data(
            DataFrame,
            filename = '../temp/test_good.csv',
            data_key = ['id1','id2']
        )
        self.assertTrue(os.path.exists('../temp/test_good.csv'))
        self.assertFalse(os.path.exists('../output/data_file_manifest.log'))

        # test saving in Stata format
        save_data(
            DataFrame,
            filename = '../output/test_good.dta',
            data_key = ['id1','id2'],
            ftype = 'dta',
            return_object = False
        )

        self.assertTrue(os.path.exists('../output/test_good.dta'))
        
        # test passing a writable object as the manifest log
        log_buffer = StringIO.StringIO()
        save_data(
            DataFrame,
            filename = '../output/test_good.csv',
            data_key = ['id1','id2'],
            log = log_buffer
        )
        log_contents = log_buffer.getvalue()
        log_buffer.close()
        hash_contents = hashlib.sha224(log_contents[0:241]).hexdigest()
        self.assertTrue(hash_contents == 'ca49a370f8072c265ccc3e561a118848515bbf42256c02ac932e2735')

    def test_bad(self):
        DataFrame = self.DataFrame

        # test an incorrect file type
        with self.assertRaises(NotImplementedError):
            save_data(DataFrame,
                      filename = '../output/test_bad.csv',
                      data_key = ['id1','id2'],
                      ftype = 'rda')

        # test a non-unqiuely identifying key
        with self.assertRaises(StandardError):
            save_data(DataFrame,
                      filename = '../output/test_bad.csv',
                      data_key = 'non_unique_key')

        # test a key with missing values
        with self.assertRaises(StandardError):
            save_data(DataFrame,
                      filename = '../output/test_bad.csv',
                      data_key = 'key_with_nas')

# RUN TESTS
if __name__ == '__main__':
    unittest.main()