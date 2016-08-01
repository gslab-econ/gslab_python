*! version 1.0.6 SRH 1 June 2003
program define gllasim
	version 6.0

	if "`e(cmd)'" ~= "gllamm" { 
		di in red  "gllamm was not the last command"
		exit 301  
	}

	*syntax anything(name=pref id="prefix for variable(s)") [if] [in] 
	syntax newvarname [if] [in] /*
	*/ [,Y U LInpred FAC FSAMPLE MU OUTcome(int -99) ABove(numlist integer) /*
	*/ noOFFset ADOONLY FRom(string) US(string)]
	local nopt = ("`u'"!="") + ("`linpred'"!="") + ("`fac'"!="") + ("`mu'"!="")

	local pref `varlist'
	if `nopt'>1 { 
		disp in re "only one of these option allowed: u, fac, linpred or mu"
		exit 198 
	} 
	local tplv = e(tplv)
	local tprf = e(tprf)
	if `nopt'==0 { 
		local y "y" 
	}

	if "`e(weight)'"~=""&"`y'"~=""{
		disp in re "weight option used in gllamm: It doesn't normally make sense to simulate responses for collapsed data"
	}
	
	if `tplv' < 2{
		if "`u'"~="" | "`fac'"~="" {
			disp in re "u and fac options not valid for 1 level model"
			exit 198
		}
		if "`linpred'"~="" & "`y'"=="" {
			*disp in re "nothing to simulate. use gllapred, xb"
			*exit 198
		}
		
	}

	local vars
	if "`y'"~=""{
		local vars `pref'
		local ysim `pref'
		tempvar musim
		local what=0
		disp in gr "(simulated responses will be stored in `pref')"
		/* check if gamma family used */
		local found = 0
		local fm  "`e(famil)'"
		local num: word count `fm'
		local k = 1
		while `k' < `num'{
			local ll: word `k' of `fm'
			if "`ll'" == "gamma"{
				local found = 1
			}
			local k = `k' + 1
		}
		if `found' == 1{
			disp in re "cannot simulate from gamma yet"
			exit 198
		}
	}

	if "`u'"~=""|"`fac'"~=""{
		local i = 1
		while `i' < `tprf'{
			local vars `vars' `pref'p`i'
			local i = `i' + 1
		}
		disp in gr "(simulated scores will be stored in `vars')"
	}
	if "`linpred'"~=""{
		local vars `vars' `pref'p
		local lpred `pref'p
		disp in gr "(linear predictor will be stored in `pref'p)"
	}
	if "`mu'"~=""{
		local vars `vars' `pref'p
		local musim `pref'p
		tempvar lpred
		tempvar ysim
		if "`y'"~=""{
			local what = 1
		}
		else{
			local what = 5
		}
		disp in gr "(mu will be stored in `pref'p)"
	}
	else if "`y'"~=""{
		tempvar lpred
	}

	if "`offset'"~=""{
		if "`linpred'"==""&"`mu'"==""{
			disp in re "nooffset option only allowed with linpred or mu option"
			exit 198
		}
	}
	if "`us'"~=""& "`u'"~=""{
		disp in re "u option does not make sense with us() option"
		exit 198
	}
	* disp in re "setting macros"

/* check if variables already exist */

	confirm new var `vars'

/* restrict to estimation sample */

	tempvar idno
	gen int `idno' = _n
	preserve
	if "`fsample'"==""{
		qui keep if e(sample)
	}

/* interpret if and in */
	marksample touse, novarlist	
	qui count if `touse'
	if _result(1) <= 1 {
		di in red "insufficient observations"
		exit 2001
	}
	qui keep if `touse'

	tempfile file

