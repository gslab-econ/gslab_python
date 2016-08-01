****************************************************************************************************
*
* TEST_INSERT_TAG.DO
*
****************************************************************************************************

quietly {
    version 11
    set more off
    adopath + ../ado
    preliminaries

    program main
        quietly setup_data
        testgood insert_tag test, open
        testgood regress y x
        testgood insert_tag test, close
        testgood insert_tag test, open prefix(new_prefix)
        testgood regress y x
        testgood insert_tag test, close prefix(new_prefix)
        
        testbad insert_tag, close
        testbad insert_tag test_again, close open
        testbad insert_tag test_again
        testbad insert_tag testtag1 testtag2, open
    end

    program setup_data
        set obs 100
        gen x = uniform()
        gen y = uniform()
    end
}

* EXECUTE
main


