#! /usr/bin/env python

import unittest
import sys
import os
import re
import decimal
from subprocess import check_call, CalledProcessError

# Ensure the script is run from its own directory 
os.chdir(os.path.dirname(os.path.realpath(__file__)))

sys.path.append('../..') 
from gslab_fill import tablefill
from gslab_make.tests import nostderrout

class testTablefill(unittest.TestCase):

    def testInput(self):
        with nostderrout():
            message = tablefill(input    = './input/tables_appendix.txt ./input/tables_appendix_two.txt', 
                                template = './input/tablefill_template.lyx', 
                                output   = './input/tablefill_template_filled.lyx')
        self.assertIn('filled successfully', message)                        
        tag_data = open('./input/tablefill_template.lyx', 'rU').readlines()
        filled_data = open('./input/tablefill_template_filled.lyx', 'rU').readlines()
        self.assertEqual(len(tag_data) + 13, len(filled_data))
        for n in range(len(tag_data)):
            self.tag_compare(tag_data[n], filled_data[n + 13]) 
    
    def tag_compare(self, tag_line, filled_line):
        if re.match('^.*#\d+#', tag_line) or re.match('^.*#\d+,#', tag_line):
            entry_tag = re.split('#', tag_line)[1]
            decimal_places = int(entry_tag.replace(',', ''))
            if decimal_places > 0:
                self.assertTrue(re.search('\.', filled_line))
                decimal_part = re.split('\.', filled_line)[1]
                non_decimal = re.compile(r'[^\d.]+')
                decimal_part = non_decimal.sub('', decimal_part)
                self.assertEqual(len(decimal_part), decimal_places)
            else:
                self.assertFalse(re.search('\.', filled_line))
            if re.match('^.*#\d+,#', tag_line):
                integer_part = re.split('\.', filled_line)[0]
                if len(integer_part) > 3:
                    self.assertEqual(integer_part[-4], ',')
   
    def testBreaksRoundingString(self):
        with nostderrout():
            error = tablefill(input    =  './input/tables_appendix.txt ./input/tables_appendix_two.txt', 
                              template =  './input/tablefill_template_breaks.lyx', 
                              output   =  './input/tablefill_template_filled.lyx')
        self.assertIn('InvalidOperation', error)
    
    def testIllegalSyntax(self):
        # missing arguments
        with nostderrout():

            error = tablefill(input   = './input/tables_appendix.txt ./input/tables_appendix_two.txt', 
                              template = './input/textfill_template.lyx')
        self.assertIn('KeyError', error)
                
        # non-existent input 1
        with nostderrout():
            error = tablefill(input    = './input/fake_file.txt ./input/tables_appendix_two.txt', 
                              template = './input/tablefill_template_breaks.lyx', 
                              output   = './input/tablefill_template_filled.lyx')
        self.assertIn('IOError', error)
        
        # non-existent input 2
        with nostderrout():
            error = tablefill(input    = './input/tables_appendix.txt ./input/fake_file.txt', 
                              template = './input/tablefill_template_breaks.lyx', 
                              output   = './input/tablefill_template_filled.lyx')
        self.assertIn('IOError', error)
        
    def testArgumentOrder(self):
        with nostderrout():
            message = tablefill(input    = './input/tables_appendix.txt ./input/tables_appendix_two.txt', 
                                output   = './input/tablefill_template_filled.lyx',
                                template = './input/tablefill_template.lyx')
        self.assertIn('filled successfully', message)
        filled_data_args1 = open('./input/tablefill_template_filled.lyx', 'rU').readlines()
        
        with nostderrout():
            message = tablefill(output   = './input/tablefill_template_filled.lyx', 
                                template = './input/tablefill_template.lyx', 
                                input    = './input/tables_appendix.txt ./input/tables_appendix_two.txt')
        self.assertIn('filled successfully', message)
        filled_data_args2 = open('./input/tablefill_template_filled.lyx', 'rU').readlines()
        
        self.assertEqual(filled_data_args1, filled_data_args2)
        

if __name__ == '__main__':
    os.getcwd()
    unittest.main()
