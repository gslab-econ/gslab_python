import unittest
import os
import shutil
import zipfile
from gencat import gencat

class test_tupleVals(unittest.TestCase): 
    
    def setUp(self):
        paths = ['./test_data', './test_temp', './test_out']
        for path in paths:
            try:
                os.makedirs(path)
            except:
                shutil.rmtree(path, ignore_errors = True)
                os.makedirs(path)
    
    def test_allTuple(self):
        class TestCat(gencat.gencat):
            def makeZipDict(self):
                self.zip_dict = {'a': ('tuple1', )}
            def makeConcatDict(self):
                self.concat_dict = {'b': ('tuple1', )}
        testcat = TestCat('./test_data', './test_temp', './test_out')
        testcat.makeConcatDict()
        testcat.makeZipDict()
        
        testcat.tupleVals()
    
    def test_notallTuple(self):
        class TestCat(gencat.gencat):
            def makeZipDict(self):
                self.zip_dict = {'a': 'not_a_tuple_tuple1'}
            def makeConcatDict(self):
                self.concat_dict = {'b', ('tuple2', )}
        testcat = TestCat('./test_data', './test_temp', './test_out')
        testcat.makeConcatDict()
        testcat.makeZipDict()
        
        with self.assertRaises(TypeError):
            testcat.tupleVals()
    
    def tearDown(self):
        paths = ['./test_data', './test_temp', './test_out']
        for path in paths:
            shutil.rmtree(path, ignore_errors = True)
    

if __name__ == '__main__':
    unittest.main()

    