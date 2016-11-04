#! /usr/bin/env python

import unittest
import sys
import os
sys.path.append('../../..')
from gslab_scons.build import *
from gslab_scons.log import *
from gslab_scons.exceptions import *

class test_build_tables(unittest.TestCase):

    def setUp(self):
        if not os.path.exists('../build/'):
            os.mkdir('../build/')

    def default(self):
        source = ['./input/tablefill_template.lyx', './input/tables_appendix.txt', './input/tables_appendix_two.txt']
        target = ['./input/tablefill_template_filled.lyx']
        build_tables(target, source, '')
        filled_data = open('./input/tablefill_template_filled.lyx', 'rU').readlines()
        self.assertEqual(len(tag_data) + 13, len(filled_data))
        for n in range(len(tag_data)):
            self.tag_compare(tag_data[n], filled_data[n + 13])         
 
    def default_string_target(self):
        source = ['./input/tablefill_template.lyx', './input/tables_appendix.txt', './input/tables_appendix_two.txt']
        target = './input/tablefill_template_filled.lyx'
        build_tables(target, source, '')
        filled_data = open('./input/tablefill_template_filled.lyx', 'rU').readlines()
        self.assertEqual(len(tag_data) + 13, len(filled_data))
        for n in range(len(tag_data)):
            self.tag_compare(tag_data[n], filled_data[n + 13])         

    def test_target_extension(self):
        source = ['./input/tablefill_template.lyx', './input/tables_appendix.txt', './input/tables_appendix_two.txt']
        target = './input/tablefill_template_filled.BAD'
        with self.assertRaises(BadExtensionError):
            build_tables(target, source, '')    

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
        
        
if __name__ == '__main__':
    os.getcwd()
    unittest.main()