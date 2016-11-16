/**********************************************************
 *
 * SORTUNIQUE.ADO: A replacement for egen XXX = rank(), unique
 *   that uses explicit randomization to break ties.
 *
 *   Option seed() is optional; allows you to set seed
 *   explicitly.
 *
 * Date: 2/22/08
 * Creator: MG
 *
 **********************************************************/

program define sortunique

	version 10
	syntax anything [if] [in], [by(varlist)] [seed(integer 4271975)]
	tempvar rand
	tempname oldseed

	* retain old seed so calling function does not permanently change it
	local oldseed = c(seed)

	set seed `seed'
	sort *
	gen `rand' = uniform()
	set seed `oldseed'
	gsort `by' `anything' `rand'

end

