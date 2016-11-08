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

    def test_nofile(self):
        testcat.unzipFiles()
        l = os.listdir('./test_out')
        self.assertEqual(l, [])

    def test_afile(self):
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

    def test_twofile(self):

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

    def tearDown(self):
        paths = ['./test_data', './test_temp', './test_out']
        for path in paths:
            shutil.rmtree(path, ignore_errors = True)


if __name__ == '__main__':
    unittest.main()
