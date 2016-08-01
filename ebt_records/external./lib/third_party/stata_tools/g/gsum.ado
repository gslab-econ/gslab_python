*! $Rev$  $Sep 09 2011$
// gsum calculates the mean, standard deviation, and two versions of a set of quantiles for grouped data.

program gsum, rclass byable(recall)
	version 11.1
	syntax varlist [if] [fweight aweight pweight iweight], [g0(string)] [g1(string)] ///
	[g2(string)] [g3(string)] [g4(string)] [g5(string)] [g6(string)] ///
	[g7(string)] [g8(string)] [g9(string)] [g10(string)] [g11(string)] ///
	[g12(string)] [g13(string)] [g14(string)] [g15(string)] [g16(string)] ///
	[g17(string)] [g18(string)] [g19(string)] [g20(string)] [g21(string)] ///
	[g22(string)] [g23(string)] [g24(string)] [g25(string)] ///
	[Table] [Save(string)] [GENerate(namelist)] [Quantiles(numlist)]
	preserve
	*mark sample
	marksample touse
	*get categorical list, assure they are all integers
	quietly : levelsof `varlist' if `touse', local(gvarlist)
	local gcount = 0
	foreach l in `gvarlist' {
		if "`lowestg'" == "" {
			local lowestg = `l'
		}
		local highestg = `l'
		capture confirm integer number `l'
		if _rc == 7 {
			display as error "non-integer value found in `varlist'"
			exit 7
		}
		local ++gcount
	}
	capture assert `gcount' > 1
	if _rc == 9 {
		display "only 1 category of `varlist'"
		exit 9
	}
	*figure out the quantiles
	capture confirm existence `quantiles'
	if _rc == 6 {
		local qlist "25 50 75"
	}
	else {
		foreach n in `quantiles' {
			capture assert `n' > 0 & `n' < 1
			if _rc == 9 {
				display as error "quantiles need to be between 0 and 1"
				exit 9
			}
			local p = regexr("`n'","\.","")
			foreach k in 1 2 3 4 5 6 7 8 9 {
				if "`p'" == "`k'" {
					local p "`p'0"
				}
			}
			local qlist "`qlist' `p' "
		}
	}
	*specifiy the temporary scalars
	tempname count totw mean var sd mn mx
	foreach q in `qlist' {
		tempname qi`q' qm`q'
	}
	forvalue i = 0/25 {
		tempname lower`i' upper`i' midpt`i' range`i'
	}
	*specify the temporary variables
	tempvar w fw sfw upper lower midpt range w_midpt dev2 quantile
	*assure that there is only one variable to get stats of
	local k = 0
	foreach v in `varlist' {
		local ++k
	}
	if `k' > 1 {
		display as error  ///
		"gsum only calcuates point estimates for a single variable"
		exit 9
	}
	*assure that the categorical variable only has values between 0 and 25
	quietly : sum `gvar' if `touse'
	capture assert r(min) > 0 & r(max) < 26
	if _rc == 9 {
		display as error  ///
		"your group variable needs numeric categories that range from 0-25"
		exit 9
	}
	*capture ranges from value labels if they exist
	forvalues l = 0/25 {
		local checklist "`checklist'`g`l''"
	}
	capture confirm existence `checklist'
	if _rc == 6 {
		local labelist : value label `varlist'
		capture confirm existence `labelist'
		if _rc == 6 {
			display as error "need to specify ranges in either the options or as value labels"
		}
		else {
			foreach l in `gvarlist' {
				local g`l' : label `labelist' `l'
			}
		}
	}
	*create category macros
	foreach l in `gvarlist' {
		tokenize `g`l'', parse(-)
		if "`2'" == "-" {
			*parse ok
		}
		else {
			display as error "please provide a range for group `l'"
			exit 9
		}
		capture confirm number `1'
		if _rc == 7 {
			display as error  ///
			"`1' not a number, please provide numeric quantity for group `l' lower bound"
			exit 9
		}
		capture confirm number `3'
		if _rc == 7 {
			display as error  ///
			"`3' not a number, please provide numeric quantity for group `l' higher bound"
			exit 9
		}
		if `3' > `1' {
			*range ok
		}
		else if `3' < `1' {
			display as error  ///
			"lower bound is higher than upper bound for group `l'"
			exit 9
		}
		else if `3' == `1' {
			display as error ///
			"lower bound is equal to upper bound for group `l'"
			exit 9
		}
		scalar `lower`l'' = `1'
		scalar `upper`l'' = `3'
		scalar `range`l'' = `3' - `1'
		scalar `midpt`l'' = ((`3' - `1')/2) + `1'
		if `l' == `lowestg' {
			scalar `mn' = `1'
		}
		if `l' == `highestg' {
			scalar `mx' = `3'
		}
	}
	*assure that categories don't overlap
	foreach l in `gvarlist' {
		foreach k in `gvarlist' {
			if `l' == `k' {
				*skip
			}
			else if `l' < `k' {
				capture assert `upper`l'' <= `lower`k''
				if _rc == 9 {
					display as error "group definitions `l' and `k' overlap"
					exit 9
				}
			}
			else if `k' < `l' {
				capture assert `upper`k'' <= `lower`l''
				if _rc == 9 {
					display as error "group definitions `k' and `l' overlap"
					exit 9
				}
			}
		}
	}
	*drop missing categories of varlist
	quietly : drop if `varlist' == .
	*create or use the weight variable
	if "`weight'" == "" {
		quietly : gen `w' = 1 if `touse'
	}
	else {
		quietly : gen `w' `exp' if `touse'
	}
	*gen casecount variable
	quietly : gen n = 1 if `touse'
	quietly : sum n
	scalar `count' = r(sum)
	*get the sum of the weights for each value of varlist
	collapse (sum) `w' n if `touse', by(`varlist')
	sort `varlist'
	*calculate CDF
	quietly : sum `w'
	scalar `totw' = r(sum)
	quietly : gen `fw' = `w'/`totw'
	quietly : gen `sfw' = sum(`fw')
	*initialize necessary variables
	quietly : gen `lower' = .
	quietly : gen `upper' = .
	quietly : gen `midpt' = .
	quietly : gen `range' = .
	*fill in values
	foreach l in `gvarlist' {
		foreach stat in lower upper midpt range {
			quietly : replace ``stat'' = ``stat'`l'' if `varlist' == `l'
		}
	}
	*calculation of the mean
	quietly : gen `w_midpt' = `midpt' * `w'
	quietly : sum `w_midpt'
	scalar `mean' = r(sum)/`totw'
	*calculation of variance and standard deviation
	quietly : gen `dev2' = ((`midpt' - `mean')^2)*`w'
	quietly : sum `dev2'
	scalar `var' =  r(sum) / (`totw' - 1)
	scalar `sd' = `var'^.5
	*calculate quantiles
	foreach q in `qlist'  {
		*interpolation
		quietly : gen `quantile' =  ///
		`lower' + ((((.`q') - `sfw'[_n-1])/`fw') * `range')  ///
		if `sfw' >= (.`q') & `sfw'[_n-1] < (.`q')
		quietly : sum `quantile'
		if r(N) == 1 {
			scalar `qi`q'' = r(mean)
		}
		else if r(N) == 0 {
			quietly : replace `quantile' =  ///
			`upper' - ((( `sfw' - (.`q'))/`fw') * `range')  ///
			if (`sfw' >= (.`q') & `sfw'[_n-1] < (.`q')) | _n == 1
			quietly : sum `quantile'
			scalar `qi`q'' = r(mean)
		}
		drop `quantile'
		*midpoint of the category at or above quantile
		quietly : gen `quantile' =  ///
		`midpt' if (`sfw' >= (.`q') & `sfw'[_n-1] < (.`q') )
		quietly : sum `quantile'
		if r(N) == 1 {
			scalar `qm`q'' = r(mean)
		}
		else if r(N) == 0 {
			quietly : replace `quantile' =  ///
			`midpt' if _n == 1
			quietly : sum `quantile'
			scalar `qm`q'' = r(mean)
		}
		drop `quantile'
	}
	*post results to r
	return scalar N = `count'
	else if "`weight'" != "" {
		return scalar sum_W = `totw'
	}
	foreach stat in mean var sd mn mx {
		return scalar `stat' = ``stat''
	}
	foreach q in `qlist' {
		return scalar qm`q' = `qm`q''
		return scalar qi`q' = `qi`q''
	}
	*display results
	display _newline as text "Grouped Data Summary Statistics" _newline
	display as text %12s abbrev("Variable",12) _col(14) "{c |}"  ///
	_col(22) "N" _col(29) "Mean" _col(40) "Std. Dev." _col(55) "Min" _col(67) "Max"
	display as text "{hline 13}" "{c +}" "{hline 60}"
	if "`weight'" == "" {
		display as text as text %12s abbrev("`varlist'",12) _col(14) "{c |}" ///
		_col(15) as result %8.0fc `count'  ///
		_col(22) as result %10.3f `mean' _col(38) as result %10.3f `sd' ///
		_col(45) as result %10.3f `mn' _col(60) as result %10.3f `mx'
	}
	else if "`weight'" != "" {
		display as text as text %12s abbrev("`varlist'",12) _col(14) "{c |}" ///
		_col(15) as result %8.0fc `totw'  ///
		_col(22) as result %10.3f `mean' _col(38) as result %10.3f `sd' ///
		_col(45) as result %10.3f `mn' _col(60) as result %10.3f `mx'
	}
	display _newline as text "Quantiles" _newline
	display as text %12s abbrev("Quantile",12) _col(14) "{c |}"  ///
	_col(17) "Lowest Midpoint at Quantile" _col(50) "Linear Interpolation"
	display as text "{hline 13}" "{c +}" "{hline 60}"
	foreach q in `qlist' {
		if `qm`q'' != . & `qi`q'' != . {
			display as text  %12s abbrev("0.`q'",12) _col(14) "{c |}"  ///
			_col(23) as result %10.3f `qm`q'' _col(53) as result %10.3f `qi`q''
		}
		else {
			display as text  %12s abbrev("0.`q'",12) _col(14) "{c |}"  ///
			_col(23) as result "not attainable" _col(53) as result %10.3f "not attainable"
		}
	}
	display as text "{hline 13}" "{c BT}" "{hline 60}"
	*rename for value table and renaming
	quietly : tostring `lower' `upper', force replace format(%10.0f)
	quietly : gen Range = `lower' + "-" + `upper'
	rename `midpt' Midpoint
	rename `w' Weight
	rename `fw' pWeight
	rename `sfw' CDF
	format Weight pWeight CDF %9.3f
	label val `varlist'
	if "`table'" == "table" {
		display _newline as text "Value Table"
		list `varlist' Range Midpoint n Weight pWeight CDF,   ///
		noobs  sep(35) sum(n Weight pWeight)
	}
	if "`save'" != "" {
		keep `varlist' Range Midpoint n Weight pWeight CDF
		order `varlist' Range Midpoint n Weight pWeight CDF
 		quietly : save "`save'", replace
	}
	*restore data
	restore
	if "`generate'" != "" {
		display _newline "variable `generate' created with value midpoints"
		quietly : gen `generate' = .
		foreach l in `gvarlist' {
			quietly : replace `generate' = `midpt`l'' if `varlist' == `l'
		}
	}
end
