****************************************************************************************************
*
* SELECT_OBSERVATIONS.ADO
*
* Keep observations from the dataset in memory that match a using dataset.
*
****************************************************************************************************

program select_observations
    version 11
    syntax varlist using, [utostring(str) udestring(str) delim(str) uif(str) umatch(str) *]
    
    preserve
    tempfile temp
    
    if "`delim'"=="comma" {
        insheet `using', comma clear
    }
    else if "`delim'"=="tab" {
        insheet `using', tab clear
    }
    else {
        use `using', clear
    }
    
    if "`utostring'"~="" {
        tostring `utostring', replace
    }
    if "`udestring'"~="" {
        destring `udestring', replace
    }
    
    if "`umatch'"~="" {
        local mergelist "`umatch'"
    }
    else {
        local mergelist "`varlist'"
    }

    if "`uif'"~="" {
        keep if `uif'
    }

    keep `mergelist' 
    duplicates drop
    save `temp'
    
    restore
    mmerge `varlist' using `temp', type(n:1) unm(none) umatch(`mergelist')
    drop _merge
    
end
