****************************************************************************************************
*
* TEST_TESTBAD.DO
*
****************************************************************************************************

quietly {
    version 11
    set more off
    adopath + ../ado
    preliminaries

    program main
        quietly setup_data
        testbad regress y z
        testbad regress y x, blah
        testbad blah
        
        di ""
        di "THESE TESTS SHOULD ALL FAIL:"
        testbad regress y x
        testbad regress y x, robust
        testbad gen z = 2
        
    end

    program setup_data
        set obs 100
        gen x = uniform()
        gen y = uniform()
    end
}

* EXECUTE
main


