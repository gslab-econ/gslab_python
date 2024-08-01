import unittest
import sys
import pandas as pd
import numpy as np
import os
from pathlib import Path

sys.path.append('..')

from SaveData import SaveData

pd.set_option('future.no_silent_downcasting', True)

class TestSaveData(unittest.TestCase):
    
    def test_wrong_extension(self):
        df = pd.read_csv('data/data.csv')
        with self.assertRaises(ValueError):
            SaveData(df, ['id'], 'dfs.pdf')

    def test_wrong_keytype(self):
        df = pd.read_csv('data/data.csv')
        with self.assertRaises(TypeError):
            SaveData(df, 'id', 'dfs.csv')        
            
    def test_missingkeys(self):
        df = pd.read_csv('data/data.csv')
        with self.assertRaises(ValueError):
            SaveData(df, ['num'], 'dfs.csv')

    def test_duplicate_keys(self):
        df = pd.read_csv('data/data.csv')
        with self.assertRaises(ValueError):
            SaveData(df, ['partid1'], 'dfs.csv')

    def test_multiple_keys(self):
        df = pd.read_csv('data/data.csv')
        SaveData(df, ['id', 'partid1','partid2'], 'df.csv')
        df_saved = pd.read_csv('df.csv')
        self.assertEqual(True, df.compare(df_saved).shape==(0,0))
        os.remove('df.csv')

    def test_saves_desired_file_dta(self):
        df = pd.read_csv('data/data.csv')
        SaveData(df, ['id'], 'df.dta')
        df_saved = pd.read_stata('df.dta')
        self.assertEqual(True, df.compare(df_saved).shape==(0,0))
        os.remove('df.dta')
                
    def test_saves_desired_file_without_log(self):
        df = pd.read_csv('data/data.csv')
        SaveData(df, ['id'], 'df.csv')
        exists = os.path.isfile('df.csv')
        df_saved = pd.read_csv('df.csv')
        self.assertEqual(True, df.compare(df_saved).shape==(0,0))
        os.remove('df.csv')
                
    def test_saves_with_log(self):    
        df = pd.read_csv('data/data.csv')
        SaveData(df, ['id'], 'df.csv', 'df.log')
        exists = os.path.isfile('df.log')
        self.assertEqual(exists, True)
        os.remove('df.log')
        os.remove('df.csv')
        
    def test_saves_when_append_given(self):    
        df = pd.read_csv('data/data.csv')
        SaveData(df, ['id'], 'df.csv')
        SaveData(df, ['id'], 'df.csv', 'df.log', append = True)
        exists = os.path.isfile('df.log')
        self.assertEqual(exists, True)
        os.remove('df.log')
        os.remove('df.csv')
        
    def test_saves_when_sort_is_false(self):    
        df = pd.read_csv('data/data.csv')
        SaveData(df, ['id'], 'df.csv', 'df.log', sortbykey = False)
        exists = os.path.isfile('df.csv')
        self.assertEqual(exists, True)
        os.remove('df.log')
        os.remove('df.csv')    

    def test_saves_with_path(self):  
        indir = Path('data/data.csv')
        outdir_csv = Path('data.csv')
        outdir_log = Path('data.log')
        df = pd.read_csv(indir)
        SaveData(df, ['id'], outdir_csv, outdir_log)
        exists = os.path.isfile(str(outdir_log))
        self.assertEqual(exists, True)
        os.remove(str(outdir_csv))
        os.remove(str(outdir_log))
        
if __name__ == '__main__':
    unittest.main()
