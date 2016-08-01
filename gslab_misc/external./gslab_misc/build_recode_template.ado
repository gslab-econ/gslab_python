/**********************************************************
 *
 * BUILD_RECODE_TEMPLATE.ADO
 *
 * Creates new recode_template.csv preserving old recode information.
 *
 **********************************************************/

program build_recode_template
	version 11
	syntax [using/], output(str) variables(str) [key(str) import(str) descriptors(str) ///
        recode_var_name(str) quantity_vars(str) count]
    
    if "`recode_var_name'"=="" {
        local recode_var_name = "recode"
    }

	quietly {
		preserve
		tempfile temp_output
		create_empty_tempfile, outfile(`temp_output') strvarlist(attribute description) numvarlist(code)
		local num_vars : word count("`variables'")

        if "`using'"!="" {
            use `using', clear
        }

		forvalues i = 1/`num_vars' {
            local var = word("`variables'",`i')
            local desc = word("`descriptors'",`i')
			build_list, attribute(`var') key(`key') descriptor(`desc') appendto(`temp_output') ///
                quantity_vars(`quantity_vars') `count'
		}
		use `temp_output', clear
		import_recode_values using `temp_output', import(`import') key(`key') ///
            varname(`recode_var_name')
		format_and_save using `output', key(`key')
		restore
	}
end


program create_empty_tempfile
	preserve
	syntax, outfile(str) strvarlist(namelist) numvarlist(namelist)
	clear
	set obs 0
	foreach V in `strvarlist' {
		gen `V' = "" 
	}
	foreach V in `numvarlist' {
		gen `V' = .
	}
	save `outfile'
	restore
end


program build_list
	syntax, attribute(str) appendto(str) [key(str) descriptor(str) quantity_vars(str) count]
    
    preserve
    if "`descriptor'" == "" {
        local descriptor = "`attribute'_descr"
    }

    cap confirm variable `descriptor'
    if ~_rc {
        ren `descriptor' description
    }
    else {
        gen description = ""
    }

    ren `attribute' code
    gen attribute = "`attribute'"
    replace description = subinstr(description,",","",.)
    keep `key' attribute code description `quantity_vars'
    gen count = 1
    collapse (sum) count `quantity_vars', by(`key' attribute code description)
    if "`count'"=="" {
        drop count
    }
    
	append using `appendto'
	save `appendto', replace
    restore
end


program import_recode_values
	syntax using, [import(str) key(str) varname(str)]
	cap confirm file `import'
	if _rc==0 {
		tempfile temp
		preserve
		insheet using `import', clear
		save `temp'
		restore	
		
		* ensure variable types match
		foreach var in `key' attribute code {
			preserve
			sum `var'
			use `temp', clear
						
			if r(N)==0{
				tostring `var', replace
				save `temp', replace
			}
			else{
				destring `var', replace
				save `temp', replace
			}
			restore
		}
		
		use `using', clear
        mmerge `key' attribute code using `temp', type(1:1) unmatched(both) ukeep(`varname' notes)
		
		if _m==2 {
            show_warning
			drop if _m==2
		}
		drop _m
	}
	else {
        use `using', clear
		gen `varname' = .
		gen notes = ""
	}
end

program show_warning
    di ""
    di ""
    di "WARNING: Data may be lost. Some rows of imported recode file not in new template."
    di ""
    di "Press enter to continue." _request(null)
end

program format_and_save
	syntax using/, [key(str)]
	format code %12.0g
    save_data `using', key(`key' attribute code) ///
        outsheet log(none) delim(",") noquote replace
end


