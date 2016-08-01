/**********************************************************
 *
 * OOO.ADO: Display comment in log file.
 *  (To be used within loops)
 *
 * Date: 3/19/08
 * Creator: MG
 *
 **********************************************************/

cap program drop ooo

program define ooo

	version 10
	syntax anything

	display ""
	display ""
	display ""
	display "**************************************************************"
	display "* `anything'"
	display "**************************************************************"
	display ""
	display ""

end

