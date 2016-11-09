/**********************************************************
 *
 * CUTBY.ADO: A version of egen, cut() that allows by.
 *   That is, cutby forms N groups within categories
 *   defined by the by(varlist).
 *
 * Date: 2/22/08
 * Creator: MG
 *
 **********************************************************/

cap program drop cutby

program define cutby

	version 10
	syntax varname [if] [in], by(varlist) groups(integer) gen(name)
	tempvar rank max pctile

	egen `rank' = rank(`varlist'), track by(`by')
	egen `max' = max(`rank'), by(`by')
	gen `pctile' = (`rank'-1)/`max'
	gen `gen' = int(`pctile' * `groups')

end

