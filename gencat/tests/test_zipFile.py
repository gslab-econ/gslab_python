import unittest
import os
import shutil
import zipfile
from gencat import gencat

class TestCat(gencat.gencat):
    def makeZipDict(self):
        pass

    def makeConcatDict(self):
        pass

class test_zipFiles(unittest.TestCase):
    
    def setUp(self):
        paths = ['./test_data', './test_temp', './test_out']
        for path in paths:
            try:
                os.makedirs(path)
            except:
                shutil.rmtree(path, ignore_errors = True)
                os.makedirs(path)
        for FILE in ['./test_data/file1.txt', './test_data/file2.txt']:
            with open(FILE, 'wb') as f:
                f.write('''THIS IS A TEST FILE.\n''')


    def test_twofile(self):
        testcat = TestCat('./test_data', './test_temp', './test_out')
        testcat.zip_dict = {} 
        testcat.zip_dict['zip1'] = ('concat1', )
        testcat.concat_dict = {}
        testcat.concat_dict['concat1'] = ('./test_data/file1.txt', ) + ('./test_data/file2.txt', )
        
        testcat.zipFiles()

        self.assertTrue(os.path.isfile('./test_out/zip1.zip'))
        self.assertTrue(zipfile.is_zipfile('./test_out/zip1.zip'))
        
        with zipfile.ZipFile('./test_out/zip1.zip', 'r') as zf:
            zf.extractall('./test_out/')

        with open('./test_out/zip1/concat1.txt', 'rU') as f:
            text = f.read()
        
        test_text = '\nNEWFILE\nFILENAME: file1.txt\n\nTHIS IS A TEST FILE.' + \
                    '\n\nNEWFILE\nFILENAME: file2.txt\n\nTHIS IS A TEST FILE.\n'
        self.assertEqual(text, test_text)

    def test_onefile(self):
        testcat = TestCat('./test_data', './test_temp', './test_out')
        testcat.zip_dict = {} 
        testcat.zip_dict['zip1'] = ('concat1', )
        testcat.concat_dict = {}
        testcat.concat_dict['concat1'] = ('./test_data/file1.txt', )
        
        testcat.zipFiles()

        self.assertTrue(os.path.isfile('./test_out/zip1.zip'))
        self.assertTrue(zipfile.is_zipfile('./test_out/zip1.zip'))
        
        with zipfile.ZipFile('./test_out/zip1.zip', 'r') as zf:
            zf.extractall('./test_out/')

        with open('./test_out/zip1/concat1.txt', 'rU') as f:
            text = f.read()

        self.assertEqual(text, '\nNEWFILE\nFILENAME: file1.txt\n\nTHIS IS A TEST FILE.\n')

    def test_twozips(self):
        testcat = TestCat('./test_data', './test_temp', './test_out')
        testcat.zip_dict = {} 
        testcat.zip_dict['zip1'] = ('concat1', )
        testcat.zip_dict['zip2'] = ('concat2', )
        testcat.concat_dict = {}
        testcat.concat_dict['concat1'] = ('./test_data/file1.txt', )
        testcat.concat_dict['concat2'] = ('./test_data/file2.txt', )
        
        testcat.zipFiles()

        self.assertTrue(os.path.isfile('./test_out/zip1.zip'))
        self.assertTrue(os.path.isfile('./test_out/zip2.zip'))
        self.assertTrue(zipfile.is_zipfile('./test_out/zip1.zip'))
        self.assertTrue(zipfile.is_zipfile('./test_out/zip2.zip'))
        
        with zipfile.ZipFile('./test_out/zip1.zip', 'r') as zf:
            zf.extractall('./test_out/')
        with zipfile.ZipFile('./test_out/zip2.zip', 'r') as zf:
            zf.extractall('./test_out/')

        with open('./test_out/zip1/concat1.txt', 'rU') as f:
            text1 = f.read()
        with open('./test_out/zip2/concat2.txt', 'rU') as f:
            text2 = f.read()

        self.assertEqual(text1, '\nNEWFILE\nFILENAME: file1.txt\n\nTHIS IS A TEST FILE.\n')
        self.assertEqual(text2, '\nNEWFILE\nFILENAME: file2.txt\n\nTHIS IS A TEST FILE.\n')

    def test_twoconcats_onezip(self):
        testcat = TestCat('./test_data', './test_temp', './test_out')
        testcat.zip_dict = {} 
        testcat.zip_dict['zip1'] = ('concat1', ) + ('concat2', )
        testcat.concat_dict = {}
        testcat.concat_dict['concat1'] = ('./test_data/file1.txt', )
        testcat.concat_dict['concat2'] = ('./test_data/file2.txt', )
        
        testcat.zipFiles()

        self.assertTrue(os.path.isfile('./test_out/zip1.zip'))
        self.assertTrue(zipfile.is_zipfile('./test_out/zip1.zip'))
        
        with zipfile.ZipFile('./test_out/zip1.zip', 'r') as zf:
            zf.extractall('./test_out/')

        with open('./test_out/zip1/concat1.txt', 'rU') as f:
            text1 = f.read()
        with open('./test_out/zip1/concat2.txt', 'rU') as f:
            text2 = f.read()

        self.assertEqual(text1, '\nNEWFILE\nFILENAME: file1.txt\n\nTHIS IS A TEST FILE.\n')
        self.assertEqual(text2, '\nNEWFILE\nFILENAME: file2.txt\n\nTHIS IS A TEST FILE.\n')

    def tearDown(self):
        paths = ['./test_data', './test_temp', './test_out']
        for path in paths:
            shutil.rmtree(path, ignore_errors = True)


if __name__ == '__main__':
    unittest.main()
