****************************************************************************************************
*
* TESTGOOD.ADO
*
* Unit test utility which confirms that the command entered succeeds.
*
****************************************************************************************************

program testgood
    version 11
    syntax anything(equalok everything), [showoutput *]
    if "`options'"!="" {
        local options ", `options'"
    }
    if "`showoutput'"=="" {
        cap `anything' `options'
    }
    else {
        cap noisily `anything' `options'
    }
    if _rc==0 {
        di "Test passed"
    } 
    else {
        di "Test failed"
        di "    Command: `anything', `options'"
        di "    Result: Error where none expected"
    }
end