/* set all global macros needed by gllam_ll */
	setmacs 0

	if "`adoonly'"!="" {
		global HG_noC=1
		global HG_noC1=1
	}

	*disp "HG_free = " $HG_free

	tempname b
	matrix `b'=e(b)

/* deal with from */
	if "`from'"~=""{
		capture qui matrix list `from'
		local rc=_rc
		if `rc'>1{
			disp in red "`from' not a matrix"
			exit 111
		}
		local ncol = colsof(`from')
		local nrow = rowsof(`from')
		local ncolb = colsof(`b')
		if `ncolb'~=`ncol'{
			disp in re "from matrix has `ncol' columns but should have `ncolb'"
			exit 111
		}
		if `nrow'~=1{
			disp in re "from matrix has more than one row"
			exit 111
		}
		local coln: colnames(`b')
		local cole: coleq(`b')
		matrix `b' = `from'
		matrix colnames `b' = `coln'
		matrix coleq `b' = `cole'
	}
/* deal with outcome() and above() */

	if "`mu'"~=""&$HG_nolog>0{
		if "`above'"==""{
			disp in re "must specify above() option for ordinal responses"
			exit 198
		}
		else{	
			matrix M_above = J(1,$HG_nolog,0)
			local num: word count `above'
			if `num'>1&`num'~=$HG_nolog{
				disp in re "wrong length of numlist in above() option"
				exit 198
			}
			local no = 1
			local k = 1
			while `no' <= $HG_nolog{
				if `num'>1{
					local k = `no'
				}
				local ab: word `k' of `above'
				* disp in re "`no'th ordinal response, above = `ab'"
				local n=M_nresp[1,`no']
				local i = 1
				local found = 0
				while `i'<= `n'&`found'==0{
					if M_resp[`i',`no']==`ab'{
						local found=`i'
						matrix M_above[1,`no']=`i'
					}
					local i = `i' + 1
				}
				if `found'==0{
					disp in re "`ab' not a category for `no'th ordinal response"
					exit 198
				}
				else if `found' == `n'{
					disp in re "`ab' is highest category for `no'th ordinal response"
					exit 198
				}
				local no = `no' + 1
			}
		}
		* noi matrix list M_above
	}
	if "`mu'"~=""&$HG_mlog>0{
		if `outcome'==-99&$HG_exp==0{
			disp in re "must specify outcome() option for nominal responses unless data in expanded form"
			exit 198
		}
		if $HG_exp==0{
			local n=rowsof(M_respm)
			local found = 0
			local i = 1
			while `i'<= `n'&`found'==0{
				if M_respm[`i',1]==`outcome'{
					local found=`i'
				}
				local i = `i' + 1
			}
			if `found'==0{
				disp in re "`outcome not a category of the nominal response'"
				exit 198
			}
			global HG_outc=`outcome'
		}
	}


/* run remcor */
	/* set up names for HG_xb`i' */
	local i = 1
	while (`i' <= $HG_tpff){
		tempname junk
		global HG_xb`i' "`junk'"
		local i = `i' + 1
	}
	/* set up names for HG_s`i' */
	local i = 1
	while (`i'<=$HG_tprf){
		tempname junk
		global HG_s`i' "`junk'"
		local i = `i' + 1
	}

	if $HG_free{  /* names for HG_p`lev'`k' */
		local lev = 2
		while `lev'<=$HG_tplv{
			local npar = M_np[1,`lev']
			if `npar'>0{
				local k = 1
				while `k'<=M_nip[1, `lev']{
					* disp in re "creating HG_p`lev'`k'"
					tempname junk
					global HG_p`lev'`k' "`junk'"
					local k = `k' + 1
				}
			}
			local lev = `lev' + 1
		}		
	}
	qui remcor "`b'" `us'

/* sort out level 1 clus variable */
	local clus `e(clus)'
	global HG_clus `clus'
	tempvar id
	if $HG_exp~=1&$HG_comp==0{
		gen int `id'=_n
		tokenize "`clus'"
		local l= $HG_tplv
		local `l' "`id'"
		global HG_clus "`*'"
		if $HG_tplv>1{
			global HG_clus "`*'"
		}
		else{
			global HG_clus "`1'"
		}	
	}
	* disp "HG_clus: $HG_clus"	

