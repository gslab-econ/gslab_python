import unittest
import os
import shutil
from gencat import gencat


class TestCat(gencat.gencat):
    def makeZipDict(self):
        pass

    def makeConcatDict(self):
        pass


testcat = TestCat('./test_data', './test_temp', './out_temp')


class test_cleanDir(unittest.TestCase):
    
    def setUp(self):
        paths = ['./test_data', './test_temp', './test_out']
        for path in paths:
            try:
                os.makedirs(path)
            except:
                shutil.rmtree(path, ignore_errors = True)
                os.makedirs(path)

    def test_cleandir(self):
        '''
        Test that files in directory are cleared
        '''
        with open('test_data/test_file', 'wb') as f:
            f.write('test')
        testcat.cleanDir('./test_data')
        self.assertFalse(os.listdir('./test_data'))
    
    def test_makedir(self):
        '''
        Test that method creates a new directory.
        '''
        try:
            shutil.rmtree('./test')
        except:
            pass
        testcat.cleanDir('./test')
        self.assertTrue(os.path.isdir('./test'))
    
    def test_strange(self):
        '''
        Test that new_dir flag does not affect output unless False is entered
        '''
        testcat.cleanDir('./test', new_dir = 'gibberish1!')
        self.assertTrue(os.path.isdir('./test'))
    
    def test_nonew(self):
        '''
        Test that a new directory is not created if the new_dir flag is False
        '''
        testcat.cleanDir('./test', new_dir = False)
        self.assertFalse(os.path.isdir('./test'))
    
    def test_deeppath(self):
        '''
        Test that the cleanDir method functions on subdirectories
        '''
        testcat.cleanDir('./a/deep/test/dir')
        self.assertTrue(os.path.isdir('./a/deep/test/dir'))
        shutil.rmtree('./a')
    
    def tearDown(self):
        paths = ['./test_data', './test_temp', './test_out']
        for path in paths:
            shutil.rmtree(path, ignore_errors = True)


if __name__ == '__main__':
    unittest.main()