import unittest
import os
import shutil
import zipfile
import sys

# Ensure that Python can find and load gencat.py
os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path.append('../')

from gencat import gencat


class TestCat(gencat):

    def makeZipDict(self):
        self.zip_dict = {} 
        self.zip_dict['zip1'] = ('concat1', )

    def makeConcatDict(self):
        self.concat_dict = {}
        self.concat_dict['concat1'] = ('./test_data/file1.txt', ) + ('./test_data/file2.txt', )


class test_main(unittest.TestCase):
    
    def setUp(self):
        paths = ['./test_data']
        for path in paths:
            try:
                os.makedirs(path)
            except:
                shutil.rmtree(path, ignore_errors = True)
                os.makedirs(path)
        count = 1
        for FILE in ['./test_data/file1.txt', './test_data/file2.txt']:
            with open(FILE, 'wb') as f:
                f.write('THIS IS TEST FILE %s.\n' % (count))
            count = count + 1

    def test_default(self):
        '''
        Test that the lines in main run in the intended order and produce predictable output 
        when given simple input. 
        '''
        testcat = TestCat('./test_data', './test_temp', './test_out')
        testcat.main()
        
        self.assertFalse(os.path.isdir('./test_temp'))
        self.assertTrue(os.path.isfile('./test_out/concatDict.txt'))
        self.assertTrue(os.path.isfile('./test_out/zipDict.txt'))
        self.assertTrue(os.path.isfile('./test_out/zip1.zip'))
        self.assertTrue(zipfile.is_zipfile('./test_out/zip1.zip'))
        with zipfile.ZipFile('./test_out/zip1.zip', 'r') as zf:
            zf.extractall('./test_out/')

        with open('./test_out/zip1/concat1.txt', 'rU') as f:
            text = f.read()

        test_text = '\nNEWFILE\nFILENAME: file1.txt\n\nTHIS IS TEST FILE 1.' + \
                    '\n\nNEWFILE\nFILENAME: file2.txt\n\nTHIS IS TEST FILE 2.\n'
        self.assertEqual(text, test_text)

    def tearDown(self):
        paths = ['./test_data', './test_out']
        for path in paths:
            shutil.rmtree(path, ignore_errors = True)


if __name__ == '__main__':
    unittest.main()