/* deal sith us */
	if "`us'"~="" {
		local j = 1
		while `j'<$HG_tprf{
			capture confirm variable `us'`j'
			if _rc~=0{
				disp in re "variable `us'`j' not found"
				exit 111
			}
			else{
				global HG_U`j' "`us'`j'"
			}
			local j = `j' + 1
		}
	}
	else {
		if $HG_free{
			/* simulate discrete latent variables HG_U`rf'*/
			tempvar f r cum1 cum2
			qui gen double `r' = 0
			qui gen byte `f' = 0
			gen double `cum2' = 0
			gen double `cum1' = 0	
			local sortlst $HG_clus
			local lev = 2
			local rf = 1
			local k = $HG_tplv
			while `lev'<=$HG_tplv{
				/* sortlist etc. */
				tokenize "`sortlst'"
				local `k' " "
				local sortlst "`*'"
				sort $HG_clus
				qui by `sortlst': replace `f' = _n==1
				qui replace `r' = cond(`f'==1,uniform(),.)

				/* define variables HG_V */
				local rf = M_nrfc[2,`lev'-1]
				while `rf'<M_nrfc[2,`lev']{
					tempname junk
					global HG_U`rf' "`junk'"
					qui gen double ${HG_U`rf'} = 0
					local rf = `rf' + 1
				}				

				/* assign values */
				local i=M_nrfc[1,`lev'-1] + 1 
				local np = M_nip[2,`i']
				local npar = M_np[1,`lev']
				local n = M_nip[1,`lev']
				local probs "M_zps`np'"
				*disp "probabilities for level " `lev' " in `probs'"
				*local n = colsof(`probs')

				local i = 1
				while `i'<=`n'{
					qui replace `cum1' = `cum2'
					if `npar'>0{
						qui replace `cum2' = `cum2' + exp(${HG_p`lev'`i'})
					}
					else{
						qui replace `cum2' = `cum2' + exp(`probs'[1,`i'])
					}
					local rf = M_nrfc[2,`lev'-1]
					while `rf'<M_nrfc[2,`lev']{
						local npt = M_nip[2,`rf'+1]
						local zlocs "M_zlc`npt'"
						* disp in re "replace ${HG_U`rf'} = `zlocs'[1,`i'] if r<=" `cum2' "&r> " `cum1'
						qui replace ${HG_U`rf'} = `zlocs'[1,`i'] if `r'<=`cum2'&`r'>`cum1'
						local rf = `rf' + 1
					}
					local i = `i' + 1
				}

				/* set all values in same cluster equal to prediction */
				sort $HG_clus
				local rf = M_nrfc[2,`lev'-1]
				while `rf'<M_nrfc[2,`lev']{
					qui by `sortlst': replace ${HG_U`rf'} = sum( ${HG_U`rf'} )
					local rf = `rf' + 1
				}

				local lev = `lev' + 1
				local k = `k' - 1			
			} 
			if "`u'"~=""|"`fac'"~=""{
				local rf = 1
				while `rf'<$HG_tprf{
					qui gen double `pref'p`rf'=${HG_U`rf'}
					local rf = `rf' + 1
				}
			}
		}
		else{
			/* simulate uncorrelated iid standard normal latent variables HG_U`rf'*/
			tempvar f
			qui gen byte `f' = 0
			local sortlst $HG_clus
			local lev = 2
			local rf = 1
			local k = $HG_tplv
			while `lev'<=$HG_tplv{
				*disp "sort `sortlst'"
				tokenize "`sortlst'"
				local `k' " "
				local sortlst "`*'"
				sort $HG_clus
				qui by `sortlst': replace `f' = _n==1
				while `rf'<M_nrfc[2,`lev']{
					tempname junk
					global HG_U`rf' "`junk'"
					gen double ${HG_U`rf'} = cond(`f'==1,invnorm(uniform()),0)
					qui by `sortlst': replace ${HG_U`rf'} = sum( ${HG_U`rf'} )
					*noi summ ${HG_U`rf'} if `f' == 1
					local rf = `rf' + 1
				}
				local lev = `lev' + 1
				local k = `k' - 1			
			} 

			/* multiply by Cholesky */
			if "`u'"~=""|"`fac'"~=""{
				* noi matrix list CHmat
				local lv = 2
				local rf = 1
				while `lv'<=$HG_tplv{
					local minrf = `rf'
					local maxrf = M_nrfc[2,`lv']
					while `rf'<`maxrf'{
						qui gen double `pref'p`rf'=0
						local rf2 = `minrf'
						while `rf2'<=`rf'{ /* lower diagonal matrix */
							* disp in re "`pref'p`rf' = `pref'p`rf' + CHmat[`rf',`rf2']*HG_U`rf2'"
							qui replace `pref'p`rf'=`pref'p`rf'+CHmat[`rf',`rf2']*${HG_U`rf2'}
							local rf2 = `rf2' + 1
						}
						local rf = `rf' + 1
					}
					local lv = `lv' + 1
				}

			}
		}
	}
	if "`fac'"~=""{
	/* regressions for factors */
		if $HG_bmat{
			* assumes that nocor option was used
			local rf = $HG_tprf - 2
			while `rf'>0{
				local rf2 = `rf'+1
				while `rf2'<=$HG_tprf - 1 { /* upper diagonal matrix */
					*disp in re "`pref'p`rf'=`pref'p`rf'+Bmat[`rf',`rf2']*`pref'p`rf2'"
					qui replace `pref'p`rf'=`pref'p`rf'+Bmat[`rf',`rf2']*`pref'p`rf2'
					local rf2 = `rf2' + 1
				}
				local rf = `rf' -1
			}
		}

		*disp "dealing with geqs"
		tempname junk s1
		local i = 1
		while `i'<=$HG_ngeqs{
			local k = M_ngeqs[1,`i']
			local n = M_ngeqs[2,`i']
			local nxt = M_ngeqs[3,`i']
			*disp "random effect `k'-1 has `n' covariates"
			local nxt2 = `nxt'+`n'-1
			matrix `s1' = `b'[1,`nxt'..`nxt2']
			*matrix list `s1'
			local nxt = `nxt2' + 1
			capture drop `junk'
			matrix score double `junk' = `s1'
			local rf = `k' - 1
			replace `pref'p`rf' = `pref'p`rf' + `junk'
			local i = `i' + 1
		}
	}
	if "`y'"~=""|"`linpred'"~=""|"`mu'"~=""{
		qui gen double `lpred' = $HG_xb1
		local i = 2
		while (`i' <= $HG_tprf){
			local im = `i' - 1
			qui replace `lpred' = `lpred' + ${HG_U`im'} * ${HG_s`i'}
			local i = `i' + 1
		}
		if "`offset'"~=""&"$HG_off"~=""{
			qui replace `lpred' = `lpred' - $HG_off
		}
	}


/* simulate y */

	if "`y'"~=""|"`mu'"~=""{	
/* sort out denom */
		local denom "`e(denom)'"
		if "`denom'"~=""{
			capture confirm variable `denom'
			if _rc>0{
				tempvar den
				qui gen `den'=1
				global HG_denom "`den'"
			}
			else{
				global HG_denom `denom'
			}
		}

/* sort out HG_ind */
		capture confirm variable $HG_ind
		if _rc>0{
			tempname junk
			global HG_ind "`junk'"
			gen $HG_ind=1
		}
/* sort out HG_lvolo */
		if $HG_nolog>0{
			tempname junk
			global HG_lvolo "`junk'"
			qui gen $HG_lvolo = 0
			local no = 1
			if "$HG_lv"==""{
				local olog = M_olog[1,`no']
				qui replace $HG_lvolo = 1		
			}
			else{
				while `no'<=$HG_nolog{
					local olog = M_olog[1,`no']
					qui replace $HG_lvolo = 1 if $HG_lv == `olog'
					local no = `no' + 1
				}
			}
		}

/* call gllas_yu */
		qui gen double `ysim' = .
		qui gen double `musim' = 0
		* disp in re "musim = `musim'"
		sort $HG_clus
		gllas_yu `ysim' `lpred' `musim' `what'
	}
/* delete macros */
	delmacs
	qui keep `idno' `vars'
	qui sort `idno'
	qui save "`file'", replace
	restore
	sort `idno'
	qui merge `idno' using "`file'"
	qui drop _merge

end

program define setmacs
version 6.0
args what
/* sort out depvar */
	local depv "`e(depvar)'"	
	global ML_y1 "`depv'"


/* link and family-related macros */
	global HG_famil "`e(famil)'"
	global HG_link "`e(link)'"
	global HG_linko "`e(linko)'"
	global HG_nolog = `e(nolog)'
	global HG_ethr = `e(ethr)'
	global HG_mlog = `e(mlog)'
	global HG_smlog = `e(smlog)'
	global HG_oth = `e(oth)'
	global HG_lv "`e(lv)'"
	global HG_fv "`e(fv)'"
	capture matrix M_resp=e(mresp)
	capture matrix M_respm=e(mrespm)
	capture matrix M_frld=e(frld)
	capture matrix M_olog=e(olog)
	capture matrix M_oth=e(moth)
	global HG_exp = e(exp)
	global HG_expf = e(expf)
	global HG_ind = "`e(ind)'"
	global HG_lev1 = e(lev1)
	global HG_comp = e(comp)
	capture local coall "`e(coall)'"
	if $HG_comp~=0{
		local i = 1
		while `i'<=$HG_comp{
			local k: word `i' of `coall'
			global HG_co`i' `k'
			local i = `i' + 1
		}
	}

/* set all other global macros */
	global HG_nats = `e(nats)'
	global HG_noC = `e(noC)'
	global HG_noC1 = `e(noC1)'
	global HG_adapt = `e(adapt)'
	global HG_tplv = e(tplv)
	global HG_tpff = `e(tpff)'
	global HG_tpi = `e(tpi)'
	global HG_tprf = e(tprf)
	local tprf = $HG_tprf
	global HG_free = e(free)
	global HG_mult = e(mult)
	global HG_lzpr lzprobg
	global HG_zip zipg
	if $HG_mult{
		global HG_lzpr lzprobm
	}
	else if $HG_free{
		global HG_lzpr lzprobf
		global HG_zip zipf
		matrix M_np=e(mnp)
	}
	global HG_cip = e(cip)
	global which = 9
	global HG_off "`e(offset)'"
	global HG_error = 0
	global HG_cor = `e(cor)'
	global HG_bmat = e(bmat)
	global HG_const = 0
	global HG_ngeqs = e(ngeqs)
	global HG_inter = e(inter)
	global HG_dots = 0
	global HG_init = e(init)
	matrix M_nbrf = e(nbrf)
	matrix M_nrfc = e(nrfc)
	matrix M_ip =  J(1,$HG_tprf+2,1)
	matrix M_nffc =  e(nffc)
	if $HG_tprf<2{ local tprf = 2}
	matrix M_znow =J(1,`tprf'-1,1)
	matrix M_nip = e(nip)
	capture matrix M_ngeqs = e(mngeqs)
	capture matrix M_b=e(mb)
	*capture matrix M_chol = e(chol)
	capture matrix CHmat = e(chol)
	global HG_clus `e(clus)'
local lev = 2
while `lev'<=$HG_tplv{
	local l = M_nrfc[1,`lev'-1] + 1  /* loop */
	local k = M_nrfc[2,`lev'-1] + 1  /* r. eff. */
	while `l'<=M_nrfc[1,`lev']&$HG_tplv>1{
		while `k'<=M_nrfc[2,`lev']{
			*disp "loop " `l' " random effect " `k'
			local w = M_nip[2,`k']

			/* same loc and prob as before? */
			local found = 0
			local ii=M_nrfc[2,1] + 1
			while `ii'<`k'{
				if `w'==M_nip[2,`ii']{
					local found = 1
				}
				local ii = `ii'+1
			}


			capture matrix M_zps`w' =e(zps`w')
			*matrix list M_zps`w'
			if `what'==2{
				if $HG_free {
					if `k' == M_nrfc[1,`l']{
						local nip = colsof(M_zps`w')
						noi disp in gr "prior probabilities"


						local j = 2
						local zz=string(exp(M_zps`w'[1,1]),"%6.0gc")
						if `nip'>1{ 
							local mm "0`zz'"
						}
						else{
							local mm "1"
						}

						while `j'<=`nip'{
							local zz=string(exp(M_zps`w'[1,`j']),"%6.0gc")
							local mm "`mm'" ", " "0`zz'"
							local j = `j' + 1
						}
						disp in gr "    prob: " in ye "`mm'"

						disp " "
					}
				}
				else if `found'==0{
					noi disp in gr "probabilities for `w' quad. points"
					noi matrix list M_zps`w'
					disp " "
				}
			}
			* disp "M_zlc`w'"
			matrix M_zlc`w'=e(zlc`w')
			*matrix list M_zlc`w'
			if `what'==2{
				if $HG_free{
					noi disp in gr "locations for random effect " `w'-1
					local mm=string(M_zlc`w'[1,1],"%6.0gc")
					local j = 2
					while `j'<= `nip'{
						local zz=string(M_zlc`w'[1,`j'],"%6.0gc")
						local mm "`mm'" ", " "`zz'"
						local j = `j' + 1
					}
					disp in gr "     loc: " in ye "`mm'"
					disp " "
				}
				else if `found'==0{
					noi disp in gr "locations for `w' quadrature points"
					noi matrix list M_zlc`w'
					disp " "
				}
				
			}
			local k = `k' + 1
		}
		local l = `l' + 1
	}
local lev = `lev' + 1
}
end

program define delmacs
	version 6.0
/* deletes all global macros and matrices*/
	tempname var
	if "$HG_tplv"==""{
		* macros already gone
		exit
	}
	local nrfold = M_nrfc[2,1]
	local lev = 2
	while (`lev'<=$HG_tplv){
		local i2 = M_nrfc[2,`lev']
		local i1 = `nrfold'+1
		local i = `i1'
		local nrfold = M_nrfc[2,`lev']
		while `i' <= `i2'{
			local n = M_nip[2,`i']
			if `i' <= M_nrfc[1,`lev']{
				capture matrix drop M_zps`n'
			}
			capture matrix drop M_zlc`n'
			local i = `i' + 1
		}
		local lev = `lev' + 1
	}
	if $HG_free==0&$HG_init==0{
		*matrix drop M_chol
		matrix drop CHmat
	}
	matrix drop M_nrfc
	matrix drop M_nffc
	matrix drop M_nbrf
	matrix drop M_ip
	capture matrix drop M_b
	capture matrix drop M_resp
	capture matrix drop M_respm
	capture matrix drop M_frld
	matrix drop M_nip
	matrix drop M_znow
	capture matrix drop M_ngeqs
	capture matrix drop CHmat

	/* globals defined in gllam_ll */
	local i=1
	while (`i'<=$HG_tpff){
		global HG_xb`i'
		local i= `i'+1
	}
	local i = 1
	while (`i'<=$HG_tprf){ 
		global HG_s`i'
		global HG_U`i'
		local i= `i'+1
	}
	local i = 1
	while (`i'<=$HG_tplv){
		global HG_wt`i'
		local i = `i' + 1
	}
	global HG_nats
	global HG_noC
	global HG_noC1
	global HG_adapt
	global HG_fixe
	global HG_lev1
	global HG_bmat
	global HG_tplv 
	global HG_tprf
	global HG_tpi
	global HG_tpff
	global HG_clus
	global HG_weigh
	global which   
	global HG_gauss 
	global HG_free
	global HG_famil 
	global HG_link 
	global HG_nolog
	global HG_olog
	global HG_mlog
	global HG_smlog
	global HG_oth
	global HG_exp
	global HG_expf
	global HG_lv
	global HG_fv
	global HG_nump
	global HG_eqs
	global HG_obs
	global HG_off
	global HG_denom
	global HG_cor
	global HG_s1
	global HG_init
	global HG_ind
	global HG_const
	global HG_dots
	global HG_inter
	global HG_ngeqs
	global HG_ethr
	global HG_mult
	global HG_lzpr
	global HG_zip
	global HG_cip
	global HG_comp
	capture macro drop HG_co*
end

