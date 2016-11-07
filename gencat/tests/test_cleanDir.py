import unittest
import os
import shutil
from gencat import gencat


class test_cleanDir(unittest.TestCase):
    
    def setUp(self):
        paths = ['./test_data', './test_temp', './test_out']
        for path in paths:
            try:
                os.makedirs(path)
            except:
                shutil.rmtree(path, ignore_errors = True)
                os.makedirs(path)

    def test_base(self):
        class TestCat(gencat.gencat):
            def makeZipDict(self):
                pass
            def makeConcatDict(self):
                pass
        testcat = TestCat('./test_data', './test_temp', './out_temp')

        testcat.cleanDir('./test')
        self.assertTrue(os.path.isdir('./test'))
    
    def test_strange(self):
        class TestCat(gencat.gencat):
            def makeZipDict(self):
                pass
            def makeConcatDict(self):
                pass
        testcat = TestCat('./test_data', './test_temp', './out_temp')
        
        testcat.cleanDir('./test', new_dir = 'gibberish')
        self.assertTrue(os.path.isdir('./test'))
    
    def test_nonew(self):
        class TestCat(gencat.gencat):
            def makeZipDict(self):
                pass
            def makeConcatDict(self):
                pass
        testcat = TestCat('./test_data', './test_temp', './out_temp')
        
        testcat.cleanDir('./test', new_dir = False)
        self.assertFalse(os.path.isdir('./test'))
    
    def test_deep(self):
        class TestCat(gencat.gencat):
            def makeZipDict(self):
                pass
            def makeConcatDict(self):
                pass
        testcat = TestCat('./test_data', './test_temp', './out_temp')

        testcat.cleanDir('./a/deep/test/dir')
        self.assertTrue(os.path.isdir('./a/deep/test/dir'))
        shutil.rmtree('./a')
    
    def tearDown(self):
        paths = ['./test_data', './test_temp', './test_out']
        for path in paths:
            shutil.rmtree(path, ignore_errors = True)

if __name__ == '__main__':
    unittest.main()