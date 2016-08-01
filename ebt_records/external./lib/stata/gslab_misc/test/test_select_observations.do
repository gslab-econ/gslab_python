****************************************************************************************************
*
* TEST_SELECT_OBSERVATIONS.DO
*
****************************************************************************************************

quietly {
    version 11
    set more off
    adopath + ../ado
    preliminaries

    program main
        cap mkdir temp
        quietly setup_main_dataset
        quietly setup_using_datasets

        testgood test_basic
        testgood test_using_csv
        testgood test_using_tab
        testgood test_umatch
        testgood test_uif
        testgood test_udestring
        testgood test_utostring

        clean_up
    end

    program setup_main_dataset
        set obs 100
        gen n = _n
        gen y = uniform()
        save temp/main.dta, replace
    end

    program setup_using_datasets
        preserve
        keep if mod(n,10)==0
        gen nstr = string(n)
        save temp/using.dta, replace
        outsheet using temp/using.txt, replace
        outsheet using temp/using.csv, comma replace
        restore
    end
    
    program test_basic
        preserve
        select_observations n using temp/using.dta
        basic_assertion
        restore
    end
    
    program basic_assertion
        assert mod(n,10)==0
        sum n
        assert r(min)==10
        assert r(max)==100
        assert r(mean)==55
    end
    
    program test_using_csv
        preserve
        select_observations n using temp/using.csv, delim(comma)
        basic_assertion
        restore
    end
    
    program test_using_tab
        preserve
        select_observations n using temp/using.txt, delim(tab)
        basic_assertion
        restore 
    end
    
    program test_umatch
        preserve
        gen nalt = n
        select_observations nalt using temp/using.dta, umatch(n)
        basic_assertion
        restore   
    end

    program test_uif
        preserve
        select_observations n using temp/using.dta, uif(n>=50)
        sum n
        assert r(min)==50
        restore   
    end
    
    program test_udestring
        preserve
        select_observations n using temp/using.dta, udestring(nstr) umatch(nstr)
        basic_assertion
        restore   
    end

    program test_utostring
        preserve
        gen nstr = string(n)
        select_observations nstr using temp/using.dta, utostring(n) umatch(n)
        basic_assertion
        restore   
    end

    program clean_up
        erase temp/main.dta
        erase temp/using.dta
        erase temp/using.csv
        erase temp/using.txt
        rmdir temp
    end

    }

* EXECUTE
main


