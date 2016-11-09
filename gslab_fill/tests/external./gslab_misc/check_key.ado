 /**********************************************************
 *
 *  CHECK_KEY.ADO: Check that a dataset has a valid key
 * 
 **********************************************************/ 

 program check_key
     quietly {
        version 11
        syntax [using/], key(str) [sort]
        preserve
        
        if "`using'"!=""{
            use `key' using `using', clear
        }

        if "`sort'"!=""{
            check_sort `key'
        }

        check_no_missings `key'
        check_key_unique `key'

        restore
    }
end

program check_sort
    syntax anything(name=key)
    describe, varlist
    local sortlist=r(sortlist)
    cap assert "`key'" == "`sortlist'"
    if _rc > 0 {
        di as error "Data are not sorted by <`key'>"
        exit 198
    }
end

program check_no_missings
    syntax anything(name=key)
    foreach var in `key'{
    cap assert missing(`var')==0
    if _rc > 0 {
        di as error "Key `key' is missing for one or more observations"
        exit 198
    }
}
end

program check_key_unique
    syntax anything(name=key)
    tempvar temp
    qui bysort `key': gen `temp' = _N
    cap assert `temp'==1
    if _rc > 0 {
        di as error "<`key'> does not uniquely identify observations"
        exit 198
    }
end


