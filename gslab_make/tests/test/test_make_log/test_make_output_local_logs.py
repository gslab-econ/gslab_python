#! /usr/bin/env python

import unittest, sys, os, shutil
sys.path.append('../..')
from make_log import make_output_local_logs
from nostderrout import nostderrout
    
    
class testMakeOutputLocalLogs(unittest.TestCase):

    def setUp(self):
        self.test_dir = './input/'
        files = os.listdir(self.test_dir)
        files = [ f for f in files if (os.path.isfile(os.path.join(self.test_dir, f)) 
                                       and not f.startswith('.')) ]
        self.file_count = len(files)
            
    def test_default_log(self):
        default_stats = '../output/stats.log'
        default_heads = '../output/heads.log'
        self.assertFalse(os.path.exists(default_stats))
        self.assertFalse(os.path.exists(default_heads))

        with nostderrout():
            make_output_local_logs(self.test_dir)
            
        self.assert_logs(default_stats, default_heads, self.file_count)          
                         
    def test_custom_log(self):
        custom_stats = '../out/custom_stats.log'
        custom_heads = '../out/custom_heads.log'
        self.assertFalse(os.path.exists(custom_stats))
        self.assertFalse(os.path.exists(custom_heads))
        
        with nostderrout():
            make_output_local_logs(self.test_dir,
                            output_dir = '../out/',
                            stats_file = 'custom_stats.log',
                            heads_file = 'custom_heads.log')

        self.assert_logs(custom_stats, custom_heads, self.file_count)       
        
    def test_no_recur_lim (self):
        default_stats = '../output/stats.log'
        default_heads = '../output/heads.log'
        self.assertFalse(os.path.exists(default_stats))
        self.assertFalse(os.path.exists(default_heads))
        
        with nostderrout():
            make_output_local_logs(self.test_dir,
                            recur_lim = False)
        
        file_count = 0
        for root, dirs, files in os.walk(self.test_dir):
            root = os.path.abspath(root)
            this_dir = os.path.basename(root)
            if not this_dir.startswith('.'):
                files = [ f for f in files if not f.startswith('.') ]
                file_count += len(files)
            else:
                del dirs[:]

        self.assert_logs(default_stats, default_heads, file_count)  
        
    def assert_logs(self, stats, heads, file_count):
        self.assertTrue(os.path.exists(stats))
        self.assertTrue(os.path.exists(heads))
        stats_count = len(open(stats).readlines()) - 1
        self.assertEqual(stats_count, file_count)
        heads_count = self.get_string_count(heads, '-' * 65) - 1
        self.assertEqual(heads_count, file_count)

    def get_string_count(self, logfile, string):
        logfile_data = open(logfile, 'rU').readlines()
        count = 0
        for line in logfile_data:
            if line.startswith(string):
                count += 1

        return count        

    def tearDown(self):
        if os.path.isdir('../output/'):
            shutil.rmtree('../output/')
        if os.path.isdir('../out/'):
            shutil.rmtree('../out/')             
    
if __name__ == '__main__':
    os.getcwd()
    unittest.main()
