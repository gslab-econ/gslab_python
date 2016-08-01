*!version 3.1  12Mar2014

capture program drop rdbinselect
program define rdbinselect, eclass
	syntax anything [if] [, c(real 0) p(real 4) scale(real 1) scalel(real 1) scaler(real 1) numbinl(real 1) numbinr(real 1) lowerend(string) upperend(string) generate(string) hide * graph_options(string) ]

	marksample touse

	tokenize "`anything'"
	local y `1'
	local x `2'
	local n_sim = 10000

	tokenize `generate'	
	local w : word count `generate'
	if `w' == 1 {
		confirm new var `1'	
		local genid `"`1'"'
		local nsave 1
	}
	if `w' == 2 {
		confirm new var `1'	
		confirm new var `2'
		local genid `"`1'"'
		local genmeanx `"`2'"'
		local nsave 2
	}
	if `w' == 3 {
		confirm new var `1'	
		confirm new var `2'
		confirm new var `3'
		local genid    `"`1'"'
		local genmeanx `"`2'"'
		local genmeany `"`3'"'
		local nsave 3
	}

	tempvar x_l x_r y_l y_r orig_order miss sample
	qui gen `orig_order' = _n
	*mata: orig_order = st_data(.,("orig_order"),  0)
	*qui drop orig_order

	if "`lowerend'"=="" {
		qui su `x'
		local lowerend = r(min)
	}
	if "`upperend'"=="" {
		qui su `x'
		local upperend = r(max)
	}
	local x_low = "`lowerend'"
	local x_upp = "`upperend'"

	qui gen `sample'=.
	qui replace `sample'=_n if `y'!=. & `x'!=. & `x'>=`x_low' & `x'<=`x_upp'
	qui count
	local size=r(N)

	preserve

	sort `sample' `y' `x'

	qui keep if `touse'
	qui drop if `y'==. | `x'==.
	qui drop if `x'<`x_low' 
	qui drop if `x'>`x_upp'

	qui gen `x_l' = `x' if `x'<`c'
	qui gen `y_l' = `y' if `x'<`c'
	qui gen `x_r' = `x' if `x'>=`c'
	qui gen `y_r' = `y' if `x'>=`c'

	qui su `x'
	local x_min = r(min)
	local x_max = r(max)
	qui su `x_l' 
	local range_l = abs(r(max) - r(min))
	local n_l = r(N)
	qui su `x_r' 
	local range_r = abs(r(max) - r(min))
	local n_r = r(N)


	**************************** ERRORS
	if (`c'<=`x_min' | `c'>=`x_max'){
	 di "{err}{cmd:c()} should be set within the range of `x'"  
	 exit 125
	}

	if ("`p'"<="0" ){
	 di "{err}{cmd:p()} should be a positive integer"  
	 exit 411
	}

	if ( "`scale'"<="0" | "`scalel'"<="0" | "`scaler'"<="0" | "`numbinl'"<="0" | "`numbinr'"<="0"){
	 di "{err}{cmd:scale()}, {cmd:scalel()}, {cmd:scaler()}, {cmd:numbinl()} and {cmd:numbinr()} should be positive integers"  
	 exit 411
	}

	if ( ("`scale'"!="1" & "`scalel'"!="1") |  ("`scale'"!="1" & "`scaler'"!="1")){
	     di "{err}{cmd:scale()} cannot be combined with either {cmd:scalel()} or {cmd:scaler()}"
         exit 498
	}
	
	if ( ("`scale'"!="1" | "`scalel'"!="1" | "`scaler'"!="1") &  ("`numbinl'"!="1" | "`numbinr'"!="1")){
	     di "{err}{cmd:scale()}, {cmd:scalel()} and {cmd:scaler()} cannot be combined with either {cmd:numbinl()} or {cmd:numbinr()}"
         exit 498
	}
	
	local p_round   = round(`p')/`p'
	local p_scale   = round(`scale')/`scale'
	local p_scalel  = round(`scalel')/`scalel'
	local p_scaler  = round(`scaler')/`scaler'
	local p_numbinl = round(`numbinl')/`numbinl'
	local p_numbinr = round(`numbinr')/`numbinr'

	if (`p_round'!=1 | `p_scale'!=1 | `p_scalel'!=1 | `p_scaler'!=1 | `p_numbinl'!=1 | `p_numbinr'!=1 ) {
	 di "{err}{cmd:p()}, {cmd:scale()}, {cmd:scalel()}, {cmd:scaler()}, {cmd:numbinl()} and {cmd:numbinr()} should be integers"  
	 exit 126
	}

	if ((`numbinl'!=1 & `numbinr'==1 ) | (`numbinr'!=1 & `numbinl'==1 )) {
	     di "{err}both {cmd:numbinl()} and {cmd:numbinr()} should be set"
         exit 498
	}
	
	
	if ( `scale'>1 & `scalel'==1 & `scaler'==1){
		local scalel = `scale'
		local scaler = `scale'
	}
	
	mata{
	
	y_l = st_data(.,("`y_l'"), 0)
	x_l = st_data(.,("`x_l'"), 0)
	y_r = st_data(.,("`y_r'"), 0)
	x_r = st_data(.,("`x_r'"), 0)
	
	
	allsample=`size'
	usesample=`n_l'+`n_r'
	p1 = `p' + 1
	

	rp_l = J(`n_l',p1,.)
	rp_r = J(`n_r',p1,.)
	for (j=1; j<=p1; j++) {
		rp_l[.,j] = x_l:^(j-1)
		rp_r[.,j] = x_r:^(j-1)
	}
	gamma_p1_l = invsym(cross(rp_l,rp_l))*cross(rp_l,y_l)		
	gamma_p2_l = invsym(cross(rp_l,rp_l))*cross(rp_l,y_l:^2)	
	gamma_p1_r = invsym(cross(rp_r,rp_r))*cross(rp_r,y_r)		
	gamma_p2_r = invsym(cross(rp_r,rp_r))*cross(rp_r,y_r:^2)
		
	*** Bias w/sample
	mu0_p1_l = rp_l*gamma_p1_l
	mu0_p1_r = rp_r*gamma_p1_r
	mu0_p2_l = rp_l*gamma_p2_l
	mu0_p2_r = rp_r*gamma_p2_r
	drp_l = J(`n_l',`p',.)
	drp_r = J(`n_r',`p',.)
	for (j=1; j<=`p'; j++) {
		drp_l[.,j] = j*x_l:^(j-1)
		drp_r[.,j] = j*x_r:^(j-1)
	}
	mu1_hat_l = drp_l*(gamma_p1_l[2::p1])
	mu1_hat_r = drp_r*(gamma_p1_r[2::p1])
	
	if (`numbinl'==1 & `numbinr'==1 ) {


	B_l = ((`range_l'^2)/12)*sum(mu1_hat_l:^2)/(`n_l'+`n_r')
	B_r = ((`range_r'^2)/12)*sum(mu1_hat_r:^2)/(`n_l'+`n_r')
	
	* Integrals
	*rseed(13579)
	*unif_l = `lowerend' :+ (`c' - `lowerend'):*runiform(`n_sim',1)
	*unif_r = `c' :+ (`upperend' - `c'):*runiform(`n_sim',1)
	*rp_ul = rp_ur = J(`n_sim',p1,.)
	*   for (j=1; j<=p1; j++) {
	*		rp_ul[.,j] = unif_l*:^(j-1)
	*		rp_ur[.,j] = unif_r:^(j-1)
	*	}
	*mu0_p1_ul = rp_ul*gamma_p1_l;mu0_p1_ur = rp_ur*gamma_p1_r
	*mu0_p2_ul = rp_ul*gamma_p2_l;mu0_p2_ur = rp_ur*gamma_p2_r
	*sigma2_hat_ul = mu0_p2_ul - (mu0_p1_ul):^2
	*sigma2_hat_ur = mu0_p2_ur - (mu0_p1_ur):^2

	*sigma2_hat_l = mu0_p2_l - (mu0_p1_l):^2
	*sigma2_hat_r = mu0_p2_r - (mu0_p1_r):^2
	*sigma2_hat_l2 = (y_l - mu0_p1_l):^2
	*sigma2_hat_r2 = (y_r - mu0_p1_r):^2

	*V_l = mean(sigma2_hat_ul)
	*V_r = mean(sigma2_hat_ur)

	*V_l2 = mean(sigma2_hat_l)
	*V_r2 = mean(sigma2_hat_r)
	*V_l3 = mean(sigma2_hat_l2)
	*V_r3 = mean(sigma2_hat_r2)
	V_l4 = variance(y_l)
	V_r4 = variance(y_r)

	* Bias Integrated
	*drp_ul = J(`n_sim',`p',.)
	*drp_ur = J(`n_sim',`p',.)
	*for (j=1; j<=`p'; j++) {
	* drp_ul[.,j] = j*unif_l:^(j-1)
	* drp_ur[.,j] = j*unif_r:^(j-1)
	*}
	*mu1_hat_ul = drp_ul*(gamma_p1_l[2::p1])
	*mu1_hat_ur = drp_ur*(gamma_p1_r[2::p1])
	*E_mu_hat_ul = sum(mu1_hat_ul:^2)/(2*`n_sim')
	*E_mu_hat_ur = sum(mu1_hat_ur:^2)/(2*`n_sim')
	*B_ul = ((`range_l'^2)/12)*E_mu_hat_ul
	*B_ur = ((`range_r'^2)/12)*E_mu_hat_ur

	C_l = (2*B_l)/V_l4
	C_r = (2*B_r)/V_r4
	J_star_l_orig = round((C_l*(`n_l'+`n_r'))^(1/3))
	J_star_r_orig = round((C_r*(`n_l'+`n_r'))^(1/3))
	J_star_l = round(`scalel'*J_star_l_orig)
	J_star_r = round(`scaler'*J_star_r_orig)
	st_numscalar("J_star_l", J_star_l[1,1])
	st_numscalar("J_star_r", J_star_r[1,1])
	st_numscalar("J_star_l_orig", J_star_l_orig[1,1])
	st_numscalar("J_star_r_orig", J_star_r_orig[1,1])
	
	}		
	}
	

	
if (`numbinl'>1 & `numbinr'>1 ) {
	local J_star_l = `numbinl'
	local J_star_r = `numbinr'
	
	scalar J_star_l = `J_star_l'
	scalar J_star_r = `J_star_r'
	scalar J_star_l_orig = `J_star_l'
	scalar J_star_r_orig = `J_star_r'

}

*	ereturn clear
*	ereturn scalar J_star_l = `J_star_l'
*	ereturn scalar J_star_r = `J_star_r'


	local jump = `range_l'/J_star_l
	
	qui su `x_l'
	local x_min = r(min)
	local x_max = r(max)
	qui gen bin_x =.
	qui replace bin_x = -J_star_l  if `x_l' <= (`x_min' + `jump') & `x_l'!=.
	qui replace bin_x = -1         if `x_l' >= (`x_max' - `jump') & `x_l'!=.
	local K = J_star_l-1
	forvalues k = 2 (1) `K' {
		qui replace bin_x = -J_star_l+`k' if  `x_l' <= `x_min'+`k'*`jump' & `x_l' > `x_min'+(`k'-1)*`jump' & `x_l'!=.
	}

	local jump = `range_r'/J_star_r
	qui su `x_r'
	local x_min = r(min)
	local x_max = r(max)
	qui replace bin_x = 1        if `x_r' <= (`x_min' + `jump') & `x_r'!=.
	qui replace bin_x = J_star_r if `x_r' >= (`x_max' - `jump') & `x_r'!=.
	local K = J_star_r-1
	forvalues k = 2 (1) `K' {
		qui replace bin_x = `k' if  `x_r' <= `x_min'+`k'*`jump' & `x_r' > `x_min'+(`k'-1)*`jump' & `x_r'!=.
	}

	qui gen bin_xmean=.
	qui gen bin_ymean=.
	local J_star_l = J_star_l
	local J_star_r = J_star_r
	
	forvalues k = 1 (1) `J_star_l' {
		qui su `x_l' if bin_x == -`k'
		qui replace bin_xmean=r(mean) if bin_x == -`k'
		qui su `y_l' if bin_x == -`k'
		if (r(N)==1){
			qui replace bin_ymean=r(mean) if bin_x == -`k'
		}
		if (r(N)>1){
			qui reg `y_l' if bin_x == -`k' 
			qui replace bin_ymean=_b[_cons] if bin_x == -`k' 
		}
	}

	forvalues k = 1 (1) `J_star_r' {
		qui su `x_r' if bin_x == `k'
		qui replace bin_xmean=r(mean) if bin_x == `k'
		qui su `y_r' if bin_x == `k'
		if (r(N)==1){
			qui replace bin_ymean=r(mean) if bin_x == `k'
		}
		if (r(N)>1){
			qui reg `y_r' if bin_x == `k' 
			qui replace bin_ymean=_b[_cons] if bin_x == `k' 
		}
	}


	
	mata{
	x_sup = x_l \ x_r
	y_hat = mu0_p1_l \ mu0_p1_r
	bin_x     = st_data(.,("bin_x"), 0)
	bin_xmean = st_data(.,("bin_xmean"), 0)
	bin_ymean = st_data(.,("bin_ymean"), 0)
	st_store(., st_addvar("float", "x_sup"), x_sup)
	st_store(., st_addvar("float", "y_hat"), y_hat)
	*st_numscalar("J_star_l", J_star_l[1,1])
	*st_numscalar("J_star_r", J_star_r[1,1])
	*st_numscalar("J_star_l_orig", J_star_l_orig[1,1])
	*st_numscalar("J_star_r_orig", J_star_r_orig[1,1])
	st_matrix("gamma_p1_l", gamma_p1_l)
	st_matrix("gamma_p1_r", gamma_p1_r)
	}

	
	
	ereturn clear
	ereturn scalar J_star_l         = J_star_l
	ereturn scalar J_star_r         = J_star_r
	ereturn scalar J_star_l_orig    = J_star_l_orig
	ereturn scalar J_star_r_orig    = J_star_r_orig
	ereturn scalar binlength_l      = `range_l'/J_star_l
	ereturn scalar binlength_r      = `range_r'/J_star_r
	ereturn scalar binlength_l_orig = `range_l'/J_star_l_orig
	ereturn scalar binlength_r_orig = `range_r'/J_star_r_orig
	ereturn matrix gamma_p1_l = gamma_p1_l
	ereturn matrix gamma_p1_r = gamma_p1_r
	cap drop x_sup_l
	cap drop x_sup_r
	cap drop y_hat_l 
	cap drop y_hat_r
	
	disp ""
	disp in smcl in gr "Number of bins for RD Estimates" 
	disp ""
	disp in smcl in gr "{ralign 17: Cutoff c = `c'}"  _col(18) " {c |} " _col(19) in gr "Left of " in yellow "c"        _col(35) in gr "Right of " in yellow "c" 
	disp in smcl in gr "{hline 18}{c +}{hline 30}"                                                                                
	disp in smcl in gr "{ralign 17:Number of obs}"   _col(18) " {c |} " _col(18) as result %7.0f `n_l'                 _col(38) %7.0f  `n_r'
	disp in smcl in gr "{ralign 17:Poly. Order}"     _col(18) " {c |} " _col(18) as result %7.0f `p'                   _col(38) %7.0f  `p'
	disp in smcl in gr "{ralign 17:Number of bins}"  _col(18) " {c |} " _col(18) as result %7.0f e(J_star_l_orig)      _col(38) %7.0f  e(J_star_r_orig)
	disp in smcl in gr "{ralign 17:Bin Length}"      _col(18) " {c |} " _col(18) as result %7.3f e(binlength_l_orig)   _col(38) %7.3f  e(binlength_r_orig)
	if ("`scale'"~="1" | "`scalel'"~="1" | "`scaler'"~="1") {
		disp in smcl in gr "{hline 18}{c +}{hline 30}"                                                                                
		disp in smcl in gr "{ralign 17:Scale}"           _col(18) " {c |} " _col(18) as result %7.0f `scalel'              _col(38) %7.0f  `scaler'
		disp in smcl in gr "{ralign 17:Number of bins}"  _col(18) " {c |} " _col(18) as result %7.0f e(J_star_l)           _col(38) %7.0f  e(J_star_r)
		disp in smcl in gr "{ralign 17:Bin Length}"      _col(18) " {c |} " _col(18) as result %7.3f e(binlength_l)        _col(38) %7.3f  e(binlength_r)
	}
	disp ""
	if ("`hide'"=="") {
		twoway (scatter bin_ymean bin_xmean, sort msize(small)  mcolor(gs10)) (line y_hat x_sup if x_sup<`c', lcolor(black) sort lwidth(medthin) lpattern(solid) ) (line y_hat x_sup if x_sup>=`c', lcolor(black) sort lwidth(medthin) lpattern(solid) )  , ///
		xline(`c', lcolor(black) lwidth(medthin)) xscale(r(`x_low' `x_up')) title("Regression Function Fit", color(gs0))  ///
		legend(cols(2) order(1 "Sample average within bin" 2 "`p'th order global polynomial" )) `graph_options'
	}
	
	*xtitle("`x'") ytitle("`y'")
	*
	*if "`savefig'" != "" {
	*saving("Fig1.gph", replace)
	*}
	restore
	sort `sample'
	mata{

	if ("`nsave'"=="1") {
		if (allsample!=usesample){
			miss = J(allsample-usesample,1, .)
			bin_x=(bin_x',miss')'
	}

	st_store(., st_addvar("float", "`genid'"), bin_x)
	}

	if ("`nsave'"=="2") {
		if (allsample!=usesample){
			miss = J(allsample-usesample,1, .)
			bin_x=(bin_x',miss')'
			bin_xmean=(bin_xmean',miss')'
		}
		st_store(., st_addvar("float", "`genid'"),    bin_x )
		st_store(., st_addvar("float", "`genmeanx'"), bin_xmean )
	}

	if ("`nsave'"=="3") {
		if (allsample!=usesample){
			miss = J(allsample-usesample,1, .)
			bin_x=(bin_x',miss')'
			bin_xmean=(bin_xmean',miss')'
			bin_ymean=(bin_ymean',miss')'
		}
		st_store(., st_addvar("float", "`genid'"), bin_x )
		st_store(., st_addvar("float", "`genmeanx'"), bin_xmean )
		st_store(., st_addvar("float", "`genmeany'"), bin_ymean )
		*qui gen `genid' = .
		*mata: st_store(., "`genid'", bin_x, )
		*qui gen bin_xmean = .
		*mata: st_store(., "bin_xmean", bin_xmean)
		*qui ren bin_xmean `genmeanx'
		*qui gen bin_ymean = .
		*mata: st_store(., "bin_ymean", bin_ymean)
		*qui ren bin_ymean `genmeany'
		}
	}
	sort `orig_order'
	qui drop `sample' `orig_order'
	mata mata clear

end


