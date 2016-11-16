/**********************************************************
 *
 * MULTICOLLAPSE.ADO: A replacement for collaspe that allows the calculation of means using various weights
 *   
 *
 **********************************************************/

 
 program define multicollapse
	version 11
	syntax [if] [in], means(varlist) [weights(varlist)] [by(varlist)] 
	
	local stat1 = ""
	if "`weights'" != "" {
		local stat1 = "(sum)" 
	}	
	local prods = ""
	foreach m in `means' {	
		foreach w in `weights' {	
			gen `m'_`w'_prod = `m'*`w' if `m' != .
			gen `w'_`m'_nomiss = `w'*(`m' != . ) 
			local prod = "`prod' `m'_`w'_prod" 
			local weight_nomiss = "`weight_nomiss' `w'_`m'_nomiss"
		}
	}

collapse `stat1' `prod' `weight_nomiss' `weights' (mean) `means' `if' `in', by(`by')
	
foreach m in `means' {
	foreach w in `weights' {	
		gen `m'_`w' = `m'_`w'_prod/`w'_`m'_nomiss
		drop `m'_`w'_prod
		drop `w'_`m'_nomiss
	}
	rename `m' `m'_noweight
}	


 end
