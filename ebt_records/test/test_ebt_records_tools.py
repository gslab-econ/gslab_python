import unittest
import os
import sys
import re
import shutil
import pandas as pd
import numpy  as np
sys.path.append('../py')
import ebt_records_tools as ebt

class test(unittest.TestCase):

    def setUp(self):
        if os.path.exists('../output'): shutil.rmtree('../output')
        os.mkdir('../output')
        
        trans_files = os.listdir('../external_links/transactions')
        trans_files = map(lambda x: '../external_links/transactions/' + x, trans_files)
        self.ebt_transactions = pd.read_csv(
                                    trans_files[0]
                                ).drop_duplicates().reset_index(
                                    drop = True
                                )
        self.ebt_transactions.columns = map(
            lambda x: x.lower().replace(' ','_'), self.ebt_transactions.columns.tolist()
        )
        self.duplicated_data = pd.DataFrame({
                                   'var1' : range(10),
                                   'var2' : [1,1,1] + range(2,7) + [9,9]
                               })
        self.categorical_data = pd.DataFrame({
                                    'categorical' : ['A'] * 8 + ['B'] * 2,
                                    'other_data'  : range(10)
                                })
    def tearDown(self):
        shutil.rmtree('../output')

    def test_mask_id(self):
        ebt_transactions = self.ebt_transactions

        unique_values_before = (
            ebt_transactions['casehead_individual_id'].drop_duplicates().count()
        )
        dtype_before = ebt_transactions['casehead_individual_id'].dtype
        self.assertTrue(dtype_before == np.dtype('O'))

        # masking should map all IDs to an integer and drop the original ID
        masked = ebt.mask_id(
                      ebt_transactions, 
                      rawname  = 'individual_id',
                      maskname = 'mask_individual_id',
                      apply_to = 'casehead_individual_id'
                 )
        unique_values_after = masked['mask_casehead_individual_id'].drop_duplicates().count()
        self.assertTrue(unique_values_before == unique_values_after)

        dtype_after = masked['mask_casehead_individual_id'].dtype
        self.assertTrue(
            dtype_after == np.dtype('int64') or dtype_after == np.dtype('int32')
        )

        varnames_after = masked.columns.tolist()
        self.assertFalse('casehead_individual_id' in varnames_after)

    def test_build_numeric_key(self):
        categorical_data = self.categorical_data
        as_numeric = ebt.build_numeric_key(
                         categorical_data,
                         'categorical',
                         saving = '../output/categorical_lookup.h5',
                         compression = 9,
                         complib = 'blosc',
                     )
        self.assertTrue(
            (as_numeric['categorical_key'].dtype == np.dtype('int32')) or
            (as_numeric['categorical_key'].dtype == np.dtype('int64'))
        )
        self.assertTrue('other_data' in as_numeric.columns.tolist())
        self.assertFalse('categorical' in as_numeric.columns.tolist())

        expected_crosswalk = pd.DataFrame({
                                 'categorical_key' : [0,1],
                                 'categorical'     : ['A','B']
                             }).ix[:,[1,0]]
        from_disk = pd.read_hdf('../output/categorical_lookup.h5', key = 'categorical')
        self.assertTrue(expected_crosswalk.equals(from_disk))

        as_numeric = ebt.build_numeric_key(
                         categorical_data,
                         'categorical',
                         saveing = '../output/categorical_lookup.h5',
                         compression = 9,
                         complib = 'blosc',
                         newname = 'categorical_code'
                     )
        self.assertTrue('categorical_code' in as_numeric.columns.tolist())
        os.unlink('../output/categorical_lookup.h5')

        as_numeric = ebt.build_numeric_key(
                         categorical_data,
                         'categorical'
                     )
        self.assertTrue('categorical_key' in as_numeric.columns.tolist())
        self.assertFalse('categorical' in as_numeric.columns.tolist())
        self.assertFalse(os.path.exists('../output/categorical_lookup.h5'))

    def test_drop_all_duplicates(self):
        duplicated_data = self.duplicated_data
        
        de_duplicated = ebt.drop_all_duplicates(duplicated_data.copy(), on = 'var2')
        expected_output = duplicated_data.query('(var2 != 1) & (var2 != 9)')
        self.assertTrue(de_duplicated.equals(expected_output))

        # removing all duplicates on a column with no duplicates should produce original
        de_duplicated = ebt.drop_all_duplicates(duplicated_data.copy(), on = 'var1')
        self.assertTrue(de_duplicated.equals(duplicated_data))

    def test_drop_duplicates(self):
        duplicated_data = self.duplicated_data
        
        unique_rows = ebt.drop_duplicates(duplicated_data['var2'])
        self.assertTrue(unique_rows.tolist() == [1,2,3,4,5,6,9])

        unique_rows = ebt.drop_duplicates(duplicated_data)
        self.assertTrue(duplicated_data.equals(unique_rows))

if __name__ == '__main__':
    unittest.main()