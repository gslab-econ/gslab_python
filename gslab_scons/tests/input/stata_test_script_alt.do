version 12
set more off
adopath + ../external/lib/stata/gslab_misc/ado/
preliminaries

set obs 10
gen var1 = _n

save_data ../customoutput/stata1.dta, key(var1) log(../customoutput/data_file_manifest.log) replace
save_data ../customoutput/stata2.dta, key(var1) log(../customoutput/data_file_manifest.log) replace
save_data ../customoutput/stata.csv, key(var1) outsheet log(../customoutput/data_file_manifest.log) replace
save_data ../customoutput/stata.txt, key(var1) outsheet log(../customoutput/data_file_manifest.log) replace
