import unittest
import sys
import pandas as pd
import numpy as np
import os

sys.path.append('..')

from SaveData import SaveData

class TestSaveData(unittest.TestCase):
    
    def test_wrong_extension(self):
        df = pd.DataFrame({'a' : [4,3,6], 'b': [4,5,6], 'c': [1,2,3]})
        with self.assertRaises(ValueError):
            SaveData(df, ['a'], 'dfs.pdf')
            
    def test_wrong_keytype(self):
        df = pd.DataFrame({'a' : [4,3,6], 'b': [4,5,6], 'c': [1,2,3]})
        with self.assertRaises(TypeError):
            SaveData(df, 'a', 'dfs.csv')        
            
    def test_missingkeys(self):
        df = pd.DataFrame({'a' : [4,3,6], 'b': [4,np.nan,6], 'c': [1,2,3]})
        with self.assertRaises(ValueError):
            SaveData(df, ['b'], 'dfs.csv')

    def test_duplicate_keys(self):
        df = pd.DataFrame({'a' : [3,3,6], 'b': [4,5,6], 'c': [1,2,3]})
        with self.assertRaises(ValueError):
            SaveData(df, ['a'], 'dfs.csv')

    def test_saves_desired_file(self):
        df = pd.DataFrame({'a' : [3,3,6], 'b': [4,5,6], 'c': [1,2,3]})
        SaveData(df, ['b'], 'df.csv')
        exists = os.path.isfile('df.csv')
        self.assertEqual(exists, True)
        os.remove('df.csv')
                
    def test_saves_with_log(self):    
        df = pd.DataFrame({'a' : [3,3,6], 'b': [4,5,6], 'c': [1,2,3]})
        SaveData(df, ['b'], 'df.csv', 'df.log')
        exists = os.path.isfile('df.log')
        self.assertEqual(exists, True)
        os.remove('df.log')
        os.remove('df.csv')
        
    def test_saves_when_append_given(self):    
        df = pd.DataFrame({'a' : [3,3,6], 'b': [4,5,6], 'c': [1,2,3]})
        SaveData(df, ['b'], 'df.csv', 'df.log')
        SaveData(df, ['c'], 'df.csv', 'df.log', append = True)
        exists = os.path.isfile('df.log')
        self.assertEqual(exists, True)
        os.remove('df.log')
        os.remove('df.csv')
        
    def test_saves_when_sort_is_false(self):    
        df = pd.DataFrame({'a' : [3,3,6], 'b': [4,5,6], 'c': [1,2,3]})
        SaveData(df, ['c'], 'df.csv', 'df.log', sortbykey = False)
        exists = os.path.isfile('df.csv')
        self.assertEqual(exists, True)
        os.remove('df.log')
        os.remove('df.csv')    
        
if __name__ == '__main__':
    unittest.main()
