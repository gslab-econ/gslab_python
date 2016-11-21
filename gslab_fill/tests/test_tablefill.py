#! /usr/bin/env python

import unittest
import sys
import os
import re
import decimal
import shutil
from subprocess import check_call, CalledProcessError

# Ensure the script is run from its own directory 
os.chdir(os.path.dirname(os.path.realpath(__file__)))

sys.path.append('../..') 
from gslab_fill import tablefill
from gslab_make.tests import nostderrout

class testTablefill(unittest.TestCase):
   
    def setUp(self):
        if not os.path.exists('./build/'):
            os.mkdir('./build/')

    def test_standard_input(self):
        with nostderrout():
            message = tablefill(input    = './input/tables_appendix.txt ' + \
                                           './input/tables_appendix_two.txt', 
                                template = './input/tablefill_template.lyx', 
                                output   = './build/tablefill_template_filled.lyx')
        self.assertIn('filled successfully', message)  

        # Read the empty and filled template files
        with open('./input/tablefill_template.lyx', 'rU') as template_file:
            tag_data = template_file.readlines()
        with open('./build/tablefill_template_filled.lyx', 'rU') as filled_file:
            filled_data = filled_file.readlines()

        # The filled LyX file should be longer than its template by a fixed 
        # number of lines because tablefill() adds a note to this template
        # in addition to filling it in.
        self.assertEqual(len(tag_data) + 13, len(filled_data))

        # Check that tablefill() filled the template's tags correctly.
        for n in range(len(tag_data)):
            self.tag_compare(tag_data[n], filled_data[n + 13]) 
    
    def tag_compare(self, tag_line, filled_line):
        '''
        Check that a line in a template LyX file containing a tag was
        properly filled by tablefill()
        '''
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
   
    def test_breaks_rounding_string(self):
        with nostderrout():
            error = tablefill(input    =  './input/tables_appendix.txt ' + \
                                          './input/tables_appendix_two.txt', 
                              template =  './input/tablefill_template_breaks.lyx', 
                              output   =  './build/tablefill_template_filled.lyx')
        self.assertIn('InvalidOperation', error)
    
    def test_illegal_syntax(self):
        # missing arguments
        with nostderrout():

            error = tablefill(input   = './input/tables_appendix.txt ' + \
                                        './input/tables_appendix_two.txt', 
                              template = './input/textfill_template.lyx')
        self.assertIn('KeyError', error)
                
        # non-existent input 1
        with nostderrout():
            error = tablefill(input    = './input/fake_file.txt ' + \
                                         './input/tables_appendix_two.txt', 
                              template = './input/tablefill_template_breaks.lyx', 
                              output   = './build/tablefill_template_filled.lyx')
        self.assertIn('IOError', error)
        
        # non-existent input 2
        with nostderrout():
            error = tablefill(input    = './input/tables_appendix.txt ' + \
                                         './input/fake_file.txt', 
                              template = './input/tablefill_template_breaks.lyx', 
                              output   = './build/tablefill_template_filled.lyx')
        self.assertIn('IOError', error)
        
    def test_argument_order(self):
        with nostderrout():
            message = tablefill(input    = './input/tables_appendix.txt ' + \
                                           './input/tables_appendix_two.txt', 
                                output   = './build/tablefill_template_filled.lyx',
                                template = './input/tablefill_template.lyx')
        self.assertIn('filled successfully', message)

        with open('./build/tablefill_template_filled.lyx', 'rU') as filled_file:
            filled_data_args1 = filled_file.readlines()
        
        with nostderrout():
            message = tablefill(output   = './build/tablefill_template_filled.lyx', 
                                template = './input/tablefill_template.lyx', 
                                input    = './input/tables_appendix.txt ' + \
                                            './input/tables_appendix_two.txt')
        self.assertIn('filled successfully', message)

        with open('./build/tablefill_template_filled.lyx', 'rU') as filled_file:
            filled_data_args2 = filled_file.readlines()
        
        self.assertEqual(filled_data_args1, filled_data_args2)
        
    def tearDown(self):
        if os.path.exists('./build/'):
            shutil.rmtree('./build/')


if __name__ == '__main__':
    os.getcwd()
    unittest.main()
