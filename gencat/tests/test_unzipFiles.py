import unittest
import os
import shutil
import zipfile
import sys

# Ensure the script is run from its own directory 
os.chdir(os.path.dirname(os.path.realpath(__file__)))

sys.path.append('../')
from gencat import gencat

class TestCat(gencat):
    def makeZipDict(self):
        pass
    def makeConcatDict(self):
        pass


testcat = TestCat('./test_data', './test_temp', './out_temp')


class test_unzipFiles(unittest.TestCase):

    def setUp(self):
        paths = ['./test_data', './test_temp', './test_out']
        for path in paths:
            try:
                os.makedirs(path)
            except:
                shutil.rmtree(path, ignore_errors = True)
                os.makedirs(path)

    def test_noFile(self):
        '''
        Test that an empty list is returned when there is no file in the input directory.
        '''
        testcat.unzipFiles()
        l = os.listdir('./test_out')
        self.assertEqual(l, [])

    def test_noZipFile(self):
        '''
        Test that an empty list is returned when there is no zip file in the input directory.
        '''
        with open('./test_data/test.txt', 'wb') as f:
            f.write('test')

        testcat.unzipFiles()
        l = os.listdir('./test_out')
        self.assertEqual(l, [])
    
    def test_blankZipFile(self):
        '''
        Test that nothing is returned by a zip file without content.
        '''
        # Set up
        inzip = zipfile.ZipFile('test_temp/test_zip.zip', 'w', zipfile.ZIP_DEFLATED, True)
        inzip.close()

        # Test Zipping
        self.assertTrue(os.path.isfile('test_temp/test_zip.zip'))
        self.assertTrue(zipfile.is_zipfile('test_temp/test_zip.zip'))

        # Test Unzipping
        testcat.unzipFiles()
        outzip = zipfile.ZipFile('test_temp/test_zip.zip')
        outzip.extractall('test_temp')
        
        # Test Content
        self.assertEqual(os.listdir('test_temp/'), ['test_zip.zip'])

    def test_aZipFile(self):
        '''
        Test that a single file in a single zip file is unzipped and that content is preserved.
        '''
        # Set up
        inzip = zipfile.ZipFile('test_temp/test_zip.zip', 'w', zipfile.ZIP_DEFLATED, True)
        with open('test_data/test_text.txt', 'wb') as f:
            f.write('test\ntest')
        inzip.write('test_data/test_text.txt')
        inzip.close()

        # Test Zipping
        self.assertTrue(os.path.isfile('test_temp/test_zip.zip'))
        self.assertTrue(zipfile.is_zipfile('test_temp/test_zip.zip'))

        # Test Unzipping
        testcat.unzipFiles()
        outzip = zipfile.ZipFile('test_temp/test_zip.zip')
        outzip.extractall('test_temp')
        self.assertTrue(os.path.isfile('test_temp/test_data/test_text.txt'))

        # Test Content
        with open('test_temp/test_data/test_text.txt', 'rU') as f:
            lines = f.readlines()

        count = 0
        for line in lines:
            line = line.strip()
            self.assertEqual(line, 'test')
            count = count + 1
        self.assertEqual(count, 2)

    def test_twoFile(self):
        '''
        Test that a single zip file containing two text files is unzipped and that content is preserved.
        '''
        # Set up
        files = ['test1', 'test2']
        inzip = zipfile.ZipFile('test_temp/test_zip.zip', 'w', zipfile.ZIP_DEFLATED, True)
        for f in files:
            with open('test_data/%s_text.txt' % f, 'wb') as fi:
                fi.write('%s\n%s' % (f, f))
            inzip.write('test_data/%s_text.txt' % f)
        inzip.close()

        # Test Zipping
        self.assertTrue(os.path.isfile('test_temp/test_zip.zip'))
        self.assertTrue(zipfile.is_zipfile('test_temp/test_zip.zip'))

        # Test Unzipping
        testcat.unzipFiles()
        outzip = zipfile.ZipFile('test_temp/test_zip.zip')
        outzip.extractall('test_temp')

        for f in files:
            self.assertTrue(os.path.isfile('test_temp/test_data/%s_text.txt' % f))

        # Test Content
        for f in files:
            with open('test_temp/test_data/%s_text.txt' % f, 'rU') as fi:
                lines = fi.readlines()
            
            count = 0
            for line in lines:
                line = line.strip()
                self.assertEqual(line, f)
                count = count + 1
            self.assertEqual(count, 2)

    def test_twoZipFile(self):
        '''
        Test that two zip files containing one text file apiece are unzipped and that content is preserved.
        '''
        # Set up
        files = ['test1', 'test2']
        inzip1 = zipfile.ZipFile('test_temp/test1_zip.zip', 'w', zipfile.ZIP_DEFLATED, True)
        inzip2 = zipfile.ZipFile('test_temp/test2_zip.zip', 'w', zipfile.ZIP_DEFLATED, True)
        for f in files:
            with open('test_data/%s_text.txt' % f, 'wb') as fi:
                fi.write('%s\n%s' % (f, f))
            if f == 'test1':
                inzip1.write('test_data/%s_text.txt' % f)
                inzip1.close()
            elif f == 'test2':
                inzip2.write('test_data/%s_text.txt' % f)
                inzip2.close()

        # Test Zipping
        for zf in ['test1_zip.zip', 'test2_zip.zip']:
            self.assertTrue(os.path.isfile('test_temp/%s' % zf))
            self.assertTrue(zipfile.is_zipfile('test_temp/%s' % zf))

        # Test Unzipping
        testcat.unzipFiles()
        outzip1 = zipfile.ZipFile('test_temp/test1_zip.zip')
        outzip1.extractall('test_temp')
        outzip2 = zipfile.ZipFile('test_temp/test2_zip.zip')
        outzip2.extractall('test_temp')

        for f in files:
            self.assertTrue(os.path.isfile('test_temp/test_data/%s_text.txt' % f))

        # Test Content
        for f in files:
            with open('test_temp/test_data/%s_text.txt' % f, 'rU') as fi:
                lines = fi.readlines()
            
            count = 0
            for line in lines:
                line = line.strip()
                self.assertEqual(line, f)
                count = count + 1
            self.assertEqual(count, 2)

    def tearDown(self):
        paths = ['./test_data', './test_temp', './test_out']
        for path in paths:
            shutil.rmtree(path, ignore_errors = True)


if __name__ == '__main__':
    unittest.main()
