#! /usr/bin/env python
from __future__ import print_function
import re, os, subprocess, time

def externals_search(search_terms, search_path, results_name, rev_num=None):

    # Preliminaries
    time_start = time.time()
    fnull = open(os.devnull, 'w')
    if rev_num is None:
        rev_num = "HEAD"
        
    # Test input arguments    
    if search_path[:34] != "http://gslab.chicagobooth.edu/svn/":
        print('ERROR: Search path must begin with "http://gslab.chicagobooth.edu/svn/"')
        return
    if search_path[-1:] != "/":
        print('ERROR: Search path must end with "/"')
        return
    if not isinstance(rev_num, str) or not isinstance(results_name, str) or not isinstance(search_path, str):
        print('ERROR: rev_num, results_name, and search_path must all be strings')
        return    
    if rev_num != "HEAD":
        if not isinstance(int(float(rev_num)), int):
            print('ERROR: rev_num must either be a stringed integer or "HEAD"')
            return        
    if not isinstance(search_terms, list):
        print('ERROR: search_terms must be entered as a list')
        return    
    isString = 'TRUE'
    for term in search_terms:
        if not isinstance(term, str):
            isString = 'FALSE'        
    if isString == 'FALSE':
        print('ERROR: each element of search_terms must be a string')
        return

    ## START EXECUTION    
    # Get list of all files under search_path
    filenames = subprocess.check_output("svn list -R -r " + rev_num + 
      ' "' + search_path + '"', stderr = fnull, shell = True)
    filenames = re.compile(r'\r\n').split(filenames.decode("utf-8"))

    # Print list of externals files containing any of the search_terms
    results = open("../output/" + results_name + ".txt", 'w+')
    print("term\tfile", file = results)
    
    hits  = 0
    for filename in filenames:
        if "externals.txt" in filename or "externals.bat" in filename:
            externals_text = subprocess.check_output('svn cat -r ' + rev_num + 
              ' "' + search_path + filename + '"', stderr = fnull, shell = True)
            for term in search_terms:
                if term in externals_text:
                    hits = hits + 1
                    print("%s\t%s" % (term, filename), file = results) 
    # Log results 
    print("Search Externals Results \nFinished searching.")
    print("Hits: %d" % hits)
    print("Search terms: %s" % search_terms) 
    print("Search path: %s" % search_path)
    print("Revision number: %s " % rev_num)
    print("Duration: %d second(s)." % (time.time() - time_start))
    print("Results stored in ../output/" + results_name + ".txt\n\n")
  
