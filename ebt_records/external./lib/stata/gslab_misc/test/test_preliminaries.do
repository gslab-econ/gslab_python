 /**********************************************************
 *
 *  TEST_PRELIMINARIES.ADO
 * 
 * 
 **********************************************************/ 

adopath ++ ../ado/

display "maxvar " c(maxvar) ", matsize " c(matsize) ", linesize " c(linesize) ", seed " c(seed)
query sortseed
display `r(sortseed)'
***DEFAULT TEST
preliminaries
display "maxvar " c(maxvar) ", matsize " c(matsize) ", linesize " c(linesize) ", seed " c(seed)
query sortseed
display `r(sortseed)'

***FULL TEST
*test global file
file open TESTCONST using ./testconst.txt, write replace
file write TESTCONST "testconst 1"
file close TESTCONST

preliminaries, matsize(1000) maxvar(10000) seed(10) sortseed(100) linesize(200) loadglob(testconst.txt)
display "maxvar " c(maxvar) ", matsize " c(matsize) ", linesize " c(linesize) ", seed " c(seed)
query sortseed
display `r(sortseed)'
display "$testconst"

*test seed set
display runiform()
display runiform()
preliminaries, seed(10)
display runiform()

*test matsize/maxvar error
capture noisily preliminaries, maxvar(test)
capture noisily preliminaries, matsize(test)

*test linesize error
capture noisily preliminaries, linesize(256)

*test loadglob error
capture noisily preliminaries, loadglob(none)
capture noisily preliminaries, loadglob(testconst.txt testconst2.txt)

erase ./testconst.txt

* Help file exists and is correct
help preliminaries

