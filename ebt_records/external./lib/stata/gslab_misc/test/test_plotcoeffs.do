version 11
set more off
adopath + ../ado
preliminaries

program main
    cap mkdir temp
    quietly {
        setup_dataset

        testgood test_basic
        testgood test_with_options
        testgood test_with_multiple_regs
        testgood test_with_matrix_notation
        testgood test_with_factor_variables
    }
end

program setup_dataset
    set obs 100
    gen n = round(_n,10)
    gen x1 = round(5*runiform(), 1)
    gen x2 = round(5*runiform(), 1)
    gen x3 = round(5*runiform(), 1)
    gen x4 = round(5*runiform(), 1)
    gen a = _n
    gen y = a*rnormal(1)
    end

program test_basic
    reg y x1 x2 x3 x4
    plotcoeffs x1 x2 x4
end

program test_with_options
    reg y x1 x2 x3 x4
    plotcoeffs x1 x2 x4, graphs(line) label("cows sheep grass") ytitle(Meat Production)
    plotcoeffs x1 x2 x4, graphs(linenose) label("cows sheep grass") ytitle(Meat Production)
    plotcoeffs x1 x2 x4, graphs(connect) label("cows sheep grass") ytitle(Meat Production)
end

program test_with_multiple_regs
    reg y x1 x2 x3
    estimates store reg1
    reg y a x1 x2 x3 x4
    estimates store reg2
    plotcoeffs x1 x2 x3, estimates(reg1 reg2) graphs(err line)
    plotcoeffs x1 x2 x3, scheme(s1color) estimates(reg1 reg2) graphs(connect connect)
end

program test_with_matrix_notation
    foreach V in x1 x2 x3 x4 {
    reg y `V'
    matrix beta = (nullmat(beta)\_b[`V'])
    matrix stderr = nullmat(stderr) \ _se[`V']
    }
    plotcoeffs, b(beta) se(stderr)
    plotcoeffs, b(beta) se(stderr) graphs(line)
end

program test_with_factor_variables
    reg y i.n#c.a
    plotcoeffs i.n#c.a
    plotcoeffs i.n#c.a, graphs(line) label( "1 2 3 4 5 6 7 8 9 10 11") ytitle(Production per year) xtitle(Year)
    reg y i.n#i.a
    plotcoeffs i.n#i.a
    reg y c.n#c.a
    plotcoeffs c.n#c.a
    reg y c.n#i.a
    plotcoeffs c.n#i.a, scheme(s1color) graphs(connect)
    reg y i.n##c.a
    plotcoeffs i.n##c.a, scheme(s1color) graphs(connect)
end


* EXECUTE
main


