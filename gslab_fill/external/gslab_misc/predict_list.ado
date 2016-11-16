/**********************************************************
 *
 * PREDICT_LIST.ADO: Compute predicted value from a subset
 *  of regression coefficients
 *
 * Date: 6/08
 * Creator: MG
 *
 **********************************************************/

program define predict_list

	version 10
	syntax varlist, gen(name)
	
	gen `gen' = 0
	foreach V in `varlist' {
		replace `gen' = `gen' + _b[`V']*`V'
	}
end

