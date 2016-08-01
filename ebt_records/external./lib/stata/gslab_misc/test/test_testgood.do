****************************************************************************************************
*
* TEST_TESTGOOD.DO
*
****************************************************************************************************

quietly {
    version 11
    set more off
    adopath + ../ado
    preliminaries

    program main
        quietly setup_data
        testgood regress y x
        testgood regress y x, robust
        testgood gen z = 2
        testgood replace y = 0 if x<0
        sort x
        testgood by x: replace z = 0
        
        di ""
        di "THESE TESTS SHOULD ALL FAIL:"
        testgood regress y q
        testgood regress y x, blah
        testgood blah
    end

    program setup_data
        set obs 100
        gen x = uniform()
        gen y = uniform()
    end
}

* EXECUTE
main


