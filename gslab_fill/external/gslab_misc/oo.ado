/**********************************************************
 *
 * OO.ADO: Display minor comment in log file.
 *  (To be used within loops)
 *
 * Date: 3/19/08
 * Creator: MG
 *
 **********************************************************/

cap program drop oo

program define oo

	version 10
	syntax anything

	display ""
	display ""
	display "* `anything'"
	display ""

end

