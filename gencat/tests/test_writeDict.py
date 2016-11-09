import unittest
import os
import shutil
import zipfile
import sys

sys.path.append('../')
from gencat import gencat

class TestCat(gencat.gencat):
    def makeZipDict(self):
        pass
    def makeConcatDict(self):
        pass


testcat = TestCat('./test_data', './test_temp', './test_out')


class test_writeDict(unittest.TestCase):
    
    def setUp(self):
        paths = ['./test_data', './test_temp', './test_out']
        for path in paths:
            try:
                os.makedirs(path)
            except:
                shutil.rmtree(path, ignore_errors = True)
                os.makedirs(path)
    
    def test_onePath(self):
        '''
        Test that dictionary with one key paired to a single-element tuple value is printed as intended.
        '''
        d = {'path': ('path/to/file.txt', )}
        testcat.writeDict(d, 'test_dict.txt', 'path/to/')
        
        self.assertTrue(os.path.isfile('./test_out/test_dict.txt'))
        with open('./test_out/test_dict.txt', 'rU') as f:
            lines = f.readline().strip()
        self.assertEqual(lines, 'path|file.txt')
    
    def test_twopPath(self):
        '''
        Test that dictionary with two keys paired to single-element tuple values is printed as intended.
        '''
        d = {'path1': ('path/to/file1.txt', ), 'path2': ('path/to/file2.txt', )}
        testcat.writeDict(d, 'test_dict.txt', 'path/to/')
        
        self.assertTrue(os.path.isfile('./test_out/test_dict.txt'))
        with open('./test_out/test_dict.txt', 'rU') as f:
            lines = []
            for line in f:
                lines.append(line.strip())
        self.assertEqual(lines[0], 'path1|file1.txt')
        self.assertEqual(lines[1], 'path2|file2.txt')

    def test_twoFile(self):
        '''
        Test that dictionary with one key paired to two-element tuple value is printed as intended.
        '''
        d = {'path': ('path/to/file1.txt', 'path/to/file2.txt')}
        testcat.writeDict(d, 'test_dict.txt', 'path/to/')

        self.assertTrue(os.path.isfile('./test_out/test_dict.txt'))
        with open('./test_out/test_dict.txt', 'rU') as f:
            lines = f.readline().strip()
        self.assertEqual(lines, 'path|file1.txt|file2.txt')
    
    def test_noPath(self):
        '''
        Test that printed path is not modified when rel_path flag is blank.
        '''
        d = {'path': ('a/path/file.txt', )}
        testcat.writeDict(d, 'test_dict.txt', '')

        with open('./test_out/test_dict.txt', 'rU') as f:
            lines = f.readline()
        lines = lines.strip()
        self.assertEqual(lines, 'path|a/path/file.txt')
    
    def tearDown(self):
        paths = ['./test_data', './test_temp', './test_out']
        for path in paths:
            shutil.rmtree(path, ignore_errors = True)


if __name__ == '__main__':
    unittest.main()