OVERVIEW
====================================================
This directory houses a Python script which parses through externals.txt
and externals.bat files in search of specific terms, and produces a list
of the externals files which contains such terms. 


HOW TO RUN
=====================================================
Create a python analysis code which imports the external_search function and
call the function by setting the four parameters according to the following:
    2a. search_terms 
        A python list of terms to be searched. Must be within [] brackets and words must 
        be separated by quotes and commas, if there is more than one term. 
    2b. rev_num 
        The SVN revision number at which all externals files will be searched. Input 
        must be in string format. Can be either "HEAD" or a revision number in the 
        format "#####".
    2c. results_name 
        A string denoting the results file name stored in /output/[results_name].txt
    2d. search_path
        The string of the SVN GSLab repository to which the search will be constrained.
        MUST end with forward slash ("/").


OUTPUT/
=====================================================
make.log            Includes search report. Otherwise is standard GSLab make.log
[results_name].txt  Contains search hits in tabular format. 


NOTES
=====================================================
Search for terms is STRICTLY case sensitive. E.g., searching for the terms "ANES" and 
"Anes" will not return the same results. 

As a matter of computational efficiency, adding terms to search_terms is preferable to 
executing the externals_search function many times. Variations of the search_path
and rev_num will, however, require separate executions of externals_search.

Benchmark runs:
15 minutes for one term on search_path = "http://gslab.chicagobooth.edu/svn/trunk/"
1  second for two terms on search_path = "http://gslab.chicagobooth.edu/svn/trunk/analysis/Media Productivity/"
   

EXAMPLE CALLS
=====================================================

    externals_search(
      search_terms = ["ANES", "lib"], 
      rev_num      = "20000",
      results_name = "ANES_lib_20000_results",
      search_path  = "http://gslab.chicagobooth.edu/svn/trunk/analysis/Media Productivity/")

    externals_search(
      search_terms = ["ANES", "Anes", "anes"], 
      rev_num      = "HEAD",
      results_name = "ANES_results",
      search_path  = "http://gslab.chicagobooth.edu/svn/trunk/analysis/Media Productivity/")
 
    externals_search(
      search_terms = ["loadglob"], 
      rev_num      = "HEAD",
      results_name = "loadglob_results",
      search_path  = "http://gslab.chicagobooth.edu/svn/trunk/analysis/BiasMeasures/")