/**********************************************************
 *
 * RANKUNIQUE.ADO: A replacement for egen XXX = rank(), unique
 *   that uses explicit randomization to break ties.
 *
 *   Option seed() is optional; allows you to set seed
 *   explicitly.
 *
 * Date: 8/22/08
 * Creator: MG
 *
 **********************************************************/

program define rankunique

	version 10
	syntax anything [if] [in], gen(name) [by(varlist)] [seed(integer 4271975)]
	marksample touse
	tempvar rand seq max
	tempname oldseed

	* retain old seed so calling function does not permanently change it
	local oldseed = c(seed)

	set seed `seed'
	sort *
	gen `rand' = uniform() if `touse'
	set seed `oldseed'
	gsort `by' `anything' `rand'
	egen `seq' = seq() if `touse', by(`by')
	egen `max' = sum(1) if `touse', by(`by')
	gen `gen' = `max'-`seq'+1 if `touse'

end

