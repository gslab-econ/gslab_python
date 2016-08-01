*! version 1.0.4 SRH 12 September 2003
program define gllas_yu
	version 6.0
* simulates y given u
	args y lpred mu what

if "`what'"==""{
	local what = 0
}
* what=0: simulate y
* what=1: mu and y
* what=5: get mu, return in y
* what=6: Pearson residual
* what=7: Deviance residual
* what=8: Anscombe residual

	tempvar zu xb /* linear predictor and zu: r.eff*design matrix for r.eff */

/* ----------------------------------------------------------------------------- */
*quietly{

	* matrix list M_znow
	* disp "ML_y1: $ML_y1 " $ML_y1[$which]
	* matrix list M_ip
	* disp " xb1 = " $HG_xb1[$which]
	* disp " zu = " `zu'[$which]


	if $HG_mlog>0{
		qui gen double `zu' = `lpred' - $HG_xb1
		if `what'<=1{
			simnom `y' `zu'
		}
		if `what'==1|`what'==5{
			nominal `mu' `zu' 5
			if `what'==5{
				qui replace `y' = `mu' 
			}
		}
		if `what'>5{
			nominal `y' `zu' `what'
		}
	}

	if $HG_oth{
		if "$HG_lv"~=""&($HG_nolog>0|$HG_mlog>0){
			local myand $HG_lvolo~=1
		}
		*quietly gen double `mu' = 0
		link "$HG_link" `mu' `lpred' $HG_s1
		if $HG_comp>0{
			compos `mu' "`myand'"
		}
		if `what'==5{
			local ifs
			if "`myand'"~=""{
				local ifs if `myand'
			}
			qui replace `y' = `mu' `ifs'
		}
		else{
			family "$HG_famil" `y' `mu' "`myand'" `what'
		}
	}

	if $HG_nolog>0{
		if `what'<=1{ 
			simord `y' `lpred'
		}
		if `what'==1|`what'==5{
			ordinal `mu' `lpred' 5
			if `what'==5{
				qui replace `y' = `mu' if $HG_lvolo==1
			}
		}
		if `what'>5{
			ordinal `y' `lpred' `what'
		}
	}


	
*} /* qui */
end

program define compos
	version 6.0
	args mu und
	
	tempvar junk mu2
	local ifs
	if "`und'"~=""{
		local ifs if `und'
	}
	qui gen double `junk'=0
	qui gen double `mu2'=.
	local i = 1
	*disp in re "in compos: HG_clus is: $HG_clus"
	while `i'<= $HG_comp{
		*disp in re "in compos: variable HG_co`i' is: ${HG_co`i'}" 
		qui replace `junk' = `mu'*${HG_co`i'}
		qui by $HG_clus: replace `junk' = sum(`junk')
		qui by $HG_clus: replace `mu2' = `junk'[_N] if $HG_ind==`i'
		local i = `i' + 1
	}
	qui replace `mu' = `mu2' `ifs'
end

program define nominal
	version 6.0
	args res zu what
	tempvar mu den

	if $HG_smlog{
		local s $HG_s1
	}
	else{
		local s = 1
	}
	local and
   	if "$HG_lv"~=""{
		local and & $HG_lv == $HG_mlog
		local mlif if $HG_lv == $HG_mlog
	}
	* disp "mlogit link `mlif'"
	if $HG_exp==1&$HG_expf==0{
		qui gen double `mu' = exp(`zu'/`s') if $ML_y1==M_respm[1,1] `and'
		local n=rowsof(M_respm)
		local i=2
		while `i'<=`n'{
			local prev = `i' - 1 
			* disp "xb`prev':" ${HG_xb`prev'}[$which]
			qui replace `mu' = exp( (${HG_xb`prev'} + `zu')/`s') if $ML_y1==M_respm[`i',1] `and'
			local i = `i' + 1
		}

		sort $HG_clus $HG_ind
		qui by $HG_clus: gen double `den'=sum(`mu') `mlif'
		qui by $HG_clus: replace `mu' = `mu'/`den'[_N] `mlif'
		if `what'>5{
			res_b `res' `mu' $HG_ind "`mlif'" " " `what'
			* res_b res mu y if and what	
		}
	}
	else if $HG_exp==1&$HG_expf==1{
		qui gen double `mu' = exp(($HG_xb1 + `zu')/`s') `mlif'
		sort $HG_clus $HG_ind
		qui by $HG_clus: gen double `den'=sum(`mu') `mlif'
		qui by $HG_clus: replace `mu' = `mu'/`den'[_N] `mlif'
		if `what'>5{
			res_b `res' `mu' $HG_ind "`mlif'" " " `what'	
		}
	}
	else{
		tempvar den tmp
		local n=rowsof(M_respm)
		local i = 2
		qui gen double `mu' = 1 if $HG_outc==M_respm[1,1] `mlif'
		qui gen double `den' = 1
		qui gen double `tmp' = 0
		while `i'<= `n'{
			local prev = `i' - 1 
			qui replace `tmp' = exp((${HG_xb`prev'} + `zu')/`s') `mlif'
			qui replace `mu' =  `tmp' if $HG_outc==M_respm[`i',1] `mlif'
			qui replace `den' = `den' + `tmp' `mlif'
			local i = `i' + 1
		}
		qui replace `mu' = `mu'/`den' `mlif'
		if `what'>5{
			tempname y
			qui gen `y' = $ML_y1==$HG_outc
			res_b `res' `mu' `y' "`mlif'" " " `what'	
		}
	}
	if `what'==5{
		qui replace `res' = `mu' `mlif'
	}

