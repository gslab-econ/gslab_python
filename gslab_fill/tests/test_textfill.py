#! /usr/bin/env python

import unittest
import sys
import os
import re
import types
import HTMLParser

sys.path.append('..')
from textfill import textfill, read_text, remove_trailing_leading_blanklines
from nostderrout import nostderrout

class testTextfill(unittest.TestCase):

    def testInput(self):
        with nostderrout():
            message = textfill(input    = './log/stata_output_for_textfill/legal.log', 
                               template = './input/textfill_template.lyx', 
                               output   = './input/textfill_template_filled.lyx')
        self.assertIn('filled successfully', message)
        log_remove_string = '. insert_tag'
        log = './log/stata_output_for_textfill/legal.log'
        self.checkLogInLyX(log, log_remove_string, "textfill_")
        
    def testAlternativePrefix(self):
        with nostderrout():
            message = textfill(input    = './log/stata_output_for_textfill/alternative_prefix.log', 
                               template = './input/textfill_template.lyx', 
                               output   = './input/textfill_template_filled.lyx', 
                               prefix   = 'prefix')
        self.assertIn('filled successfully', message)
        log_remove_string = '. insert_tag'
        log = './log/stata_output_for_textfill/alternative_prefix.log'
        self.checkLogInLyX(log, log_remove_string, "prefix_")
        
    def testRemoveEchoes(self):
        with nostderrout():
            textfill(input    = './log/stata_output_for_textfill/legal.log',
                     template = './input/textfill_template.lyx',
                     output   = './input/textfill_template_filled.lyx',
                     remove_echoes = True)
        log_remove_string = '. '
        log = './log/stata_output_for_textfill/legal.log'
        self.checkLogInLyX(log, log_remove_string, "textfill_")
    
    def checkLogInLyX(self, log, log_remove_string, prefix):
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
    
    def testTagsDontMatch(self):
        with nostderrout():
            error = textfill(input    = './log/stata_output_for_textfill/tags_dont_match.log', 
                             template = './input/textfill_template.lyx', 
                             output   = './input/textfill_template_filled.lyx')
        self.assertIn('ValueError', error)
        
    def testTagsNotClosed(self):
        with nostderrout():   
            error = textfill(input    = './log/stata_output_for_textfill/tags_not_closed.log', 
                             template = './input/textfill_template.lyx', 
                             output   = './input/textfill_template_filled.lyx')
        self.assertIn('HTMLParseError', error)
        
    def testTagsIncorrectlySpecified(self):
        with nostderrout():
            textfill(input    = './log/stata_output_for_textfill/tags_incorrectly_named.log',
                     template = './input/textfill_template.lyx',
                     output   = './input/textfill_template_filled.lyx')
        
        log_remove_string = '. insert_tag'

        with self.assertRaises(AssertionError):
            log = './log/stata_output_for_textfill/tags_incorrectly_named.log'
            self.checkLogInLyX(log, log_remove_string, "textfill_")
        
    def testIllegalSyntax(self):
        # missing arguments
        with nostderrout(): 
            error = textfill(input    = './log/stata_output_for_textfill/legal.log', 
                             template = './input/textfill_template.lyx')
        self.assertIn('KeyError', error)                      
                          
        # non-existent input 1
        with nostderrout():
            error = textfill(input    = './log/stata_output_for_textfill/fake_file.log', 
                             template = './input/textfill_template.lyx', 
                             output   =  './input/textfill_template_filled.lyx')

        self.assertIn('IOError', error)
        
        # non-existent input 2
        with nostderrout():
            error = textfill(input    = './log/stata.log ./log/stata_output_for_textfill/fake_file.log', 
                             template = './input/textfill_template.lyx', 
                             output   = './input/textfill_template_filled.lyx')

        self.assertIn('IOError', error)
        
    def testArgumentOrder(self):
        with nostderrout():
            message = textfill(input    = './log/stata_output_for_textfill/legal.log', 
                               output   = './input/textfill_template_filled.lyx', 
                               template = './input/textfill_template.lyx')

        self.assertIn('filled successfully', message)                                
            
        with nostderrout():            
            message = textfill(template = './input/textfill_template.lyx',
                               output   = './input/textfill_template_filled.lyx',
                               input    = './log/stata_output_for_textfill/legal.log')

        self.assertIn('filled successfully', message)
        
        
if __name__ == '__main__':
    os.getcwd()
    unittest.main()
