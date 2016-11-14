/**********************************************************
 *
 * BENCHMARK.ADO: Simulates data and runs analyses that we 
 * might expect from a highly computation Stata script. 
 * Logs output time as I/O, Paralleled, or Serial.
 *
 * I/O time includes data generation, save/use, merge, write, and insheet.
 * Parallel time includes regress and probit.
 * Serial time includes xtreg and areg.
 *
 **********************************************************/

cap program drop benchmark

program define benchmark

	version 10
	set trace off
	set more off
	
	display "Running test code..."
	
	clear
	timer clear
	local numobs 1000000
	local numvars 10
	local regs 60
	tempfile firstdata finaldata

	****************************************************************
	** generate/manipulate data **
	****************************************************************
	timer on 1

	local times 1000
	local groups=`numobs'/`times'
	
	**GENERATE DATA
	clear
	quietly set obs `times'
	gen time = _n
	quietly expand `groups'
	sort time
	gen group = mod(_n, `groups')

	forval i=1(1)`numvars' {
		gen var`i' = uniform() * 1000000
	}
	gen outcome = floor(uniform()*2)
	quietly save `firstdata', replace

	**MERGE DATA 
	clear
	quietly set obs `times'
	gen time = _n
	quietly expand `groups'
	sort time
	gen group = mod(_n, `groups')

	forval i=1(1)`numvars' {
		gen var`i'_2 = uniform() * 10000
		gen var`i'_3 = uniform() * 100
	}
	quietly mmerge time group using `firstdata', type(1:1) unmatched(none) 
	quietly save `finaldata', replace

	
	**WRITE THE DATA
	quietly file open OUTDATA using "tempdata.txt", write replace
	forval i = 1(1)`numobs' {
		local time=time[`i']
		local group=group[`i']
		local outcome=outcome[`i']
		file write OUTDATA "`time'" _tab "`group'" _tab "`outcome'" _n
	}
	file close OUTDATA
	
	**READ THE DATA
	forval i=1(1)5 {
		quietly insheet using tempdata.txt, clear
	}


	****************************************************************
	** regressions **
	****************************************************************
	use `finaldata', replace
	timer off 1
	
	local eachreg=floor(`regs'/4)

	**PARALLEL
	timer on 5
	*PROBIT
	local regcount 0
	while `regcount' <= `eachreg' {
		forval i=1(1)`numvars' {
			quietly probit outcome var`i' var`i'_2 var`i'_3
			local regcount=`regcount'+1
		}
	}
	timer off 5

	*REGRESS
	timer on 6
	local regcount 0
	while `regcount' <= `eachreg' {
		forval i=1(1)`numvars' {
			quietly regress outcome var`i' var`i'_2 var`i'_3, vce(cluster group)
			local regcount=`regcount'+1
		}
	}
	timer off 6

	**SERIAL
	*XTREG
	quietly xtset group time
	timer on 7
	local xtregcount 0
	while `xtregcount' <= `eachreg' {
		local i 1
		quietly xtreg outcome var`i' var`i'_2 var`i'_3
		local xtregcount=`xtregcount'+1
	}
	timer off 7

	*AREG
	timer on 8
	local aregcount 0
	while `aregcount' <= `eachreg' {
		forval i = 1(1)`numvars' {
			quietly areg outcome var`i' var`i'_2 var`i'_3, a(group)
			local aregcount=`aregcount'+1
		}
	}
	timer off 8

	****************************************************************
	** plots **
	****************************************************************
	timer on 9
	quietly scatter var1 var2
	timer off 9
	timer on 1
	quietly graph export "temp.eps", as(eps) replace
	timer off 1

	window manage close graph

	****************************************************************
	** summarize **
	****************************************************************
	quietly timer list
	local io=`r(t1)'
	local parallel = `r(t5)' + `r(t6)'
	local serial = `r(t7)' + `r(t8)'
	local plots = `r(t9)'
	local total = `io' + `parallel' + `serial' + `plots'
	
	local parallel: display %04.3f `parallel'
	local serial: display %04.3f `serial'
	local plots: display %04.3f `plots'
	local io: display %04.3f `io'
	local total: display %04.3f `total'

	display "IO time: `io's"
	display "Parallelizable processes: `parallel's"
	display "Serial processes: `serial's"
	display "Plotting: `plots's"
	display "-----------------------"
	display "Total: `total's"

	clear
	erase tempdata.txt
	erase temp.eps
end
