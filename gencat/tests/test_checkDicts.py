import unittest
import os
import shutil
import zipfile
import sys

sys.path.append('../')
from gencat import gencat

class test_checkDicts(unittest.TestCase): 
    
    def setUp(self):
        paths = ['./test_data', './test_temp', './test_out']
        for path in paths:
            try:
                os.makedirs(path)
            except:
                shutil.rmtree(path, ignore_errors = True)
                os.makedirs(path)
    
    def test_default(self):
        '''
        Test that no exception is raised when dictionaries exist and all keys are tuples.
        '''
        class TestCat(gencat.gencat):
            def makeZipDict(self):
                self.zip_dict = {'a': ('tuple1', )}
            def makeConcatDict(self):
                self.concat_dict = {'b': ('tuple2', )}
        testcat = TestCat('./test_data', './test_temp', './test_out')
        testcat.makeConcatDict()
        testcat.makeZipDict()
        
        testcat.checkDicts()
    
    def test_notAllTuple(self):
        '''
        Test that TypeError is raised when dictionaries exist but do not have tuple-valued keys.
        '''
        class TestCat(gencat.gencat):
            def makeZipDict(self):
                self.zip_dict = {'a': 'not_a_tuple_tuple1'}
            def makeConcatDict(self):
                self.concat_dict = {'b', ('tuple2', )}
        testcat = TestCat('./test_data', './test_temp', './test_out')
        testcat.makeConcatDict()
        testcat.makeZipDict()
        
        with self.assertRaises(TypeError):
            testcat.checkDicts()

    def test_notAllDicts(self):
        '''
        Test that Exception is raised when a dictionary does not exist.
        '''
        class TestCat(gencat.gencat):
            def makeZipDict(self):
                self.zip_dict = {}
            def makeConcatDict(self):
                self.concat_dict = {'b', ('tuple2', )}
        testcat = TestCat('./test_data', './test_temp', './test_out')
        testcat.makeConcatDict()
        testcat.makeZipDict()
        
        with self.assertRaises(Exception):
            testcat.checkDicts()
    
    def tearDown(self):
        paths = ['./test_data', './test_temp', './test_out']
        for path in paths:
            shutil.rmtree(path, ignore_errors = True)
    

if __name__ == '__main__':
    unittest.main()

    