end

program define simnom
	version 6.0
	args y zu
	tempvar mu
	tempvar r
	qui gen double `r' = uniform()

	if $HG_smlog{
		local s $HG_s1
	}
	else{
		local s = 1
	}
	local and
   	if "$HG_lv"~=""{
		local and & $HG_lv == $HG_mlog
		local mlif if $HG_lv == $HG_mlog
	}
	* disp "mlogit link `mlif'"
	if $HG_exp==1&$HG_expf==0{
		qui gen double `mu' = `zu'/`s' -ln(-ln(`r')) if $ML_y1==M_respm[1,1] `and'
		local n=rowsof(M_respm)
		local i=2
		while `i'<=`n'{
			local prev = `i' - 1 
			* disp "xb`prev':" ${HG_xb`prev'}[$which]
			qui replace `mu' = (${HG_xb`prev'} + `zu')/`s' -ln(-ln(`r')) if $ML_y1==M_respm[`i',1] `and'
			local i = `i' + 1
		}

		sort $HG_clus `mu'
		qui by $HG_clus: replace `y'=_n==_N `mlif'
	}
	else if $HG_exp==1&$HG_expf==1{
		qui gen double `mu' = ($HG_xb1 + `zu')/`s' -ln(-ln(`r')) `mlif'
		sort $HG_clus `mu'
		qui by $HG_clus: replace `y'=_n==_N  `mlif'
	}
	else{
		tempvar den tmp1 tmp2
		local n=rowsof(M_respm)
		local i = 2
		qui gen double `mu' = 1 if $ML_y1==M_respm[1,1] `mlif'
		qui gen double `den' = 1
		while `i'<= `n'{
			local prev = `i' - 1 
			qui replace `den' = `den' + exp((${HG_xb`prev'} + `zu')/`s') `mlif'
			local i = `i' + 1
		}
		qui gen double `tmp1' = 1/`den'
		qui replace `y' = M_respm[1,1] if `r'<`tmp1' `mlif'
		qui gen double `tmp2' = `tmp1'
		local i = 2
		while `i'< `n'{
			local prev = `i' - 1 
			qui replace `tmp2' = `tmp1' + exp((${HG_xb`prev'} + `zu')/`s')/`den' `mlif'
			qui replace `y' = M_respm[`i',1] if `r'<`tmp2' & `r'>=`tmp1' `mlif'
			qui replace `tmp1' = `tmp2'
			local i = `i' + 1
		}
		qui replace `y' = M_respm[`n',1] if `r'>=`tmp2' `mlif'
	}
end

program define ordinal
	version 6.0
	args res lpred what
	local no = 1
	local xbind = 2
	tempvar mu mu1 l y
	qui gen double `l' = 0
	qui gen double `mu' = 0
	qui gen double `mu1' = 0
	qui gen `y' = 0

	local nxt = 0
	while `no' <= $HG_nolog{
		local olog = M_olog[1,`no']
		local lnk: word `no' of $HG_linko

		if "`lnk'"=="ologit"{
			local func logitl
		}
		else if "`lnk'"=="oprobit"{
			local func probitl
		}
		else if "`lnk'"=="ocll"{
			local func cll
		}
		else if "`lnk'"=="soprobit"{
			local func sprobitl
		}
		local if
   		if "$HG_lv"~=""&$HG_nolog>0{
			local if if $HG_lv == `olog'
		}
		local where = `nxt' + M_above[1,`no'] + 1
		* disp in re "no = `no', where = `where' if = `if' "
		qui replace `l' = -`lpred'+${HG_xb`where'}
		`func' `l' `mu1'
		qui replace `mu' = 1-`mu1' `if'
		if `what'>5{
			local ab = M_above[1,`no']
			local ab = M_resp[`ab',`no']
			* disp in re "replace y = y > `ab' `if' "
			qui replace `y' = $ML_y1 > `ab' `if'
		}
		local n=M_nresp[1,`no']
		local nxt = `nxt' + `n' - 1
		local no = `no' + 1
	} /* next ordinal response */
	if `what'==5{
		qui replace `res' = `mu' if $HG_lvolo==1
	}
	else{
		res_b `res' `mu' `y' "if $HG_lvolo==1" " " `what'
	}
end

program define simord
	version 6.0
	args y lpred
	local no = 1
	local xbind = 2
	tempvar mu p1 p2 r
	qui gen double `p1' = 0
	qui gen double `p2' = 0
	qui gen double `mu' = 0
	qui gen double `r' = uniform()

	while `no' <= $HG_nolog{
		local olog = M_olog[1,`no']
		local lnk: word `no' of $HG_linko

		if "`lnk'"=="ologit"{
			local func logitl
		}
		else if "`lnk'"=="oprobit"{
			local func probitl
		}
		else if "`lnk'"=="ocll"{
			local func cll
		}
		else if "`lnk'"=="soprobit"{
			local func sprobitl
		}
		local and
   		if "$HG_lv"~=""&$HG_nolog>0{
			local and & $HG_lv == `olog'
		}
		* disp "ordinal link is `lnk', and = `and'"
		local n=M_nresp[1,`no']

		* disp  "HG_xb1: " $HG_xb1
		* disp  "xbind = " `xbind'
		* disp  ${HG_xb`xbind'}[$which]

		qui replace `mu' = -`lpred'+${HG_xb`xbind'}
		`func' `mu' `p1'
		qui replace `y' = M_resp[1,`no'] if `r'<`p1' `and'
		qui replace `p2' = `p1'
		local i = 2
		while `i' < `n'{
			local nxt = `xbind' + `i' - 1 

			*disp "response " M_resp[`i',`no']
			*disp "HG_xb`nxt' "  ${HG_xb`nxt'}[$which]

			qui replace `mu' = -`lpred'+${HG_xb`nxt'}
			*disp "mu " `mu'[$which]
			`func' `mu' `p2'

			*disp "p1 and p2: "  `p1'[$which] " " `p2'[$which]

			qui replace `y' = M_resp[`i',`no'] if `r'<`p2' & `r'>=`p1' `and'
			qui replace `p1' = `p2'
			local i = `i' + 1
		}
		local xbind = `xbind' + `n' -1
		qui replace `y' = M_resp[`n',`no'] if `r'>=`p2' `and'
		local no = `no' + 1
	} /* next ordinal response */
	*tab $ML_y1 if `y'==. `and'
end

program define logitl
	version 6.0
	args mu p
	qui replace `p' = 1/(1+exp(-`mu'))
end

program define cll
	version 6.0
	args mu p
	qui replace `p' = 1-exp(-exp(`mu'))
end

program define probitl
	version 6.0
	args mu p
	qui replace `p' = normprob(`mu')
end

program define sprobitl
	version 6.0
	args mu p
	qui replace `p' = normprob(`mu'/$HG_s1)
end


program define link
	version 6.0
* returns mu for requested link
	args which mu lpred s1
	* disp " in link, which is `which' "

	tokenize "`which'"
	local i=1
	local ifs
	while "`1'"~=""{
		if "$HG_lv" ~= ""{
			local oth =  M_oth[1,`i']
			local ifs if $HG_lv==`oth'
		}
		* disp "`1' link `ifs'"
		
		if ("`1'" == "logit"){
			quietly replace `mu' = 1/(1+exp(-`lpred')) `ifs'
		}
		else if ("`1'" == "probit"){
			* disp "doing probit "
			quietly replace `mu' = normprob((`lpred')) `ifs'
		}
		else if ("`1'" == "sprobit"){
			quietly replace `mu' = normprob((`lpred')/`s1') `ifs'
		}
		else if ("`1'" == "log"){
			* disp "doing log "
			quietly replace `mu' = exp(`lpred') `ifs'
		}
		else if ("`1'" == "recip"){
			* disp "doing recip "
			quietly replace `mu' = 1/(`lpred') `ifs'
		}
		else if ("`1'" == "cll"){
			* disp "doing cll "
			quietly replace `mu' = 1 - exp(-exp(`lpred')) `ifs'
		}
		else if ("`1'" == "ident"){
			quietly replace `mu' = `lpred' `ifs'
		}
		local i = `i' + 1
		mac shift
	}

end

program define family
	version 6.0
	args which y mu und what

	tokenize "`which'"
	local i=1
	* disp "in family, und = `und'"
	if "$HG_fv" == ""{
		local ifs
		if "`und'"~=""{local und if `und'}
	}
	else{
		if "`und'"~=""{local und & `und'}
	}
	while "`1'"~=""{
		if "$HG_fv" ~=""{
			local ifs if $HG_fv == `i'
		}
		if ("`1'" == "binom"){
			if `what'==0{
				sim_b `y' `mu' "`ifs'" "`und'"
			}
			else{
				res_b `y' `mu' $ML_y1 "`ifs'" "`und'" `what'
			}
		}
		else if ("`1'" == "poiss"){
			if `what'==0{
				sim_p `y' `mu' "`ifs'" "`und'"
			}
			else{
				res_p `y' `mu' "`ifs'" "`und'" `what'
			}
		}
		else if ("`1'" == "gauss") {
			if `what'==0{
				sim_g `y' `mu' $HG_s1 "`ifs'" "`und'"  
			}
			else{
				res_g `y' `mu' $HG_s1 "`ifs'" "`und'" `what'
			}
		}
		else if ("`1'" == "gamma"){
			if `what'==0{
				sim_ga `y' `mu' $HG_s1 "`ifs'" "`und'"
			}
			else{
				res_ga `y' `mu' $HG_s1 "`ifs'" "`und'" `what'
			}
		}
		else{
			disp in re "unknown family in gllas_yu"
			exit 198
		}
		local i = `i' + 1
		mac shift
	}
end

program define res_g
	version 6.0
	* stolen from glim_p and glim_v1
	args res mu s1 if and what
	if `what'==6{  /* Pearson */
		qui replace `res' = ($ML_y1-`mu')/ `s1' `if' `and'
		exit
	}
	else if `what'==7{ /* Deviance */
		*qui replace `res'= sign($ML_y1-`mu')*sqrt(($ML_y1-`mu')^2/ `s1'^2) `if' `and'
		qui replace `res' = ($ML_y1-`mu')/ `s1' `if' `and'
		exit

	}
	else if `what'==8{ /* Anscombe */
		qui replace `res' = ($ML_y1-`mu')/ `s1' `if' `and'
	}
end

program define res_b
	version 6.0
	* stolen from glim_p and glim_v2
	args res mu y if and what
	tempvar mu_n
	gen double `mu_n' = `mu'*$HG_denom
	if `what'==6{  /* Pearson */
		qui replace `res' = (`y'-`mu_n')/sqrt(`mu_n'*(1-`mu')) `if' `and'
		exit
	}
	else if `what'==7{ /* Deviance */
		*if $HG_denom == 1 {
		*	qui replace `res' = cond(`y', /*
		*		*/ -2*ln(`mu_n'), -2*ln(1-`mu_n')) `if' `and'
		*}
		*else{
			qui replace `res' = cond(`y'>0 & `y'<$HG_denom, /*
				*/ 2*`y'*ln(`y'/`mu_n') + /*
				*/ 2*($HG_denom-`y') * /*
				*/ ln(($HG_denom-`y')/($HG_denom-`mu_n')), /*
				*/ cond(`y'==0, 2*$HG_denom * /*
				*/ ln($HG_denom/($HG_denom-`mu_n')), /*
				*/ 2*`y'*ln(`y'/`mu_n')) ) `if' `and'
		*}

		qui replace `res'= sign(`y'-`mu_n')*sqrt(`res') `if' `and'
		exit

	}
	else if `what'==8{ /* Anscombe */
		tempname b23
		scalar `b23' = exp(2*lngamma(2/3)-lngamma(4/3))
		qui replace `res' = /*
			*/ 1.5*(`y'^(2/3)*_hyp2f1(`y'/$HG_denom) -  /*
			*/      `mu_n'^(2/3)*_hyp2f1(`mu')) /             /*
			*/ ((`mu_n'*(1-`mu'))^(1/6)) `if' `and'
	}
end

program define res_p
	version 6.0
	* stolen from glim_p and glim_v3
	args res mu if and what
	if `what'==6{  /* Pearson */
		qui replace `res' = ($ML_y1-`mu')/sqrt(`mu') `if' `and'
		exit
	}
	else if `what'==7{ /* Deviance */
		qui replace `res' = cond($ML_y1==0, 2*`mu', /*
                         */ 2*($ML_y1*ln($ML_y1/`mu')-($ML_y1-`mu'))) `if' `and'
		qui replace `res'= sign($ML_y1-`mu')*sqrt(`res') `if' `and'
		exit

	}
	else if `what'==8{ /* Anscombe */
		qui replace `res' = 1.5*($ML_y1^(2/3)-`mu'^(2/3)) / `mu'^(1/6) `if' `and'
	}
