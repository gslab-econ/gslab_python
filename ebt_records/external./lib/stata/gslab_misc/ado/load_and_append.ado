 /**********************************************************
 *
 *  load_and_append.ado: Load and append a list of files
 * 
 **********************************************************/ 

program load_and_append
    version 12
    syntax anything, [clear insheet dir(str) insheet_options(str) append_options(str) DSId(string) DSName(string) OBSseq(string) SUBset(string asis) fast ]
    
    parse_input `anything', dir(`dir')
    local filelist "`r(filelist)'"
    local numfiles : word count `filelist'

    * Convert delimited files to dta
    foreach i of numlist 1/`numfiles' {
        local inputfile`i' : word `i' of `filelist'
        if "`insheet'"~="" {
            preserve
            tempfile temp`i'
            clear
            qui insheet using "`inputfile`i''", `insheet_options'
            qui save "`temp`i''"
            local insheetinputfile`i' "`inputfile`i''"
            local inputfile`i' `"`temp`i''"'
            restore
        }
    }
    
    if `"`subset'"'=="" {
        forv i=1(1)`numfiles' {
            local ids`i' `"`inputfile`i''"'
        }
    }
    else {
        preserve
        forv i=1(1)`numfiles' {
            tempfile ids`i'
            cap use `subset' using `"`inputfile`i''"', clear `label'
            if _rc!=0 {
                disp as error "Error reading input data set: " as result `"`inputfile`i''"'
                disp as error "Subset string: " as result `"`subset'"'
                error 498
            }    
            qui save `"`ids`i''"'
        }
        restore
    }
    
    * Load and append
    use `ids1', `clear'
    
    if "`fast'"=="" {
        preserve
    }
    
    tempvar dsidt dsnamet obsseqt
    
    if `"`dsid'"'!="" {
        qui {
            gene long `dsidt'=1
            lab var `dsidt' "Input dataset"
        }
    }
    
    if `"`inputfile1'"'!="" {
        qui {
            gene str1 `dsnamet'=""
            replace `dsnamet'=`"``insheet'inputfile1'"'
            lab var `dsnamet' "Input dataset file name"
        }
    }
    
    if `"`obsseq'"'!="" {
        qui {
            gene long `obsseqt'=_n
            lab var `obsseqt' "Observation sequence in input data set"
        }
    }
    local nobs=_N
    
    if `numfiles' > 1 {
        foreach i of numlist 2/`numfiles' {
            append using `ids`i'', `append_options'
            
            local nobsp=`nobs'+1
            if `"`dsid'"'!="" {
                qui replace `dsidt'=`i' in `nobsp'/l
            }
            if `"`inputfile`i''"'!="" {
                qui replace `dsnamet'=`"``insheet'inputfile`i''"' in `nobsp'/l
            }
            if `"`obsseq'"'!="" {
                qui replace `obsseqt'=_n-`nobs' in `nobsp'/l
            }
            local nobs=_N
        }
    }
    
    foreach V in dsid dsname obsseq {
        if `"``V''"'!="" {
            qui compress ``V't'
            rename ``V't' ``V''
        }
    }
    
    if "`fast'"=="" {
        restore, not
    }
    
end

program parse_input, rclass
    syntax anything, [dir(str)] 

    local filelist ""
    foreach rawname in `anything' {

        * Separate filename and path
        local temp : subinstr local rawname "\" "/", all
        local temp : subinstr local temp "/" " ", all
        local count : word count `temp'
        local rawfilename : word `count' of `temp'
        local path : subinstr local rawname "`rawfilename'" ""
        local path : subinstr local path "\" "/", all

        * Add dir() option to path
        if "`dir'"~="" {
            local dir : subinstr local dir "\" "/"
            if substr("`dir'", length("`dir'"), length("`dir'")) ~= "/" {
                local dir "`dir'/"
            }
            local path "`dir'`path'"
        }

        * Add dta extension by default
        if strpos("`rawfilename'", ".") == 0 local rawfilename "`rawfilename'.dta"

        * Handle wildcards
        if strpos("`rawfilename'", "*") > 0 {
            local dir_wildcard "."
            if "`path'"~="" local dir_wildcard "`path'"
            local newfiles : dir `"`dir_wildcard'"' files `"`rawfilename'"', respectcase
        }
        else {
            local newfiles "`rawfilename'"
        }

        * Append to list
        foreach file in `newfiles' {
            local file : subinstr local file `"""' ""
            local filelist `"`filelist' `path'`file'"'
        }
    }
    return local filelist "`filelist'"
end

