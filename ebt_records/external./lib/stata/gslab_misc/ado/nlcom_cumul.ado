/**********************************************************
 *
 * NLCOM_CUMUL.ADO: Cumulate coefficients from a regression.
 *
 * Date: July 2009
 * Creator: Matt Gentzkow, Pat Dejarnette, & James Mahon
 *
 **********************************************************/

* Grab program nlcom_cumul and drop it (clear it so we can create nlcom_cumul program)
cap program drop nlcom_cumul

* Defines  a program called: http://www.stata.com/help.cgi?program
program define nlcom_cumul
	version 10
	syntax varlist, [norm(string)]
	
	* save & temporarily clear data
	preserve
	
	* cumulate coefficients
	local past ""
	local level_anything ""
	local level_nlcom ""
	foreach V in `varlist' {
		local past "`past' `V'"
		local level_anything "`level_anything' level_`V'"
		local level_`V' "level_`V':"
		local i = 1
		foreach P in `past' {
			if `i' == 1 {
				local level_`V' "`level_`V'' _b[`P']"
			}
			else {
				local level_`V' "`level_`V'' + _b[`P']"
			}
			local i = 0
		}
		local level_`V' "(`level_`V'')"
		local level_nlcom "`level_nlcom' `level_`V''"
	}
	quietly nlcom `level_nlcom', post
	
	* normalize cumulated coefficients
	if "`norm'" != "" {
		local level_norm_nlcom ""
		local level_norm_vars ""
		foreach V in `varlist' {
			local level_norm_nlcom "`level_norm_nlcom' (level_norm_`V': _b[level_`V'] - _b[level_`norm'])"
			local level_norm_vars "`level_norm_vars' level_norm_`V'"
		}
		quietly nlcom `level_norm_nlcom', post
	}
	
	* restore data
	restore
end