end

program define res_ga
	version 6.0
	* stolen from glim_p and glim_v4
	args res mu s1 if and what
	if `what'==6{  /* Pearson */
		qui replace `res' = ($ML_y1-`mu')/`mu' `if' `and'
		exit
	}
	else if `what'==7{ /* Deviance */
		qui replace `res' = -2*(ln($ML_y1/`mu') - ($ML_y1-`mu')/`mu')
		qui replace `res'= sign($ML_y1-`mu')*sqrt(`res') `if' `and'
		exit

	}
	else if `what'==8{ /* Anscombe */
		qui replace `res' = 3*($ML_y1^(1/3)-`mu'^(1/3))/`mu'^(1/3) `if' `and'
	}
end
	
program define sim_g
	version 6.0
* returns conditionally normally distributed y
	args y mu s1 if and
	* disp "running famg `if' `and'"
	* disp "s1 = " `s1'[$which] ", mu = " `mu'[$which] " and Y = " $ML_y1[$which]
      	quietly replace `y' = invnorm(uniform())*`s1' + `mu' `if' `and'
end

program define sim_b
	version 6.0
* returns y with binomial distribution conditional on r.effs
* $HG_denom is denominator
	args y mu if and
	* disp "running famb `if' `and'"
	* disp "mu = " `mu'[$which] " and Y = " $ML_y1[$which]
	qui replace `y' = uniform()<`mu' `if' `and'
	qui summ $HG_denom `if' `and'
	if r(N)>0{
		local max = r(max)
		if `max'>1{
			tempvar left
			qui gen int `left' = $HG_denom - 1
			local i = 1
			while `i'<`max'{
				qui replace `y' = `y' + (uniform()<`mu'&`left'>0) `if' `and' 
				qui replace `left' = `left' - 1
				local i = `i' + 1
			}
		}
	}
end

program define sim_p
	version 6.0
* simulates counts from Poisson distribution

	args y mu if and
	*!! disp "running famp `if'"
	* disp in re "if and: `if' `and'"

	tempvar t p 
	qui gen double `t' = 0 `if' `and'
	qui gen int `p' = 0 `if' `and'
	local n = 1
	while `n' >0 {
		qui replace `t' = `t' -ln(1-uniform())/`mu' `if' `and'
		qui replace `p' = `p' + 1 if `t'<1
		qui count if `t' < 1
		local n = r(N)
	}
	quietly replace `y' = `p' `if' `and'
	* disp "done famp"
end

program define sim_ga
	version 6.0
* returns log of gamma density conditional on r.effs
	args y mu s1 if and
	*!! disp "running famg `if'"
	*!! disp "mu = " `mu'[$which]
	*!! disp "s1 = " `s1'[$which]
	qui replace `mu' = 0.0001 if `mu' <= 0
	tempvar nu
	qui gen double `nu' = `s1'^(-2)
      	quietly replace `y' = /*
		*/ `nu'*(ln(`nu')-ln(`mu')) - lngamma(`nu')/*
		*/ + (`nu'-1)*ln($ML_y1) - `nu'*$ML_y1/`mu' `if' `and'
end
