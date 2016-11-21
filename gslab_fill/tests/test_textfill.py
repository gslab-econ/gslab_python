#! /usr/bin/env python
import unittest
import sys
import os
import re
import types
import HTMLParser
import shutil

# Ensure that Python can find and load the GSLab libraries
os.chdir(os.path.dirname(os.path.realpath(__file__)))
sys.path.append('../..')

from gslab_fill.textfill import (textfill, read_text, 
                                 remove_trailing_leading_blanklines)
from gslab_make.tests import nostderrout

class testTextfill(unittest.TestCase):

    def setUp(self):
        if not os.path.exists('./build/'):
            os.mkdir('./build/')

    def test_input(self):
        with nostderrout():
            message = textfill(input    = './input/legal.log', 
                               template = './input/textfill_template.lyx', 
                               output   = './build/textfill_template_filled.lyx')
        self.assertIn('filled successfully', message)
        log_remove_string = '. insert_tag'
        log = './input/legal.log'
        self.check_log_in_LyX(log, log_remove_string, "textfill_")
        
    def test_alternative_prefix(self):
        with nostderrout():
            message = textfill(input    = './input/alternative_prefix.log', 
                               template = './input/textfill_template.lyx', 
                               output   = './build/textfill_template_filled.lyx', 
                               prefix   = 'prefix')
        self.assertIn('filled successfully', message)
        log_remove_string = '. insert_tag'
        log = './input/alternative_prefix.log'
        self.check_log_in_LyX(log, log_remove_string, "prefix_")
        
    def test_remove_echoes(self):
        with nostderrout():
            textfill(input    = './input/legal.log',
                     template = './input/textfill_template.lyx',
                     output   = './build/textfill_template_filled.lyx',
                     remove_echoes = True)
        log_remove_string = '. '
        log = './input/legal.log'
        self.check_log_in_LyX(log, log_remove_string, "textfill_")
    
    def check_log_in_LyX(self, log, log_remove_string, prefix):
        raw_lyx = open("./input/textfill_template_filled.lyx", 'rU').readlines()
        raw_lyx = [re.sub(r'\\end_layout\n$', '', x) for x in raw_lyx]
        
        text = read_text(log, prefix)
        self.assertEqual( len(text.results),2 )
        self.assertEqual(text.results.keys(), ['test_small', 'test_long'])
        
        for key in text.results:
            raw_table = text.results[key].split('\n')
            raw_table = filter(lambda x: not x.startswith(log_remove_string), raw_table)
            raw_table = remove_trailing_leading_blanklines(raw_table)
            for n in range( len(raw_table) ):
                self.assertIn(raw_table[n], raw_lyx)
    
    def test_tags_dont_match(self):
        with nostderrout():
            error = textfill(input    = './input/tags_dont_match.log', 
                             template = './input/textfill_template.lyx', 
                             output   = './build/textfill_template_filled.lyx')
        self.assertIn('ValueError', error)
        
    def test_tags_not_closed(self):
        with nostderrout():   
            error = textfill(input    = './input/tags_not_closed.log', 
                             template = './input/textfill_template.lyx', 
                             output   = './build/textfill_template_filled.lyx')
        self.assertIn('HTMLParseError', error)
        
    def test_tags_incorrectly_specified(self):
        with nostderrout():
            textfill(input    = './input/tags_incorrectly_named.log',
                     template = './input/textfill_template.lyx',
                     output   = './build/textfill_template_filled.lyx')
        
        log_remove_string = '. insert_tag'

        with self.assertRaises(AssertionError):
            log = './input/tags_incorrectly_named.log'
            self.check_log_in_LyX(log, log_remove_string, "textfill_")
        
    def test_illegal_syntax(self):
        # missing arguments
        with nostderrout(): 
            error = textfill(input    = './input/legal.log', 
                             template = './input/textfill_template.lyx')
        self.assertIn('KeyError', error)                      
                          
        # non-existent input 1
        with nostderrout():
            error = textfill(input    = './input/fake_file.log', 
                             template = './input/textfill_template.lyx', 
                             output   =  './build/textfill_template_filled.lyx')

        self.assertIn('IOError', error)
        
        # non-existent input 2
        with nostderrout():
            error = textfill(input    = './log/stata.log ./input/fake_file.log', 
                             template = './input/textfill_template.lyx', 
                             output   = './build/textfill_template_filled.lyx')

        self.assertIn('IOError', error)
        
    def test_argument_order(self):
        with nostderrout():
            message = textfill(input    = './input/legal.log', 
                               output   = './input/textfill_template_filled.lyx', 
                               template = './input/textfill_template.lyx')

        self.assertIn('filled successfully', message)                                
            
        with nostderrout():            
            message = textfill(template = './input/textfill_template.lyx',
                               output   = './build/textfill_template_filled.lyx',
                               input    = './input/legal.log')

        self.assertIn('filled successfully', message)
        
    def tearDown(self):
        if os.path.exists('./build/'):
            shutil.rmtree('./build/')


if __name__ == '__main__':
    os.getcwd()
    unittest.main()
