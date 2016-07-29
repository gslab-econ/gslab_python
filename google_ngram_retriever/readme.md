DESCRIPTION
==========================================================
This library contains a program to download specific n-grams from the Google ngram API and saves the output in a .csv file. This removes the necessity of downloading large files from Google and parsing the results. Files in /py and /docs were downloaded from https://github.com/econpy/google-ngrams on October 29 by clicking “Download ZIP”. 

The interface should be very similar to Google’s online Ngram graphing service, except the data is stored in a .csv file.

Software requirements:
-Python 2.7
-‘requests’ and ‘pandas’ python modules

NOTES
==========================================================
The library was reformatted to better fit GSLAB workflow. The program must now be called within a python script and can not be called from command line/terminal. 

The function definition for the user is as follows:

def downloadGoogleNgrams(query, saveFolder = './', filename = '', corpus = 'eng_2012', startYear = 1800, endYear = 2000, smoothing = 3, caseInsensitive = True, allData = True):

-‘query’ should be a string that is exactly what you would type into Google’s online Ngram service. 
-‘filename’ should include the ‘.csv’ file ending.
-‘allData’ is a binary for whether aggregated data columns should be kept. For example, under the caseInsensitive option, Google will return an aggregated column for
that aggregates each of the different cases, while also providing a column for each case. When allData is True, this aggregated data column will be kept, otherwise it will be dropped.
-‘smoothing’ denotes the smoothing number, which is the same as used in Google’s online Ngram service.


The readme for the original program can be found in /docs.

