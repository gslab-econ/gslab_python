*! 2.2.1  15aug2000  Jeroen Weesie/ICS
program define renvars
	version 6

	syntax [varlist] [, Upcase Lowcase /*
	*/ PREFix(str) POSTFix(str) PRESub(str) POSTSub(str) SUBst(str) /*
	*/ PREDrop(int 0) POSTDrop(int 0) Trim(int 8) /*
	*/ Fast Display ]

	local nopt = ("`upcase'"!="") + ("`lowcase'"!="") + (`"`prefix'"'!="") /*
	*/ + (`"`postfix'"'!="") + (`"`presub'"'!="") + (`"`postsub'"'!="")    /*
	*/ + (`"`subst'"'!="") + (`predrop'!=0) + (`postdrop'!=0) + (`trim'!=8)

	if  `nopt' != 1 {
		di in re "exactly one transformation option should be specified"
		exit 198
	}

	if "`subst'" != "" {
		local srch : word 1 of `subst'
		local repl : word 2 of `subst'
	}
	if "`presub'" != "" {
		local srch : word 1 of `presub'
		local repl : word 2 of `presub'
		local nsrch = length("`srch'")
	}
	if "`postsub'" != "" {
		local srch : word 1 of `postsub'
		local repl : word 2 of `postsub'
		local nsrch = length("`srch'")
	}

	if "`fast'" != "" {
		preserve
		local Done "restore, not"
	}

	tokenize `varlist'
	local i 1
	while "``i''" != "" {
		if "`upcase'" != "" {
			local newname = upper("``i''")
		}
		else if "`lowcase'" != "" {
			local newname = lower("``i''")
		}
		else if "`prefix'" != "" {
			local newname "`prefix'``i''"
		}
		else if "`postfix'"  != "" {
			local newname "``i''`postfix'"
		}
		else if "`subst'" != "" {
			local newname : subinstr local `i' "`srch'" "`repl'", all
		}
		else if "`presub'" != "" {
			if "`srch'" == substr("``i''",1,`nsrch') {
				local newname = "`repl'" + substr("``i''",`nsrch'+1,.)
			}
			else	local newname ``i''
		}
		else if "`postsub'" != "" {
			if "`srch'" == substr("``i''",-`nsrch',.) {
				local newname = substr("``i''",1,length("``i''")-`nsrch') + "`repl'"
			}
			else	local newname ``i''
		}
		else if `predrop' != 0 {
			local newname = substr("``i''", 1+`predrop', .)
		}
		else if `postdrop' != 0 {
			local newname = substr("``i''", 1, length("``i''")-`postdro')
		}
		else if `trim' != 8 {
			local newname = substr("``i''", 1, `trim')
		}

		RenVar ``i'' `newname'

		if "`display'" != "" & "``i''" != "`newname'" {
			di in gr "``i'' " _col(10) "-> `newname'"
		}

		local i = `i' + 1
	}

	`Done'
end


program define RenVar
	args oldname newname

	if "`oldname'" != "`newname'" {
		confirm new var `newname'
		capt rename `oldname' `newname'
		if _rc {
			di in re "`oldname' could not be renamed to `newname'"
			exit 198
		}
	}
end
exit

Note how this program demonstrates the need to have true functions in Stata!

