# #! /usr/bin/env python

# import unittest, sys, os, shutil, contextlib
# sys.path.append('..')
# from py.make_log import start_make_logging
# from py.dir_mod import clear_dirs
# from py.run_program import run_command
# from nostderrout import nostderrout
    

# class testRunCommand(unittest.TestCase):

#     def setUp(self):
#         makelog_file = '../output/make.log'
#         output_dir = '../output/'
#         with nostderrout():
#             clear_dirs(output_dir)  
#             start_make_logging(makelog_file)

#     def test_default_log(self):
#         self.assertFalse(os.path.isfile('test_data.txt'))
#         with nostderrout():
#             run_command(command = 'wzunzip ./input/zip_test_file.zip ./') 
#         logfile_data = open('../output/make.log', 'rU').readlines()
#         search_str1 = 'Unzipping test_data.txt.'
#         search_str2 = 'Extracting test_data.txt.'
#         found1 = logfile_data[-1].find(search_str1) != -1
#         found2 = logfile_data[-1].find(search_str2) != -1
#         self.assertTrue(found1 | found2)
#         self.assertTrue(os.path.isfile('test_data.txt'))
        
#     def test_custom_log(self):
#         self.assertFalse(os.path.isfile('test_data.txt'))    
#         os.remove('../output/make.log')
#         makelog_file = '../output/custom_make.log'
#         output_dir = '../output/'
#         with nostderrout():
#             clear_dirs(output_dir)  
#             start_make_logging(makelog_file)
#             run_command(command = 'wzunzip ./input/zip_test_file.zip ./', makelog = '../output/custom_make.log')
#         logfile_data = open('../output/custom_make.log', 'rU').readlines()
#         search_str1 = 'Unzipping test_data.txt.'
#         search_str2 = 'Extracting test_data.txt.'
#         found1 = logfile_data[-1].find(search_str1) != -1
#         found2 = logfile_data[-1].find(search_str2) != -1
#         self.assertTrue(found1 | found2)
#         self.assertTrue(os.path.isfile('test_data.txt'))
        
#     def test_independent_log(self):
#         self.assertFalse(os.path.isfile('test_data.txt'))     
#         with nostderrout():
#             run_command(command = 'wzunzip ./input/zip_test_file.zip ./', log = '../output/command.log')
#         makelog_data = open('../output/make.log', 'rU').readlines()
#         search_str1 = 'Unzipping test_data.txt.'
#         search_str2 = 'Extracting test_data.txt.'
#         found1 = makelog_data[-1].find(search_str1) != -1
#         found2 = makelog_data[-1].find(search_str2) != -1
#         self.assertTrue(found1 | found2)
#         self.assertTrue(os.path.isfile('../output/command.log'))
#         commandlog_data = open('../output/command.log', 'rU').readlines()
#         found1 = commandlog_data[-1].find(search_str1) != -1
#         found2 = commandlog_data[-1].find(search_str2) != -1
#         self.assertTrue(found1 | found2)
#         self.assertTrue(os.path.isfile('test_data.txt'))
   
#     def tearDown(self):
#         if os.path.isdir('../output/'):
#             shutil.rmtree('../output/')
#         if os.path.isfile('test_data.txt'):
#             os.remove('test_data.txt')
    
# if __name__ == '__main__':
#     os.getcwd()
#     unittest.main()
