import unittest
import os
import shutil
import zipfile
from gencat import gencat


class test_writeDict(unittest.TestCase):
    
    def setUp(self):
        paths = ['./test_data', './test_temp', './test_out']
        for path in paths:
            try:
                os.makedirs(path)
            except:
                shutil.rmtree(path, ignore_errors = True)
                os.makedirs(path)

    def test_nofile(self):
        class TestCat(gencat.gencat):

    def tearDown(self):
        paths = ['./test_data', './test_temp', './test_out']
        for path in paths:
            shutil.rmtree(path, ignore_errors = True)