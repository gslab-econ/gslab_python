version 14
set more off
adopath + ../external/lib/stata/gslab_misc/ado
preliminaries

program main
    setup_ivreg_test
    setup_lpoly_test, degree(0)
    setup_lpoly_test, degree(1)
    setup_lpoly_test, degree(2)
    setup_lpoly_test, degree(3)
end

program setup_ivreg_test
    sysuse auto, clear
    keep price mpg displacement
    outsheet using ../temp/ivreg_test_input.csv, comma replace

    ivregress 2sls price (mpg = displacement), small
    matrix V = e(V)
    matrix b = e(b)
    local dof = e(df_r)

    matrix_to_txt, mat(V) saving(../temp/stata_variance.txt) format(%19.8f) replace
    matrix_to_txt, mat(b) saving(../temp/stata_coeffs.txt) format(%19.8f) replace
    file open fh using ../temp/stata_dof.txt, write replace
    file write fh "`dof'"
    file close fh
end

program setup_lpoly_test
    syntax, degree(int)

    sysuse auto, clear
    keep weight length
    outsheet using ../temp/lpoly_test_input.csv, comma replace

    file open fh using ../temp/bandwidths_degree`degree'.txt, write replace
    local lpoly_opts "degree(`degree') at(length) nograph"
    lpoly weight length, `lpoly_opts' kernel(epanechnikov)  gen(epanechnikov)
    file write fh "epanechnikov" _tab "`r(bwidth)'" _n
    lpoly weight length, `lpoly_opts' kernel(gaussian) gen(gaussian)
    file write fh "gaussian" _tab "`r(bwidth)'" _n
    file close fh

    format epanechnikov gaussian %19.8f
    outsheet epanechnikov gaussian using ../temp/stata_lpoly_degree`degree'.csv, comma replace
end

* EXECUTE
main
