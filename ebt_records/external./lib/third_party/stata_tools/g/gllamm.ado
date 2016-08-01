*! version 2.1.03 27oct2001   (TSJ-2: st0005)
program define gllamm, eclass
	version 6.0
	timer on 1

	if replay() {
                if "`e(cmd)'" ~= "gllamm" {
                        error 301
                }
                Replay `0'
        }
   	else {
		Estimate `0'
	}
   timer off 1
end

program define procstr, eclass
	version 6.0
	tempname  bc b Vc Vr V ll esamp
	noi disp "processing constraints"

	scalar `ll' = e(ll)
	local df = e(df_m)
	local dof
	if "`df'"~="."{
		local dof "dof(`df')"
	}
	local k = e(k)
	capture matrix `Vr' = e(Vr)
	capture robclus "`e(robclus)'"
	matrix  `bc' = e(b)
	matrix `Vc' = e(V)
	local y = "`e(depvar)'"
	matrix `b' = `bc'*M_T' + M_a
	matrix colnames `b' = $HG_coln
	matrix coleq `b' = $HG_cole
	matrix list `b'
	matrix list `Vc'
	matrix `V' = M_T*`Vc'*M_T'
	* disp  "computed V"
	matrix list `V'
	gen `esamp' = 1
	estimates post `b' `V' M_C, $HG_obs `dof' esample(`esamp')
	est local ll =`ll'
	est local k = `k'
	est local depvar "`y'"
	capture est matrix Vr `Vr' 
	capture est local robclus "`robclus'"
	* disp "posted results"
end

program define Replay, eclass
	version 6.0
	syntax [, Level(int $S_level) EFORM ALLC ROBUST CLUSTER(varname) DOTS]
	tempname M_nffc M_nu Vs

	if "`robust'"~=""|"`cluster'"~=""{
		if "`cluster'"~=""{
			local cluster cluster(`cluster')
		}
		gllarob, `cluster' `dots'
	}
	else{
		* disp "reposting model-based standard errors"
		matrix `Vs' = e(Vs)
		estimates repost V =`Vs'
	}
		 

	local const = e(const)
	local tplv = e(tplv)
	matrix `M_nffc' = e(nffc)
	capture matrix `M_nu' = e(nu)
	capture matrix list `M_nu'
	if _rc == 0{
		disp " "
		local j = 1
		while `j' <= `tplv'{
			disp in gr "number of level `j' units = " in ye `M_nu'[1,`j']
			local j = `j' + 1
		}
		disp " "
	}
	local cn = e(cn)
	if `cn'>0{
		disp in gr "Condition Number = " in ye `cn'
	}
	else{
		disp in gr "Condition Number could not be computed"
	}
	disp " "


	* matrix list `M_nffc'
	local numeq = colsof(`M_nffc')
	if `M_nffc'[1,1]==0{local numeq = `numeq' -1}
	if `numeq' > 1{
		local first neq(`numeq')
	}
	else{
		local first first
	}
	if e(ll_0)==.|`M_nffc'[1,1]==0{
		local nohead "noheader"
		if `const'==0{
			disp in gr "gllamm model"
		}
		else{
			disp in gre "gllamm model with constraints:"
			matrix dispCns
		}	
		disp " "
		disp in gr "log likelihood = " in ye e(ll)
	}
	if "`eform'"~=""{
		local eform "eform(exp(b))"
	}
	disp " "
	if "`robust'"~=""{
		if "`cluster'"~=""{
			disp "Robust standard errors for clustered data: `cluster'"
		}
		else{
			disp "Robust standard errors"
		}
	}

	if `M_nffc'[1,1]>0|`numeq'>0 {
		if `const' == 0{
			noi ml display, level(`level') `nohead' `first' `eform'
		}
		else{
			noi estimates display, level(`level') `first' `eform'
		}
	}
	else{
		disp in gr "No fixed effects"
	}
	noi disprand
	if "`allc'"~=""{
		if `const' == 0{
			noi ml display, level(`level') `nohead'
		}
		else{
			noi estimates display, level(`level')
		}
	}	
end

program define Estimate, eclass
	version 6.0
	syntax varlist(min=1) [if] [in] , I(string) [NRf(numlist integer min=1 >=1) Eqs(string) GEqs(string) /*
	*/ noCORrel noCOnstant BMATrix(string) INTER(string)/*
	*/ Family(string) DEnom(varname numeric min=1) Link(string) EXpanded(string) /*
	*/ Offset(varname numeric) Exposure(varname numeric) Basecategory(integer 999)/*
  */ THresh(string) /*
	*/ Weightf(string) LV(varname numeric min=1) FV(varname numeric min=1) S(string) /*
	*/ IP(string) NIp(numlist integer min=1 >=1) ADapt Constraints(numlist) /*
	*/ FRom(string) LONG SEarch(passthru) Gateaux(passthru) LF0(passthru) /*
currently working on these options: 
	*/ ROBust CLuster(varname) PWeight(string) /*
	*/ DOts noLOg TRace noESt EVal Level(int $S_level) INit noDIFficult /*
	*/ EFORM ALLC ADOONLY *]
	tempname mat mnip mnbrf
	global HG_error=0

/* deal with adoonly */

	if "`adoonly'"=="" {
		qui q born
		if $S_1 < 15274 {
			noi di
			noi di as txt /* 
*/ "You must have the Stata executable born on or after " _c
			noi di as res %d 15274 
			noi di as txt " in order to use internal routines"
			noi di "Option " _c
			noi di as input "adoonly" _c
			noi di " assumed."
			noi di
			local adoonly adoonly
		}
	}

	if "`adoonly'"!="" {global HG_noC 1}
	else {global HG_noC 0}


/* deal with trace */

	if "`trace'"!="" { local noi "noisily" }	

/* deal with dots */

	global HG_dots = 0 
	if "`dots'"!="" { 
		global HG_dots = 1
	}	

/* deal with init */

	global HG_init=0
	if "`init'"~="" {global HG_init=1}

/* deal with if and in */
	marksample touse	

	qui count if `touse'
	if _result(1) <= 1 {
		di in red "insufficient observations"
		exit 2001
	}

 /* deal with varlist */
	tokenize `varlist'
	local y "`1'"

	macro shift   /* `*' is list of dependent variables */
	local indep "`*'"

	local num: word count `indep'  /* number of independent variables */

	markout `touse' `y' `indep'
 
/* deal with Link and Family */
	global HG_lev1=0
	global HG_famil
   	global HG_linko
   	global HG_link
	matrix M_olog=(0)
   	capture matrix drop M_oth
	global HG_mlog=0
	global HG_nolog = 0
	global HG_lv
	global HG_fv
	global HG_smlog=0
	global HG_oth = 0
	local l: word count `family'
	if `l'>1 {
		`noi' qui disp  "more than one family" 
		if "`fv'"==""{
			disp in re "need fv option"
			exit 198
		}
		else{
			confirm variable `fv'
			global HG_fv `fv'
		}
		parse "`family'", parse(" ")
		local n=1
		while "`1'"~=""{
			qui count if `fv'==`n'
			if _result(1)==0{
				disp "family `1' not used"
			}
			fm "`1'"
			if "`1'"=="gauss"{
				if $HG_lev1==0{
					global HG_lev1=1
				}
				else if $HG_lev1==2{
					global HG_lev1=3
				}
			}
			else if "`1'"=="gamma"{
				if $HG_lev1==0{
					global HG_lev1=2
				}
				else if $HG_lev1==1{
					global HG_lev1=3
				}
			}
			global HG_famil "$HG_famil $S_2"
			local n = `n'+1
			mac shift
		}
		
	}

	local k: word count `link'
 	local mll = 0
	if `k'>1{
		`noi' qui disp  "more than one link" 
		if "`lv'"==""{
			disp in re "need lv option"
         		exit 198
		}
		else{
			confirm variable `lv'
			global HG_lv `lv'
		}
		parse "`link'", parse(" ")
		local n=1
		while "`1'"~=""{
			qui count if $HG_lv==`n'
			if _result(1)==0{
				disp "link `1' not used"
			}
			lnk "`1'"
			if "$S_1"=="sprobit"|"$S_1"=="soprobit"{
				if $HG_lev1 == 2{
					global HG_lev1 = 3
				}
				else{
					global HG_lev1 = 1
				}
			}
/* nominal */
			if "$S_1"=="mlogit"|"$S_1"=="smlogit"{
				if $HG_mlog>0{
					disp in re "can only have one mlogit link"
					exit 198
				}
				global HG_mlog=`n'
				if "$S_1"=="smlogit"{
					if $HG_lev1 == 2{
						global HG_lev1 = 3
					}
					else{
						global HG_lev1 = 1
					}
				}
				tempvar first
				sort `touse' $HG_lv `y'
				qui by `touse' $HG_lv `y': gen `first' = cond(_n==1,1,0)
				mkmat `y' if `first' == 1 & `touse' & $HG_lv == `n', mat(M_respm)
				if "$S_1"=="smlogit"{global HG_smlog=1}
			}
/* ordinal */
			else if "$S_1"=="ologit"|"$S_1"=="oprobit"|"$S_1"=="ocll"|"$S_1"=="soprobit"{
				global HG_linko "$HG_linko $S_1"
				if $HG_nolog>0{
					* disp "more than one ordinal response"
					matrix M_olog = M_olog,`n'
				}
				else{
					capture matrix drop M_nresp
					matrix M_olog[1,1] = `n'
					tempvar first
					sort `touse' $HG_lv `y'
					qui by `touse' $HG_lv `y': gen `first' = cond(_n==1,1,0)
				}
				mkmat `y' if `first' == 1 & `touse' & $HG_lv == `n', mat(`mat')
				local ll = rowsof(`mat')
				* matrix list `mat'
				* disp "adding `ll' to M_nresp"
				matrix M_nresp = nullmat(M_nresp),`ll'
				if `ll'>`mll'{
					local mll = `ll'
				}
				global HG_nolog = $HG_nolog + 1
			}
/* other */
         		else {
				global HG_link "$HG_link $S_1"
				matrix M_oth = nullmat(M_oth),`n'
				global HG_oth=1
         		}
			local n = `n'+1
			mac shift
		}
		if $HG_nolog>0{
			tempname junk
			global HG_lvolo "`junk'"
			qui gen $HG_lvolo = 0
			matrix M_resp = J(`mll',$HG_nolog,0)
			local no = 1
			local totresp = 0
			while `no'<=$HG_nolog{
				local olog = M_olog[1,`no']
				qui replace $HG_lvolo = 1 if $HG_lv == `olog'
				mkmat `y' if `first' == 1 & `touse' & $HG_lv == `olog', mat(`mat')
				local ii = 1
				while `ii'<= M_nresp[1,`no']{
					* disp "M_resp[`ii',`no'] = mat[`ii',1]"
					matrix M_resp[`ii',`no'] = `mat'[`ii',1]
					local ii = `ii' + 1
				}
				local totresp = `totresp' + M_nresp[1,`no']
				local no = `no' + 1
			}
		}
		if $HG_mlog>0{
			if $HG_nolog==0{
				tempname junk
				global HG_lvolo "`junk'"
				qui gen $HG_lvolo = 0
			}
			qui replace $HG_lvolo = 1 if $HG_lv == $HG_mlog
		}
	}
	else if `k'<=1&`l'<=1{ /* no more than one link and one family given */
		lnkfm "`link'" "`family'"
		global HG_link = "$S_1"
		global HG_famil  = "$S_2"
		if "$HG_link"=="ologit"|"$HG_link"=="oprobit"|"$HG_link"=="ocll"|"$HG_link"=="soprobit"{
		global HG_linko = "$HG_link"
			global HG_nolog = 1
			matrix M_olog[1,1] = 1
		}
		if "$HG_link"=="smlogit"|"$HG_link"=="mlogit"{global HG_mlog=1}
		if "$HG_famil"=="gauss"{global HG_lev1=1}
		if "$HG_famil"=="gamma"{global HG_lev1=2}
		if "$HG_link"=="sprobit"{global HG_lev1=1}
		if "$HG_link"=="soprobit"{global HG_lev1=1}
		if "$HG_link"=="smlogit"{global HG_lev1=1}
		if $HG_mlog==0&$HG_nolog==0{global HG_oth = 1}	
	}
	else if `k'==1{
		lnk "`lnk'"
		global HG_link = "$S_1"
		if "$HG_link"=="ologit"|"$HG_link"=="oprobit"|"$HG_link"=="ocll"|"$HG_link"=="soprobit"{
			global HG_nolog = 1
			matrix M_olog[1,1] = 1
			global HG_linko = "$HG_link"
		}
		if "$HG_link"=="smlogit"|"$HG_link"=="mlogit"{global HG_mlog=1}
		if "$HG_link"=="sprobit"{global HG_lev1=1}
		if "$HG_link"=="smlogit"{global HG_lev1=1}
		if "$HG_link"=="soprobit"{global HG_lev1=1}
		if $HG_mlog==0&$HG_nolog==0{global HG_oth = 1}
	}
	if `l'==1{
		fm "`family'"
		global HG_famil  = "$S_2"
		if "$HG_famil"=="gauss"{global HG_lev1=1}
		if "$HG_famil"=="gamma"{global HG_lev1=2}
		if $HG_mlog==0&$HG_nolog==0{global HG_oth = 1}
	}
	if ((`k'>1&`l'==0)|(`l'>1&`k'==0))&$HG_oth==1{
		disp in re /*
		*/ "both link() and fam() required for multiple links or families"
		exit 198
	}

	markout `touse' $HG_lv $HG_fv


/* deal with noCORrel */
	global HG_cor = 1
	if "`correl'"~=""{
		global HG_cor = 0
	}

/* deal with DEnom */
	global HG_denom
	local f=0
	parse "$HG_famil", parse(" ")
	while "`1'"~=""&`f'==0{
		if "`1'"=="binom"{
			local f=1
		}
		mac shift
	}
	if `f'==1{
		if "`denom'"~=""{
			confirm variable `denom'
			global HG_denom "`denom'"
		}
		else{
			tempvar den
			quietly gen `den'=1
			global HG_denom "`den'"
		}
	}
	else{
		if "`denom'"~=""{
			disp in blue/*
			  */"option denom(`denom') given but binomial family not used"
		}
	} 
	
	markout `touse' `denom'

/* deal with offset */
	global HG_off
	if "`offset'"~=""{
		global HG_off "`offset'"
		local offset "offset(`offset')"
	}
	
	markout `touse' $HG_off

/* deal with ip */
	global HG_gauss = 1
	global HG_free = 0
	global HG_cip = 1
	if "`ip'"=="l"{
		global HG_gauss = 0
	}
	else if "`ip'"=="f"{
		global HG_free = 1
	}
	else if "`ip'"=="fn"{
		global HG_free = 1
		global HG_cip = 0
	}

/* deal with adapt */
	global HG_adapt=0
	if "`adapt'"~=""{
		if $HG_free==1|$HG_gauss==0{
			disp in re "adapt can only be used with ip(g) option"
			exit 198
		}
		global HG_adapt = 1
	}

/* deal with expanded */
	global HG_ind
	global HG_exp = 0
	global HG_expf = 0
	if "`expanded'"~=""{
		global HG_exp = 1
		if $HG_mlog==0{
			disp in re "expanded option only valid with mlogit link"
			exit 198
		}
		local k: word count `expanded'
		if `k'~=3{
			disp in re "expanded option must have three arguments"
		}
		local exp: word 1 of `expanded'
		confirm variable `exp'
		global HG_mlg `exp'
		local k: word 2 of `expanded'
		global HG_ind `k'
		local k: word 3 of `expanded'
		if "`k'"=="o"{
			global HG_expf=1
		}
		else{
			if "$HG_link"~="mlogit"&"$HG_link"~="smlogit"{
				disp in re "must use o in expanded option when combining mlogit with other links"
				exit 198
			}
		}
	}
	else{
		if $HG_mlog>0&"$HG_link"~="mlogit"&"$HG_link"~="smlogit"{
			disp in re "must use expanded option when combining mlogit with other links"
			exit 198
		}
		tempvar ind
		gen `ind' = 1
		global HG_ind `ind'
		global HG_exp = 0
	}
		

/* deal with I (turn list around)*/
	if ("`i'"==""){
		disp in red "i() required"
		global HG_error=1
		exit 198
	}
	local tplv: word count `i'
	global HG_tplv = `tplv'+1
	global HG_clus
	local k = `tplv'
	while `k'>=1{
		local clus: word `k' of `i'
		confirm variable `clus'
		markout `touse' `clus'
		local k=`k'-1
		global HG_clus "$HG_clus `clus'"
	}

	if "`expanded'"==""{
		tempvar id
		gen `id'=_n
		global HG_clus "$HG_clus `id'"
	}
	else{
		 global HG_clus "$HG_clus $HG_mlg" 
	}

/* deal with weightf */
	tempvar wt
	quietly gen double `wt'=1
	local j = 1
	if "`weightf'"==""{
		while (`j'<=$HG_tplv){
			tempname junk
			global HG_wt`j' "`junk'"
			gen double ${HG_wt`j'}=1
			local j = `j' + 1
		}
	}
	else{
		global HG_weigh "`weightf'"
		local found = 0
		while (`j'<=$HG_tplv){
			capture confirm variable `weightf'`j'   /* frequency weight */
			if _rc ~= 0 {
				tempname junk
				global HG_wt`j' "`junk'"
				gen double ${HG_wt`j'}=1
			}
			else{
				tempname junk
				global HG_wt`j' "`junk'"
				gen double ${HG_wt`j'}=`weightf'`j'
				quietly replace `wt'=`wt'*${HG_wt`j'}
				local found = `found' + 1
			}
			local j = `j' + 1
		}
		if `found' == 0 {
			disp in red "weight variables `weightf' not found"
			global HG_error=1
			exit 111
		}
		markout `touse' `weightf'* 
	}

	if "`pweight'"~=""{
		markout `touse' `pweight'* 
	}



/* deal with categorical response variables */

	if "$HG_link" == "mlogit"|"$HG_link" == "smlogit"{
		sort `touse' `y'
		tempvar first
		qui by `touse' `y': gen `first' = cond(_n==1,1,0)
		mkmat `y' if `first' == 1 & `touse', mat(M_respm)
	}
	else if /*
        */ "$HG_link" == "ologit"|"$HG_link" == "ocll"|"$HG_link" == "oprobit"|"$HG_link"=="soprobit"{
		sort `touse' `y'
		tempvar first
		qui by `touse' `y': gen `first' = cond(_n==1,1,0)
		mkmat `y' if `first' == 1 & `touse', mat(M_resp)
		local totresp = rowsof(M_resp)
		matrix M_nresp = (`totresp')
	}

/* deal with base-category */

	if `basecategory'~=999{
		if "$HG_link" ~= "mlogit"&"$HG_link" ~= "smlogit"{
			disp in red  "basecategory ignored because response not nominal"
		}
	}
	if $HG_mlog>0&$HG_expf==0{
		tempname bas
		if `basecategory'==999{
			scalar `bas' = M_respm[1,1]
			matrix `bas' = (`bas')
			local basecat = M_respm[1,1]
			disp in re "`basecat'"
		}
		else{
			matrix `bas' = (`basecategory')
			local basecat = `basecategory'
		}
		
		local n = rowsof(M_respm)
		local j = 1
		local found = 0
		while `j'<=`n'{
			local el = M_respm[`j',1]
			if `el'==`basecat'{
				local found = 1
			}
			else{
				matrix `bas' = `bas'\ `el'
			}
			local j = `j' + 1
		}
		if `found' == 0 {
			disp in re "basecategory = `basecat' not one of the categories"
			exit 198
		}
		matrix M_respm = `bas'
		local el = M_respm[1,1]
		local basecat basecat(`el')	
	}

 
/* deal with noCOns */
	if "`constant'"~=""{
		if $HG_nolog>0{
			disp in re "noconstant option not allowed with ordinal links"
			exit 198
		}
		local cns
	}
	else{
		if $HG_cip ==0{
			disp in re "are you sureyou need a constant with ip(fn) option?"
		}

		local num=`num'+1
		local cns "_cons"
	}
	matrix M_nffc=(`num')

	
	if `num'>0 {
		global HG_fixe (`y': `y'=`indep', `constant')
		local dep
	}
	else{
		global HG_fixe
		local dep "`y'="
	}

/* fixed effects matrix */

	if `num' > 0 {
		matrix M_initf=J(1,`num',0)
		matrix coleq M_initf=`y'
		matrix colnames M_initf=`indep' `cns'
	}

	if $HG_nolog==0{
		if "`thresh'"~=""{ disp in re "thresh option ignored" }
	}
	else if $HG_nolog>0{

		if "`thresh'"~=""{
			local k: word count `thresh'
			if `k'~=$HG_nolog{
				disp in re "number of threshold equations should be " $HG_nolog
				exit 198
			}
		}
		global HG_fixe
		local n = rowsof(M_resp)
		matrix M_nffc[1,1] = `num'-1
		if `num'>1{
			global HG_fixe (`y': `y'=`indep', nocons)
			matrix `mat' = M_initf[1,1..`num'-1]
			local ce: coleq(`mat')
			local cn `indep'
			matrix M_initf=J(1,`num'-1,0)
		}
      		else{
         		capture matrix drop M_initf
      		}		
		local el = M_nffc[1,1]
		local ii = 1
		local nxt = M_nffc[1,1] + 1
		local ntr = 1
		local vars
		local rhs "_cons"
		while `ii'<= $HG_nolog{
			local j = 1
			if "`thresh'"~=""{
				local eqnam: word `ii' of `thresh'
				eq ? "`eqnam'"
				local vars "$S_1"
				markout `touse' `vars'
				local ntr: word count `vars'
				local ntr = `ntr' + 1
				local rhs "`vars' _cons"
			}
			while `j'< M_nresp[1,`ii']{
				* disp "`ii'th ordinal response, level `j'"
				local el = `el' + `ntr'
				matrix M_nffc = M_nffc, `el'
				matrix `mat'=J(1,`ntr',0)
				matrix coleq `mat' =  _cut`ii'`j'
				local cee: coleq(`mat')
				local ce `ce' `cee'
				local cn `cn' `rhs'
				global HG_fixe $HG_fixe (_cut`ii'`j':`vars')
				if `j' == 1 & `ii'==1 & `num' == 1{
					global HG_fixe (_cut`ii'`j':`y'= `vars')
				}
				local j = `j' + 1
				matrix `mat'[1,`ntr'] =  `j' - (M_nresp[1,`ii']+1)/2
				matrix M_initf = nullmat(M_initf), `mat'
				local nxt = `nxt' + 1
			}
			local ii = `ii' + 1
		}
		matrix colnames M_initf=`cn'
		matrix coleq M_initf=`ce'
      		* matrix list M_initf
	}

	if ($HG_mlog>0)&$HG_expf==0{
		global HG_fixe
		local n = rowsof(M_respm)
		matrix `bas'=M_initf
		matrix drop M_initf
		matrix drop M_nffc
		local j = 2
		while `j'<=`n'{
			local  el = M_respm[`j',1]
			matrix coleq `bas' = c`el'
			matrix M_initf = nullmat(M_initf), `bas'
			matrix M_nffc = nullmat(M_nffc), (`j'-1)*`num'
			if `j' == 2{
				global HG_fixe $HG_fixe ( c`el':`y' = `indep', `constant')
			}
			else{ 
				global HG_fixe $HG_fixe ( c`el':`indep', `constant')
			}
			local j = `j' + 1
		}
		local num = `num'*(`n' - 1)		
	}

	* matrix list M_nffc
	* matrix list M_initf


/* display information */
	quietly `noi'{
		disp " "
		disp in gr "General model information"
		disp in gr "-----------------------------------------------------------------------------"
		disp in gr "dependent variable:" in ye "         `y'"	
      if $HG_oth{
         disp in gr "family:" in ye "                     $HG_famil"
         disp in gr "link:" in  ye "                       $HG_link"
      }
      if "$HG_linko"~=""{
         disp in gr "ordinal responses:" in ye "         $HG_linko"
      }
      if $HG_mlog>0{
         if $HG_smlog==1 {
            disp in gr "nominal responses:" in ye "         smlogit"
         }
         else{
            disp in gr "nominal responses:" in ye "          mlogit"
         }
      }
		if "$HG_denom"~=""{
			if "`denom'"~=""{
		     		disp in gr "denominator:" in ye "                `denom'"
			}
			else{
				disp in gr "denominator:" in ye "                1"
			}
		}
		if "`offset'"~=""{
			disp in gr "offset:" in ye "                     $HG_off"
		}
		local m = colsof(M_nffc)
		if `m'==1&M_nffc[1,1]>0{
			local cuts: colnames(M_initf)
			disp in gr "equation for fixed effects " in ye " `cuts'"
		}
		else if `m'==1{
			disp in gr "equation for fixed effects " in ye " none"
		}
		else{
			disp in gr "equations for fixed effects"
			local j = 1
			local nxt = 1
			local prev = 0
			while `j'<=`m'{
				local n = M_nffc[1,`j'] - `prev'
				if `n'>0{
					local prev = M_nffc[1,`j']
					matrix `mat' = M_initf[1,`nxt'..`nxt'+`n'-1]
					local nxt = `nxt' + `n'
					local ce: coleq(`mat')
					local ce: word 1 of `ce'
					local cn: colnames(`mat')
			                disp in gr "                           `ce': " in ye " `cn'"
				}
				local j = `j' + 1
			}
		disp " "
	}

/* deal with inter */

	global HG_inter = 0
	if "`inter'"~=""{
		global HG_inter=1
		local j: word count `inter'
		if `j'~=2{
			disp in red "inter should have two arguments"
			exit 198
		}
		local j: word 1 of `inter'
		capture confirm number `j'
		if _rc>0{
			disp in red "arguments of inter must be numbers"
			exit 198
		}
		global HG_l = `j'
		local j: word 2 of `inter'
		capture confirm number `j'
		if _rc>0{
			disp in red "arguments of inter must be numbers"
			exit 198
		}
		global HG_r = `j'
	}

/* initialise macros */
	quietly `noi' initmacs "`nrf'" "`nip'" "`eqs'" "`geqs'" "`s'" "`bmatrix'" "`touse'" "`dep'"
	qui count if `touse'
	if _result(1) <= 1 {
		di in red "insufficient observations"
		exit 2001
	}

			
/* deal with noESt */
	if "`est'"~=""{
		exit 0
	}
/* only use observations satisfying if and in and having nonmissing values */
	preserve
/*
	tempvar esamp
	qui gen `esamp' = cond(`touse',1,0)
	global HG_esamp "`esamp'"
*/

	quietly keep if `touse'

/* work out number of units at each level  */

	qui summ `wt' if `touse', meanonly
	local lobs = r(sum)
	tempvar cw f
	qui gen double `cw' = `wt'
	qui gen `f' = 1
	matrix M_nu=J(1,$HG_tplv,0)
	matrix M_nu[1,1]=`lobs'
	local sortlst $HG_clus
	local j = 1
	local k = $HG_tplv
	quietly `noi' disp in gr "number of level 1 units = " in ye `lobs' 
	while `j'<$HG_tplv{
		* disp "sort `sortlst'"
		sort `sortlst'
		tokenize "`sortlst'"
		local `k' " "
		local sortlst "`*'"
		* disp "replace cw = cw/wt`j'"
		qui replace `cw' = `cw'/${HG_wt`j'}
		* disp "by `sortlst': replace f=_n==1"
		qui by `sortlst': replace `f' = _n==1
		qui summ `cw' if `f' ==1, meanonly
		local lobs = r(sum)
		quietly `noi' disp in gr "number of level " `j'+1 " units = " in ye `lobs' 
		matrix M_nu[1,`j'+1] = `lobs'
		local j = `j' + 1
		local k = `k' - 1			
	} 
	disp " "
}

/* deal with probability weights */
	if "`pweight'"~=""{
		tempname wtp
		global HG_pwt "`pweight'"
		quietly gen double `wtp' = 1
		local j = 1
		local found = 0
		while (`j'<=$HG_tplv){
			capture confirm variable `pweight'`j'   /* frequency weight */
			if _rc == 0 {
				quietly replace ${HG_wt`j'}=${HG_wt`j'}*`pweight'`j'
				quietly replace `wtp'=`wtp'*`pweight'`j'
				local found = `found' + 1
			}
			local j = `j' + 1
		}
		if `found' == 0 {
			disp in red "probability weight variables not found"
			global HG_error=1
			exit 111
		}
	}

	* check if weights are integer

	qui cap summ `y' if `touse' [fweight=`wt'], meanonly
	if _rc>0 {
		global HG_obs
		local ftype pweight
		disp in blue "weights are non-integer"
	}
	else {
		global HG_obs obs(`lobs')
		local ftype fweight
	}
	if "`pweight'"~=""{
		quietly replace `wt' = `wt'*`wtp'
		local ftype pweight	
		
	}

/* deal with from */
	if "`from'"~=""{
		capture qui matrix list `from'
		local rc=_rc
		if `rc'>1{
			disp in red "`from' not a matrix"
			exit 111
		}
	}

/* deal with constraints (and from long)*/

	global HG_const = 0
	if "`constra'"~=""{
		tempname b V
		global HG_const = 1
		matrix `b' = nullmat(M_initf), nullmat(M_initr)
		if "`from'"~=""& "`long'"~=""{
			local nb = colsof(`b')
			local nf = colsof("`from'")
			* disp "nb = " `nb'
			* disp "nf = " `nf'
			if "`gateaux'"~=""{
				local tprf=M_nrfc[2,$HG_tplv]-M_nrfc[2,$HG_tplv-1]
				local nnf = `nf' + `tprf' + 1
				if `nnf'~=`nb'{
					disp in re "from matrix has `nf' columns and should have " `nb'-`tprf'-1
					exit 198
				}
				matrix `from' = `from',`b'[1,`nf'+1...]
			}	
			else if `nb'~=`nf'{
				disp in re "from matrix has `nf' columns and should have `nb'"
				exit 198
			}
			matrix `b' = `from'
			*matrix list `b'
		}
		global HG_coln: colnames(`b')
		global HG_cole: coleq(`b')
		* matrix list `b'
		matrix `V' = `b''*`b'
		estimates post `b' `V'
		matrix `b' = e(b)
		matrix makeCns `constra'
		qui `noi' disp in gr "Constraints:"
		qui `noi' matrix dispCns
		qui `noi' disp " "
		matcproc M_T M_a M_C
		matrix M_inshrt = `b'*M_T
		local n = colsof(M_inshrt)
		qui `noi' disp "estimating `n' parameters"
		local i = 1
		local lst "`y'"
		gen __0066 = 1
		while `i'< `n'{
			local lst `lst' "eq`i'"
			local i = `i' + 1
		}
		global HG_eqs
		matrix coleq M_inshrt = `lst'
		matrix colnames M_inshrt = __0066

		*matrix list M_inshrt
		*matrix `b' = M_inshrt*M_T' + M_a
		*matrix list `b'
		if "`gateaux'"~=""{
			local nf = `nf' - (`nb' - `n')
			matrix `from' = M_inshrt[1,1..`nf']
		}
		else if "`from'"~=""&"`long'"~=""{
			matrix `from' = M_inshrt
		}
		
	}

	if "`from'"~=""{
		local from "from(`from')"
	}

	if M_nffc[1,$HG_tpff]>0&("`from'"==""|$HG_init==1){
/* initial values for fixed effects */
		local fit = 0
		local lnk $HG_link
		if "$HG_link"=="recip"{
			local lnk pow -1
		}
		qui `noi' disp in gr "Initial values for fixed effects"
		if $HG_const { qui `noi' disp in gr "(Not applying constraints at this point)" }
		qui `noi' disp " "
		tempvar yn
		if "`offset'"~=""{
			quietly gen `yn' = `y' - $HG_off
		}
		else{
			gen `yn' = `y'
		}
		if ("$HG_famil"=="gauss")&("$HG_link"=="ident")& "`s'"==""{
			quietly `noi' reg `yn' `indep' [`ftype'=`wt'], `constant'
			matrix M_initr[1,1]=ln(_result(9))
			local fit = 1
		}
		else if ($HG_nolog+$HG_oth+$HG_mlog==1)&("$HG_famil"=="binom"|$HG_nolog==1|/*
		  */ $HG_mlog==1)&$HG_exp==0{
			local fit = 1
			local mnd = 1
			if "$HG_denom"~=""{
				qui summ $HG_denom, meanonly
				local mnd = r(mean)
			}
			if `mnd'>1 {
				if $HG_mlog>0 {
					disp in re "can't have denominator > 1 for mlogit"
					exit 198
				}
				if ($HG_nolog>0) {
					disp in re "can't have denominator > 1 for ordinal response"
					exit 198
				}
				qui `noi' glm `y' `indep' [`ftype'=`wt'], link(`lnk') /*
                                             */ fam(binom `denom') `constant' `offset'
			}
			else{
				if "$HG_link"=="logit"{
					qui `noi' logit `y' `indep' [`ftype'=`wt'], `constant' `offset'
				}
				else if "$HG_link"=="probit"{
					qui `noi' probit `y' `indep' [`ftype'=`wt'], `constant' `offset'
				}
				else if "$HG_link"=="cll"{
					qui `noi' cloglog `y' `indep' [`ftype'=`wt'], `constant' `offset'
				}
				else if $HG_mlog==1{
					qui `noi' mlogit `y' `indep' [`ftype'=`wt'] if $HG_ind==1, `constant' `basecat'
				}
				else if "$HG_linko"=="ologit"&"`thresh'"==""{
					qui `noi' ologit `y' `indep' [`ftype'=`wt'], `offset'
				}
				else if "$HG_linko"=="oprobit"&"`thresh'"==""{
					qui `noi' oprobit `y' `indep' [`ftype'=`wt'], `offset'
				}
				else if "$HG_linko"=="ocll"|"$HG_link"=="sprobit"|"$HG_linko"=="soprobit"|$HG_nolog>1|"`thresh'"~=""{
					local fit = 0
				}

			}
		}
		else if ("$HG_famil"=="poiss")&("$HG_link"=="log"){
			qui `noi' poisson `y' `indep' [`ftype'=`wt'], `constant' `offset'
			local fit = 1
		}
		else if ("$HG_famil"=="gamma"& M_nbrf[1,1]==1){
			qui `noi' glm `y' `indep' [`ftype'=`wt'], link(`lnk')/*
				*/ fam(gamma) `constant' `offset'
			matrix M_initr[1,1]= -ln($S_E_dc)
			local fit = 1
		}		
		if `fit' == 0 { /* fit level 1 model */
		/* preserve macros */
			qui `noi' disp in green "(using gllamm for inital values)"
			local eqs "$HG_eqs"
			local tprf = $HG_tprf
			local tplv = $HG_tplv
			local tpi = $HG_tpi
			local const = $HG_const
			local link $HG_link
			local linko $HG_linko
			local lev1 = $HG_lev1
			local ngeqs = $HG_ngeqs
			tempvar keep
			quietly gen `keep' = $HG_wt1
			quietly replace $HG_wt1 = `wt'
			matrix `mnip' = M_nip
			matrix `mnbrf' = M_nbrf
                        local adapt = $HG_adapt
	
		/* change global macros */
			local frm
			global HG_const = 0
			global HG_ngeqs = 0
			if "$HG_linko" == "sprobit"{
				global HG_linko "probit"
				global HG_lev1 = 0
				matrix M_nbrf = (0)
			}
			else if "$HG_linko" == "soprobit"{
				global HG_linko "oprobit"
				global HG_lev1 = 0
				matrix M_nbrf = (0)
			}
			matrix M_nip=(1,1\1,1)
			if $HG_lev1>0{
				global HG_eqs $HG_s1
				global HG_tprf=1
				global HG_tpi=1
				*local frm "from(M_initr)"
			}
			else{
				global HG_eqs
				global HG_tprf=0
				global HG_tpi=1
			}
			if "`from'"~=""{
				local frm `from'
			}
                        global HG_adapt = 0

		/* fit model for initial values */
			global HG_tplv=1 /* no level 1 standard deviation */
			local opt
			if $HG_init{
				local opt `options'
			}
			qui `noi' hglm_ml `y',  /*
			   */  $HG_obs `log' title("fixed effects model") /*
			   */ `frm' `trace'  skip `difficult' `opt'
			if $HG_init==0 {quietly `noi' ml display, level(`level') nohead}

			if $HG_init==1{
				if $HG_error==0{
					noi prepare, `robust' `cluster' `pweight' `dots' `noi'
					delmacs
					restore
					estimate local cmd "gllamm"
					* disp in re "running replay"
					noi Replay, level(`level') `eform' `allc' `robust' `cluster'
					exit
				}
			}

			if $HG_lev1>0{
				local num=M_nbrf[1,1]
				matrix `mat'=e(b)
				matrix `mat'=`mat'[1,"lns1:"]
				local i=1
				while `i'<=`num'{
					matrix M_initr[1,`i']=`mat'[1,`i']
					local i=`i'+1
				}
			}


		/* restore global macros */
			global HG_tplv=`tplv'
			global HG_eqs "`eqs'"
			global HG_tprf=`tprf'
			global HG_tpi=`tpi'
			global HG_link "`link'"
			global HG_linko "`linko'"
			global HG_ngeqs = `ngeqs'
			quietly replace $HG_wt1=`keep'
			matrix M_nip=`mnip'
			matrix M_nbrf = `mnbrf'
			global HG_const = `const'
			global HG_lev1 = `lev1'
                        global HG_adapt = `adapt'
		}
		local cn: colnames(M_initf)
		local ce: coleq(M_initf)
		matrix M_initf=e(b)
		capture matrix colnames M_initf = `cn'
		capture matrix coleq M_initf = `ce'
		local num=M_nffc[1,$HG_tpff]
		if `num'>0 {
			matrix M_initf=M_initf[1,1..`num']
			* matrix list M_initf
		}
		if $HG_const==1{
			matrix `b' = nullmat(M_initf), nullmat(M_initr)
			matrix M_inshrt = `b'*M_T
		}
		if $HG_error==1{
			exit
		}
	}

/* estimation */
	qui `noi' dis "  "
	qui `noi' dis "start running on $S_DATE at $S_TIME"

	local skip
	if $HG_const==1{
		matrix coleq M_inshrt = `lst'
		matrix colnames M_inshrt = __0066 
		local n = colsof(M_inshrt)
	        global HG_fixe (`y': `y' =__0066, nocons)
		local i = 1
		while `i'< `n'{
			global HG_fixe $HG_fixe (eq`i': __0066, nocons)
			local i = `i' + 1
		}
	}

	* disp "`trace' `options' "
        * disp "$HG_obs `log' `from'"
	* disp "`search' `lf0' `gateaux' `skip' `difficult' `eval' "

	capture noi hglm_ml `y', `trace' `options' /*
             */ $HG_obs `log' title("gllamm model") `from' /*
	     */ `search' `lf0' `gateaux' `skip' `difficult' `eval' 
	if _rc>0{ global HG_error=1 }
		
	qui `noi' dis "finish running on $S_DATE at $S_TIME"
	qui `noi' dis "  "
	if $HG_error==0{
		noi prepare, `robust' `cluster' `pweight' `dots' `noi'
		* disp "running delmacs"
		delmacs
		* disp "restore"
		restore
		estimate local cmd "gllamm"
		* disp "running replay"
		noi Replay, level(`level') `eform' `allc' `robust' `cluster'
	}	
end

program define prepare
syntax [, ROBUST CLUSTER PWEIGHT DOTS NOISILY]
* disp "options are: `robust' `cluster' `pweight' `dots' `noisily'"
	tempname b v X U
	matrix `b' = e(b)
	local n = colsof(`b')
	matrix M_Vs = e(V)
	capture	matrix `v' = inv(M_Vs)
	if _rc==0{
		matrix symeigen `X' `U' = `v'
		global HG_cn = sqrt(`U'[1,1]/`U'[1,`n'])
	}
	else{
		global HG_cn = -1
	}
	if $HG_const {
		matrix M_Vs  = M_T*M_Vs*M_T'
	}

/* deal with robust */

	if "`robust'"~=""|"`cluster'"~=""|"`pweight'"~=""{
		if "`cluster'"~=""{
			global HG_rbcls "`cluster'"
			disp "HG_rbcls is $HG_rbcls"
			local cluster cluster(`cluster')
		}
		disp "calling gllarob"
		qui `noisily' gllarob, first `cluster' `dots'
	}
	* disp "HG_const = " $HG_const
	* disp "running remcor"
	qui remcor `b'

	if $HG_const {
	* disp "running procstr"
		qui procstr
	}
end

program define hglm_ml
	version 6.0
	syntax  varlist(min=1)[, TITLE(passthru) LF0(numlist) noLOg TRace /*
	*/ OBS(passthru) FROM(string) SEarch(integer 0) Gateaux(numlist min=3 max=3) skip copy/*
	*/ noDIFficult EVal *]

	* disp in re "running hglm_ml"

	if "`log'"=="" { local log "noisily" }
	if "`trace'"~="" { local noi "noisily" }
	else local log 
	parse "`varlist'", parse(" ")
	local y "`1'"

     	tempvar mysamp
        tempname b f V M_init M_initr a lnf mlnf ip deriv

	local adapt = $HG_adapt
	global HG_adapt=0

	if "`from'"~=""{
		matrix `M_init'=`from'
		if "`eval'"~=""|`adapt'==1{
			capture ml model d0 gllam_ll $HG_fixe $HG_eqs, /*
			 */  noscvars waldtest(0) nopreserve missing  collinear

			* disp  "ml init M_init, `skip' `copy'"
	                ml init `M_init', `skip' `copy'
			qui `noi' capture ml maximize, search(off) /*
			*/  iterate(0) novce `options' nooutput nowarn
			
			matrix `M_init' = e(b)
			scalar `lnf' = e(ll)

			global ML_y1 `y'
			noisily gllam_ll 0 "`M_init'" "`lnf'"
			if `adapt'==0{
				disp in gr "log-likelihood = " in ye `lnf'
				delmacs	
				exit 1
			}
			* matrix list `M_init'
		}
		if "`gateaux'"~=""&$HG_free==0{
			disp in re "option gateaux not allowed (ignored) for fixed integration points"
		}
		else if "`gateaux'"~=""&$HG_free==1{
			qui `noi' disp in gr "Gateaux derivative"
			if $HG_tplv>2{
				disp "searching for additional point at level " $HG_tplv
			}
			local ll=$HG_tplv-1
			local tprf=M_nrfc[2,$HG_tplv]-M_nrfc[2,`ll']
			capture local mf = colsof(M_initf)
			if _rc>0 {local mf = 0}
			capture local mr = colsof(M_initr)
			if _rc>0 {local mr = 0}
			if $HG_const{
				local nreq = colsof(M_inshrt) - `tprf' - 1
				local cn: colnames(M_inshrt)
				local ce: coleq(M_inshrt)
			}
			else{
				local nreq = `mf'+`mr'-`tprf'-1
			}

			if `nreq'~=colsof(`M_init'){
				disp in re "initial value vector should have length `nreq'"
				matrix list `from'
				global HG_error=1
				exit 198
			}

			local l = `mr' - `tprf'-1 /* length of previous M_initr */
			local lp = `l' + 1
			matrix `a' = M_initr[1,`lp'...]

			matrix `M_init'= `M_init',`a'
			local locp = `nreq' + 1 + `tprf'
			if $HG_cip==0{
                                * new point must be one before last
				local locp = `locp' - `tprf'
				local nreq = `nreq' - `tprf'
				local jl = 1
				while `jl'<=`tprf'{
					matrix `M_init'[1,`locp'+`jl']=`M_init'[1,`nreq'+`jl']
					local jl = `jl' + 1
				}
			}

			tokenize "`gateaux'"
			local min = `1'
			local max = `2'
			local num = `3'
			local stp = (`max'-`min')/(`num'-1)
			matrix `M_init'[1,`locp']=-5 /* mass of new masspoint */
			scalar `mlnf'=0
			matrix `ip'=M_ip
			matrix `ip'[1,1]=1
			*recursive loop
			matrix `ip'[1,`tprf']=1
			local k = `nreq' + `tprf' 
			matrix `M_init'[1,`k']=`min'
			local nxtrf = `tprf'+1
			matrix `ip'[1,`nxtrf']=`num'
			local rf = `tprf'
			while `rf' <= `tprf'{
				*reset ip up to random effect `rf'
				while (`rf'>1) {
					local rf = `rf'-1
					matrix `ip'[1,`rf'] = 1
					local k = `nreq' + `rf'
					matrix `M_init'[1,`k']=`min'
				}
				* update lowest digit
				local rf = 1 
				while `ip'[1,`rf'] <= `num'{
					local k = `nreq' + `rf'
					matrix `M_init'[1,`k'] = `min' + (`ip'[1,`rf']-1)*`stp'
					* matrix list `M_init'
					global ML_y1 `y'
					gllam_ll 0 "`M_init'" "`lnf'"
					noi di in gr "." _c
					* noisily disp "likelihood=" `lnf'
					if (`lnf'>`mlnf'|`mlnf'==0)&`lnf'~=.{ 
						scalar `mlnf'=`lnf'
						matrix M_initr=`M_init'
					}
					matrix `ip'[1,`rf'] = `ip'[1,`rf'] + 1
				}
				matrix `ip'[1,`rf'] = `num' /* lowest digit has reached the top */
				while `ip'[1,`rf']==`num'&`rf'<=`tprf'{
					local rf = `rf' + 1
				}
				* rf is first r.eff that is not complete or rf>nrf
				if `rf'<=`tprf'{
					matrix `ip'[1,`rf'] = `ip'[1,`rf'] + 1
					local k = `nreq' + `rf'
					matrix `M_init'[1,`k'] = `min' + (`ip'[1,`rf']-1)*`stp'
				}
			}
			if "`lf0'"~=""{
				local junk: word 2 of `lf0'
				* disp in re "junk = " `junk'
				* disp in re "mlnf - lf0 is " `mlnf' " - " `junk'
				scalar `deriv' = `mlnf'-`junk'
				disp " "
				disp in ye "maximum gateaux derivative is " `deriv'
				* matrix list `M_initr'
				if `deriv'<0.00001{
					disp in re "maximum gateaux derivative less than 0.00001"
					global HG_error=1
					exit
				}
			}
			else{
				disp in ye "no gateaux derivarives could be calculated without lf0() option"
				matrix list `M_initr'
			}

			matrix `M_init' = M_initr
* starting log odds for new location
			matrix `M_init'[1,`locp']=-3
			if $HG_const{
				matrix colnames `M_init' = `cn'
				matrix coleq `M_init' = `ce'
			}
			* matrix list `M_init'
		} /* end if gateaux */		
	} /* end if from */
	else{ /* no from() */
		if "`gateaux'"~=""{ 
			disp in red "gateaux can't be used without option from()"
			exit 198
		}
		if "`eval'"~=""{
			disp in red "eval option only allowed with from()"
			exit 198
		}
		capture matrix `M_init'=M_initf
		if $HG_tprf|$HG_lev1>1{
			matrix `M_initr'=M_initr
			local max=3
			local min=0
			scalar `mlnf' = 0
			local f1= M_nbrf[1,1]+1
			local l=colsof(M_initr)
			local m=1
			if `search'>1{
				if $HG_const==1{
					disp in re "search option does not work yet with constraints"
					exit 198
				}
				else{
					qui `noi' disp in gr /*
					*/ "searching for initial values for random effects"
				}
			}
			while `m'<=`search'{ /* begin search */
				* matrix list M_initr
				matrix `a'=`M_init',M_initr
				*matrix list `a'
				global ML_y1 `y'
				noisily gllam_ll 0 "`a'" "`lnf'"
				qui `noi' disp "likelihood=" `lnf'
				if (`lnf'>`mlnf'|`m'==1)&`lnf'~=. { 
					scalar `mlnf'=`lnf'
					matrix `M_initr'=M_initr
				}
				local k=`f1'
				while `k'<=`l'{
					matrix M_initr[1,`k']=`min' + (`max'-`min')*uniform()
					local k=`k'+1
				}
				local m = `m' + 1
			} /* end search */
			matrix `M_init' = nullmat(`M_init'),`M_initr'
		}
		if $HG_const{
			matrix `M_init' = M_inshrt
		}
	}
	if "`difficult'"~=""{
		local difficu /* erase macro */
	}
	else{
		local difficu "difficult" /* default */
	}
	* disp "$HG_fixe $HG_eqs, init(`M_init',`skip') "
	* disp "`lf0' `obs' `trace' `difficu' `options'"
	*matrix list `M_init'
	if "`lf0'"~="" { local lf0 "lf0(`lf0')" }

	* matrix list `M_init'

	if `adapt'{
		local i = 1
		while `i'<$HG_tprf{
			tempname junk
			global HG_MU`i' "`junk'"
			tempname junk
			global HG_SD`i' "`junk'"
			gen double ${HG_MU`i'}=0
			gen double ${HG_SD`i'}=1
			local i = `i' + 1
		}
		global HG_adapt=0
		global ML_y1 `y'
		noi gllam_ll 1 "`M_init'" "`lnf'" "junk" "junk" 1
                qui `noi' disp " "
		qui `noi' disp in gre "Non-adaptive log-likelihood: " in ye `lnf'
		tempname last
		scalar `last' = 0
		local i = 1
		qui `noi' disp in gr " "
                qui `noi' disp in gr "First iteration of adaptive quadrature:"
		qui `noi' disp " "
*if "`eval'"~=""|"`from'"~=""{
		global HG_adapt=1
                qui `noi' disp in gr "Updating posterior means and variances"
                qui `noi' disp in gr "log-likelihood: "
		while abs((`last'-`lnf')/`lnf')>1e-8&`i'<240{
		        scalar `last' = `lnf'
		        noi gllam_ll 1 "`M_init'" "`lnf'" "junk" "junk" 1
		        qui `noi' disp in ye %10.4f `lnf' " " _c
                        if mod(`i',6)==0 {qui `noi' disp " " }
			/*
			local j = 1
			while `j'<$HG_tprf{
				qui summ ${HG_SD`j'}, meanonly
				qui replace ${HG_SD`j'}=${HG_SD`j'}+.05*r(mean)
				local j = `j' + 1
			}
			*/
			local i = `i' + 1
		}

		if "`eval'"~=""{
		        qui gllam_ll 1 "`M_init'" "`lnf'" "junk" "junk" 0
                        disp " "
		        disp in gr "log-likelihood = " in ye `lnf'
			delmacs
		        exit 1
		}
*}
		capture `log' ml model d0 gllam_ll $HG_fixe $HG_eqs, /*
		 */  noscvars `lf0' `obs' `title' /*
		 */ waldtest(0) nopreserve missing  collinear

                ml init `M_init', `skip' `copy'
		capture `log' ml maximize, search(off) `difficu' /*
		*/ `trace' ltolerance(1e-2)  /* iterate(3) 
		*/ `options' noclear novce nooutput
                local rc = _rc
	        if `rc'>1 {
		       di in red "(error occurred in ML computation)"
		       di in red "(use trace option and check correctness " /*
		       */ "of initial model)"
		       global HG_error=1
		       exit `rc'
	        }

		global HG_adapt=1
                tempname llast
		tempname llnf
                tempname last
                scalar `last' = `lnf'
                scalar `llnf' = e(ll)
                matrix `M_init'=e(b)
		local it = 1

		while abs((`last'-`llnf')/`llnf')>1e-7&abs((`llnf'-`lnf')/`lnf')>1e-7&`it'<=20{
/*
                        local i = 1
		        while `i'<$HG_tprf{
			        qui replace ${HG_MU`i'}=0
			        qui replace ${HG_SD`i'}=1
			        local i = `i' + 1
		        }
*/
			local it = `it' + 1
			qui `noi' disp " "
			qui `noi' disp in gr "Iteration `it' of adaptive quadrature:" 
                        qui `noi' disp " "
                        qui `noi' disp in gr "Updating posterior means and variances"
                        qui `noi' disp in gr "log-likelihood: "

                        local j = 1
		        scalar `llast' = 0

		        while (abs((`llast'-`lnf')/`lnf')>1e-8)&`j'<240{
					global ML_y1 `y'
					scalar `llast' = `lnf'
					noi gllam_ll 1 "`M_init'" "`lnf'" "junk" "junk" 1
					qui `noi' disp in ye %10.4f `lnf' _c
					 
					local i = 1
					local ns0 = 0
					local nsm = 0
					while `i'<$HG_tprf{
						*qui summ ${HG_SD`i'}, meanonly
						*qui replace ${HG_SD`i'}=${HG_SD`i'}+.05*r(mean)
						qui count if ${HG_SD`i'}<1e-25
						local ns0 = `ns0' + r(N)
						qui count if ${HG_SD`i'}==.
						local nsm = `nsm' + r(N)
						qui summ ${HG_SD`i'}, meanonly
						*if `nsm'>0{qui replace ${HG_SD`i'} = r(mean) if ${HG_SD`i'}==.}
						local i = `i' + 1
					}
					if `ns0'>0{
						qui `noi' disp  "*" _c
					}
					else{
						qui `noi' disp " " _c
					}
					if `nsm'>0{
						qui `noi' disp  "! " _c
					}				
					else{
						qui `noi' disp "  " _c
					}
                                        if mod(`j',6)==0 { qui `noi' disp " " }										
                                        local j = `j' + 1
		        }

                        if abs((`last'-`lnf')/`lnf')>1e-7&abs((`llnf'-`lnf')/`lnf')>1e-7{  /* adapt. quad . has not changed */
			*if abs((`last'-`lnf')/`lnf')>1e-7{  /* parameters and adapt. quad . have not changed */
                                ml init `M_init', `skip' `copy'
		                capture `log' ml maximize, search(off) `difficu' /*
		                */ `trace' iterate(1) novce /*
				*/ `options' noclear nooutput

                                local rc = _rc
	                        if `rc'>1 {
		                       di in red "(error occurred in ML computation)"
		                       di in red "(use trace option and check correctness " /*
		                        */ "of initial model)"
		                        global HG_error=1
		                        exit `rc'
	                        }

                                scalar `last' = `llnf'
                                scalar `llnf' = e(ll)
                                matrix `M_init'=e(b)

 		                qui `noi' disp in gr "log-likelihood is " in ye `llnf' in gre " and was " in ye `last' in gre ", relative change: "  in ye abs((`last'-`llnf')/`llnf')
                        }
                        else{
                                scalar `last' = `llnf'
                                scalar `lnf' = `llnf'
                        }
		}

                qui `noi' disp " "
                qui `noi' disp in gr "Last iteration of adaptive quadrature:"
                ml init `M_init', `skip' `copy'
	        capture `log' ml maximize, search(off) `difficu' /*
	        */ `trace' `options' nooutput
                local rc = _rc
	        if `rc'>1 {
		       di in red "(error occurred in ML computation)"
		       di in red "(use trace option and check correctness " /*
		       */ "of initial model)"
		       global HG_error=1
		       exit `rc'
	        }
	}
	else{
		timer on 2
		capture `log' ml model d0 gllam_ll $HG_fixe $HG_eqs, /*
		 */ maximize search(off) /*
		 */ init(`M_init', `skip' `copy') noscvars `lf0' `obs' `title' `trace' /*
		 */ waldtest(0) nopreserve missing `difficu' `options' collinear
	         * technique(bfgs) gtol(1e-4)
		timer off 2
	}

	local rc = _rc
	if `rc'>1 {
		di in red "(error occurred in ML computation)"
		di in red "(use trace option and check correctness " /*
		*/ "of initial model)"
		global HG_error=1
		exit `rc'
	}
	if `rc'==1 {
		di in red /*
		*/ "(Maximization aborted)"
		delmacs
		global HG_error=1
		exit 1
	}
	else if $HG_error==1{
		disp in red "some error has occurred"
		exit
	}
end

program define lnkfm
	version 6.0
	args link fam

	global S_1	/* link		*/
	global S_2	/* family	*/


	lnk "`1'"
	fm "`2'"	

	if "$S_1" == "" {
		if "$S_2" == "gauss" { global S_1 "ident" }
		if "$S_2" == "poiss" { global S_1 "log"   }
		if "$S_2" == "binom" { global S_1 "logit" }
		if "$S_2" == "gamma" { global S_1 "recip" }
	}

/*
	if ("$S_1"=="mlogit"|"$S_1"=="smlogit")&"$S_2"~="binom"{
		disp in red "mlogit link must be combined with binomial probability"
		exit 198
	}
*/
	if ("$S_1"=="mlogit"|"$S_1"=="smlogit"|"$S_1"=="ologit"|"$S_1"=="oprobit"|"$S_1"=="soprobit"|"$S_1"=="ocll"){
		global S_2
	}
end

program define fm
	version 6.0
	args fam
	local f = lower(trim("`fam'"))
   local l = length("`f'")

	if "`f'" == substr("gaussian",1,max(`l',3)) { global S_2 "gauss" }
	else if "`f'" == substr("normal",1,max(`l',3))   { global S_2 "gauss" }
	else if "`f'" == substr("poisson",1,max(`l',3))  { global S_2 "poiss" }
	else if "`f'" == substr("binomial",1,max(`l',3)) { global S_2 "binom" }
	else if "`f'" == substr("gamma",1,max(`l',3))    { global S_2 "gamma" }
	else if "`f'" != "" {
		noi di in red "unknown family() `fam'"
		exit 198
	}

	if "$S_2" == "" {
		global S_2 "gauss"
	}
end

program define lnk
	version 6.0
	args link
	local f = lower(trim("`link'"))
	local l = length("`f'")

	if "`f'" == substr("identity",1,max(`l',2)) { global S_1 "ident" }
	else if "`f'" == substr("log",1,max(`l',3))      { global S_1 "log"   }
	else if "`f'" == substr("logit",1,max(`l',4))    { global S_1 "logit" }
	else if "`f'" == substr("mlogit",1,max(`l',3))    { global S_1 "mlogit" }
	else if "`f'" == substr("smlogit",1,max(`l',3))    { global S_1 "smlogit" }
	else if "`f'" == substr("ologit",1,max(`l',3))    { global S_1 "ologit" }
	else if "`f'" == substr("oprobit",1,max(`l',3))    { global S_1 "oprobit" }
	else if "`f'" == substr("probit",1,max(`l',3))   { global S_1 "probit"}
	else if "`f'" == substr("ocll",1,max(`l',3))   { global S_1 "ocll"}
	else if "`f'" == substr("cll",1,max(`l',3))   { global S_1 "cll"}
	else if "`f'" == substr("sprobit",1,max(`l',3))   { global S_1 "sprobit"}
   else if "`f'" == substr("soprobit",1,max(`l',3))   { global S_1 "soprobit"}
	else if "`f'"==substr("reciprocal",1,max(`l',3)) { global S_1 "recip" }
	else if "`f'" != "" {
		noi di in red "unknown link() `link'"
		exit 198
	}
end

program define delmacs, eclass
	version 6.0
/* deletes all global macros and matrices and stores some results in e()*/
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
		local n = M_nrfc[1,`lev']
		local n = M_nip[2,`n']
		capture est matrix zps`n' M_zps`n'
		while `i' <= `i2'{
			local n = M_nip[2,`i']
			capture est matrix zlc`n' M_zlc`n'
			capture est matrix zps`n' M_zps`n'
			local i = `i' + 1
		}
		local lev = `lev' + 1
	}


	if $HG_free==0&$HG_init==0{
		est matrix chol CHmat
	}
	est matrix nrfc M_nrfc
	est matrix nffc M_nffc
	est matrix nbrf M_nbrf
	est matrix nu M_nu
	capture est matrix Vs M_Vs
	capture est matrix mresp M_resp
	capture est matrix mrespm M_respm
	if $HG_ngeqs>0{
		est matrix mngeqs M_ngeqs
	}
	matrix drop M_ip
	est matrix nip M_nip
	capture est matrix mb M_b
	matrix drop M_znow
	capture matrix drop M_initf
	matrix drop M_initr
	capture matrix drop M_chol
	capture est matrix mb M_b
	est matrix olog M_olog
	capture est matrix moth M_oth
	if $HG_const == 1{
		capture drop __0066
		est matrix a M_a
		* est matrix C M_C
		est matrix T M_T
		est local coln $HG_coln
		est local cole $HG_cole
		global HG_coln
		global HG_cole
	}

	/* globals defined in gllam_ll */
	local i=1
	while (`i'<=$HG_tpff){
		global HG_xb`i'
		local i= `i'+1
	}
	local i = 1
	while (`i'<=$HG_tprf){
		global HG_s`i'
		local i= `i'+1
	}
	local i = 1
	while (`i'<=$HG_tplv){
		global HG_wt`i'
		local i = `i' + 1
	}
	if $HG_adapt{
		local i = 1
		while `i'<$HG_tprf{
			global HG_MU`i'
			global HG_SD`i'
			local i = `i' + 1
		}
	}

	est local noC=$HG_noC
	global HG_noC
	est local adapt=$HG_adapt
	global HG_adapt
	est local const = $HG_const
	global HG_const
	global HG_fixe
	est local inter = $HG_inter
	global HG_inter
	global HG_dots
	est local ngeqs = $HG_ngeqs
	global HG_ngeqs
 	est local nolog = $HG_nolog
	global HG_nolog
	est local mlog = $HG_mlog
	global HG_mlog
	est local smlog = $HG_smlog
	global HG_smlog
  	global HG_lvolo
	est local oth = $HG_oth
	global HG_oth
	est local lev1 = $HG_lev1
	global HG_lev1
	est local bmat = $HG_bmat
	global HG_bmat
	est local tplv = $HG_tplv
	global HG_tplv 
	est local tprf = $HG_tprf
	global HG_tprf
	est local tpi = $HG_tpi
	global HG_tpi
	est local tpff = $HG_tpff
	global HG_tpff
	est local clus "$HG_clus"
	global HG_clus
	est local weight "$HG_weigh"
	global HG_pwt
	est local pweight "$HG_pwt"
	global which   
	global HG_gauss 
	est local free = $HG_free 
	global HG_free
	est local cip = $HG_cip
	est local famil "$HG_famil"
	global HG_famil 
	est local link "$HG_link"
	global HG_link 
	est local linko "$HG_linko"
	global HG_linko
	capture est local exp $HG_exp
	global HG_exp
	capture est local expf $HG_expf
	global HG_expf
	est local lv "$HG_lv"
	global HG_lv
	est local fv "$HG_fv"
	global HG_fv
	global HG_nump
	global HG_eqs
	global HG_obs
	est local offset "$HG_off"
	global HG_off
	est local denom "$HG_denom"
	global HG_denom
	est local cor = $HG_cor
	global HG_cor
	est local s1 "$HG_s1"
	global HG_s1
	capture est local init $HG_init
	global HG_init
	capture est local ind "$HG_ind"
	global HG_ind
	capture est local cn = $HG_cn
	global HG_cn
	capture est local robclus "$HG_rbcls"
	global HG_rbcls
end

program define initmacs
version 6.0
/* defines all global macros */
args nrf nip eqs geqs s bmatrix touse dep

tempname mat

disp "  "
disp in gr "Random effects information for" in ye " $HG_tplv" in gr " level model"
disp in gr "-----------------------------------------------------------------------------"


/* deal with nrf */
	matrix M_nrfc=J(2,$HG_tplv,1)
	if "`nrf'"==""|$HG_free{
		local k=1
		while (`k'<=$HG_tplv){
			matrix M_nrfc[1,`k']=`k'
			matrix M_nrfc[2,`k']=`k'
			local k=`k'+1
		}
	}
	if "`nrf'"~=""{
		local k: word count `nrf'
		if `k'~=$HG_tplv-1 {
			if $HG_tplv==1{
				disp in red "option nrf is meaningless for 1-level model"
			}
			else{
				disp in red "option nrf() does not contain " $HG_tplv-1 " argument(s)"
			}
			exit 198
		}
		parse "`nrf'", parse(" ")
		local k=2
		while (`k'<=$HG_tplv){
			matrix M_nrfc[2,`k']=`1'
			local k=`k'+1
			mac shift
		}
		/* make cumulative */
		local k=2
		while (`k'<=$HG_tplv){
			matrix M_nrfc[2,`k']=M_nrfc[2,`k'-1]+M_nrfc[2,`k']
			if $HG_free==0{matrix M_nrfc[1,`k']=M_nrfc[2,`k']}
			local k=`k'+1
		}
	}
	* matrix list M_nrfc
	global HG_tprf=M_nrfc[2,$HG_tplv] /* number of random effects */
	global HG_tpi=M_nrfc[1,$HG_tplv] /* number of integration loops + 1 */
	if $HG_tplv==$HG_tprf{
		if $HG_cor==0{
			disp "option nocorrel ignored because no multiple r. effects per level"
		}
	}


/* deal with nip */
	if "`nip'"==""{ 
		local k = 1
		local nip = 8
	}
	else{
		local k: word count `nip'
	}
	if `k'==1{
		matrix M_nip=J(2,$HG_tprf,`nip')
		if `nip' == 1 & $HG_cip==1{ global HG_init=1 }
		matrix M_nip[1,1]=1
	}
	else if `k'~=$HG_tpi-1{
		disp in red "option nip() has `k' arguments, need 1 or " $HG_tpi-1
		exit 198
	}
	else{
		matrix M_nip=J(2,$HG_tprf,1)
		local i=1
		while `i'<$HG_tpi{
			local k: word `i' of `nip'
			local l = `i' + 1
			matrix M_nip[1,`l']= `k'
			local i = `i' + 1
		}
	}
	local i = M_nrfc[2,1]+1
	while `i'<= $HG_tprf{
		if $HG_free{
			matrix M_nip[2,`i'] = `i'
		}
		else{
			matrix M_nip[2,`i'] = M_nip[1,`i']
		}
		local i = `i' + 1
	}			

	* matrix list M_nip
	capture matrix drop M_initr
	
/* deal with Eqs */
	local depv `dep'
	matrix M_nbrf=(0)
	global HG_eqs
	if $HG_lev1>0{
		disp in gr "***level 1 equation:"
		if "`s'"~=""{
			eq ? "`s'"
			local vars "$S_1"
			markout `touse' `vars'
			global HG_eqs "$HG_eqs (lns1: `depv' `vars',nocons)"
			global HG_s1 "(lns1: `depv' `vars',nocons)"
		}
		else{
			local vars "_cons"
			global HG_eqs "$HG_eqs (lns1: `depv')"
			global HG_s1 "(lns1: `depv')"
		}
		local depv
		disp " "
		if $HG_lev1==1{disp in gr "   log standard deviation"}
		else if $HG_lev1==2{disp in gr "   log coefficient of variation"}
		else if $HG_lev1==3{disp in gr "   log(phi)/2"}
		disp in ye "   lns1: `vars'"
		local num: word count `vars'
		matrix M_nbrf=(`num')
		matrix `mat'=J(1,`num',-1)
		matrix colnames `mat'=`vars'
		matrix coleq `mat'=lns1
		matrix M_initr=nullmat(M_initr),`mat'
	}
	else{
		matrix M_nbrf=(0)
		if "`s'"~=""{
			disp in re "S not used because families do not include dispersion parameters"
		}
	}
	if "`eqs'"~=""{
		local k: word count `eqs'
		if `k'~=$HG_tprf-1{
			disp in red `k' " equations specified: `eqs', need " $HG_tprf-1
			exit 198
		}
		* check that they are equations and find number of variables in each: nbrf
		local lev=2
		local l=1
		local ic=0
		while (`lev'<=$HG_tplv){
			disp " "
			local m=$HG_tplv-`lev'+1
			local clusnam: word `m' of $HG_clus
			disp " "
			disp in gr "***level `lev' (" in ye "`clusnam'" in gr ") equation(s):"
			local clusnam=substr("`clusnam'",1,4)
			local i1=M_nrfc[2, `lev'-1]
			local j1=M_nrfc[2, `lev']
			local nrf=`j1'-`i1'
			disp "   (`nrf' random effect(s))"
			disp "  "
			local rfl = 1
/* MASS POINTS */
			if $HG_free {
				if $HG_cor==0{
					disp "option nocorrel irrelevant for free masses"
				}
				local k = 1
				local nloc = M_nip[1, `lev']
				if $HG_cip{ local nloc = `nloc' - 1}
				while `k' <= `nloc'{
					disp " "
					disp in gre "class `k'"
					local j = `i1'
					while `j'< `j1'{
						local eqnam: word `j' of `eqs'
						eq ? "`eqnam'"
						local vars "$S_1"
						markout `touse' `vars'
						local num: word count `vars'
						matrix `mat'=(`num')
						matrix M_nbrf=M_nbrf,`mat'
						if (`num'>1){
							parse "`vars'", parse(" ")
							local vars1 "`1'"
							if `k'==1{
								mac shift
								local vars2 "`*'"
								local eqnaml "`clusnam'`rfl'l"
								eq "`eqnaml': `vars2'"
								eq ? "`eqnaml'"
								disp " "
								disp in gr "   lambdas for random effect " in ye `j'
								disp in ye "   `eqnaml': `vars2'"
								global HG_eqs "$HG_eqs (`eqnaml': `depv' `vars2', nocons)"
								local depv 
								local num=`num'-1
								* initial loading on masspoints
								local lod = `j'/3
								matrix `mat'=J(1,`num',`lod')
								matrix colnames `mat'= `vars2'
								matrix coleq `mat'=`eqnaml'
								matrix M_initr = nullmat(M_initr), `mat'	
							}

						}
						else{local vars1 `vars'}
						disp " "
						disp in gr "   location for random effect " in ye `j'
						local eqnam "z`lev'_`j'_`k'"
						if `nrf'==1{
							local eqnam "z`lev'_`k'"
						}
						eq "`eqnam'":`vars1'
						eq ? "`eqnam'"
						disp in ye "   `eqnam': `vars1'"
						global HG_eqs "$HG_eqs (`eqnam': `depv' `vars1', nocons)"
						local depv
						markout `touse' `vars1'
						* initial locations of mass points
						*local val = int((`k'+1)/2)*(-1)^`k'/10
						local val = int((`k'+1)/2)*(-1)^`k'
						matrix `mat'=(`val')
						matrix colnames `mat'=`vars1'
						matrix coleq `mat'=`eqnam'
						matrix M_initr=nullmat(M_initr),`mat'
						local j = `j' + 1
						local rfl = `rfl' + 1
					}
					if `k'< M_nip[1, `lev']{
						local eqnam "p`lev'_`k'"
						eq "`eqnam'":
						eq ? "`eqnam'"
						disp " "
						disp in gr "   log odds for level " in ye `lev'
						disp in ye "   `eqnam': _cons"
						global HG_eqs "$HG_eqs (`eqnam': `depv')"
						local depv
						* initial log odds for masspoints
						matrix `mat'=(-.4)
						matrix colnames `mat'=_cons
						matrix coleq `mat'=`eqnam'
						matrix M_initr=nullmat(M_initr),`mat'
					}
						local k = `k' + 1
				}
			}
/* STD DEVS */
			else{
				local j = `i1'
				while (`j'<`j1'){
					local eqnam: word `l' of `eqs'
					eq ? "`eqnam'"
					local vars "$S_1"
					local num: word count `vars'
					matrix `mat'=(`num')
					matrix M_nbrf=M_nbrf,`mat'
					markout `touse' `vars'
					if "`vars'"==""{ local vars "_cons"}
					if `num'>1{
						* vars1 is variable of first loading (fix at one)
						parse "`vars'", parse(" ")
						local vars1 "`1'"
						mac shift
						local vars "`*'"
						local eqnaml "`clusnam'`rfl'l"
						eq "`eqnaml'": `vars'
						eq ? "`eqnaml'"
						disp " "
						disp in gr "   lambdas for random effect " in ye `j'
						disp in ye "   `eqnaml': `vars'"
						global HG_eqs "$HG_eqs (`eqnaml': `depv' `vars', nocons)"
						local depv
						* initial values of loadings
						local lod = `j'/3 /*different loading for diff r.eff*/
						matrix `mat'=J(1,`num'-1,`lod')
						matrix colnames `mat'=`vars'
						matrix coleq `mat'=`eqnaml'
						matrix M_initr=nullmat(M_initr),`mat'
					}
					else{
						local vars1 `vars'
					}
					* variance
					local eqnam "`clusnam'`rfl'"
					eq "`eqnam'": `vars1'
					if `nrf'==1|$HG_cor==0{
						disp in gr "   standard deviation for random effect " in ye `j'
					}
					else{
						disp " "
						disp in gr /*
						*/"   diagonal element of cholesky decomp. of covariance matrix"
					}
					disp in ye "   `eqnam' : `vars1'"
					global HG_eqs "$HG_eqs (`eqnam': `depv' `vars1', nocons)"
					local depv
					* initial value of standard deviation
					matrix `mat' = (0.5)
					matrix colnames `mat' = `vars1'
					matrix coleq `mat' = `eqnam'
					matrix M_initr=nullmat(M_initr),`mat'
					local l=`l'+1
					local j=`j'+1
					local rfl = `rfl' + 1
				}
				if `nrf' > 1&$HG_cor==1{
					/* generate equations for covariance parameters */
					disp " "
					disp  in gr "   off-diagonal elements"
					local ii=2
					*local num = $HG_tplv-`lev'+1
					*local eqnam: word `num' of $HG_clus
					*local eqnam = substr("`eqnam'",1,4)
					while (`ii'<=`nrf'){
						local jj=1
						while (`jj'<`ii'){
							local eqnaml "`clusnam'`ii'_`jj'"
							eq "`eqnaml'":
							eq ? "`eqnaml'"
							disp in ye "   `eqnaml': _cons"
							global HG_eqs "$HG_eqs (`eqnaml':)"
							matrix `mat'=(0)
							matrix colnames `mat'=_cons
							matrix coleq `mat'=`eqnaml'
							matrix M_initr=nullmat(M_initr),`mat'
							local jj =  `jj' + 1
						}
						local ii=`ii'+1
					}
				}
			} /* end else $HG_free */
		local lev=`lev'+1
		} /* lev loop */
		
	} /* endif equ given */
	else{
	/* random intercepts */
		if M_nrfc[1,$HG_tplv]~=$HG_tplv{
			"must specify equations for random effects"
			exit 198
		}
		local k=$HG_tprf-1
		matrix `mat'=J(1,`k',1)
		matrix M_nbrf=M_nbrf,`mat'
		local lev=2
		disp " "
		while (`lev'<=$HG_tplv){
			local l=$HG_tplv-`lev'+1
			local clusnam: word `l' of $HG_clus
			disp " "
			disp in gr "***level `lev' (" in ye "`clusnam'" in gr ") equation(s):"
			local clusnam = substr("`clusnam'",1,4)
/*MASS POINTS */
			if ($HG_free){
				local k = 1
				local nloc = M_nip[1, `lev']
				if $HG_cip{ local nloc = `nloc' - 1}
				while `k' <= `nloc'{
					disp " "
					disp in gre "class `k'"
					local j = 1

					local eqnam "z`lev'_`k'"
					disp in gr "   location for random effect"
					disp in ye "   `eqnam': _cons"
					global HG_eqs "$HG_eqs (`eqnam': `depv')"
					local depv
					* initial locations of mass points
					*local val = int((`k'+1)/2)*(-1)^`k'/10
					local val = int((`k'+1)/2)*(-1)^`k'
					matrix `mat'=(`val')
					matrix colnames `mat'=_cons
					matrix coleq `mat'=`eqnam'
					matrix M_initr=nullmat(M_initr),`mat'

					if `k'<M_nip[1, `lev']{
						local eqnam "p`lev'_`k'"
						disp in gr "   log odds for random effect"
						disp in ye "   `eqnam': _cons"
						global HG_eqs "$HG_eqs (`eqnam':)"
						* initial log odds for mass-points
						matrix `mat'=(-.4)
						matrix colnames `mat'=_cons
						matrix coleq `mat'=`eqnam'
						matrix M_initr=nullmat(M_initr),`mat'
					}
					local k = `k' + 1
				}
			}
/* ST. DEVS */
			else{
				local eqnam "`clusnam'"
				disp " "
				disp in gr "   standard deviation of random effect"
				disp in ye "   `eqnam': _cons"
				global HG_eqs "$HG_eqs (`eqnam':`depv')"
				local depv
				* initial value for sd
				matrix `mat'=(0.5)
				matrix colnames `mat'=_cons
				matrix coleq `mat'=`eqnam'
				matrix M_initr=nullmat(M_initr),`mat'
				local cons `cons'1
			}
			local lev=`lev'+1
		}
	}
	disp " "

/* deal with Bmatrix */

	global HG_bmat = 0
	if "`bmatrix'"~=""{
		if $HG_tprf<2{
			disp in re "bmatrix can only be used for more than 1 random effect"
			exit 198
		}
		capture matrix list `bmatrix'
		if _rc>0{
			disp in re "bmatrix is not a matrix"
			exit 198
		}
		local bn = colsof(`bmatrix')
		if rowsof(`bmatrix')~=`bn'{
			disp in re "bmatrix must be square"
			exit 198
		}
		if `bn'~=$HG_tprf-1{
			disp in re "number of rows and columns of B matrix must be " $HG_tprf-1
			exit 198
		}
		matrix M_b=`bmatrix'
		global HG_bmat = 1
		disp in gr "B-matrix:"
		local i = 1
		while `i' <= `bn'{
			local j = 1
			while `j'<= `bn'{
				if M_b[`i',`j']>0{
					local eqnam b`i'_`j'
					disp " "
					disp in ye "   `eqnam': _cons"
					global HG_eqs "$HG_eqs (`eqnam':)"
					* initial value for sd
					matrix `mat'=(0.5)
					matrix colnames `mat'=_cons
					matrix coleq `mat'=`eqnam'
					matrix M_initr=nullmat(M_initr),`mat'
					local cons `cons'1
				}
				local j = `j' + 1
			}
			local i = `i' + 1
		}
		disp " "	
	} 

/* deal with geqs */

	global HG_ngeqs = 0
	if "`geqs'"~=""{
		* M_ngeqs: first row says which random effect, second how many terms
		local num: word count `geqs'
		global HG_ngeqs = `num'
		matrix M_ngeqs=J(2,`num',0)

		disp in gr "Regressions of random effects on covariates:"
		tokenize `geqs'
		local i = 1
		while "`1'"~="" {
			local k = substr("`1'",2,1)
			local k = `k' + 1
			if `k'>$HG_tprf {
				disp in red "eq `1' refers to a random effects that does not exist"
				exit 198
			}
			local j = 1
			while `j'<=`i'{
			        if M_ngeqs[1,`j']==`k' {
					disp in red "more than one geq given for random effect" `k'-1
					exit 198
				}
				local j = `j' + 1
			}
			eq ? "`1'"
			local vars "$S_1"
			local num: word count `vars'
			matrix `mat'=J(1,`num',0)
			matrix colnames `mat'=`vars'
			matrix coleq `mat'=`1'
			matrix M_initr=nullmat(M_initr),`mat'
			markout `touse' `vars'
			disp in gr "   equation for random effect " in ye `k'-1
			disp in ye "   `1': `vars'"
			global HG_eqs "$HG_eqs (`1': `vars', nocons)"
			matrix M_ngeqs[1,`i']=`k'
			matrix M_ngeqs[2,`i']=`num'
			local i = `i' + 1
			mac shift
		}
	disp " "
	}

/* ++++++++++++ need to define quantities +++++++++++++++++++++++++++++++++++++++ */
	global which =  4

/* ++++++++++++ calculates quantities +++++++++++++++++++++++++++++++++++++++ */
/* total number of fixed linear predictors */      
	global HG_tpff = colsof(M_nffc)
		
/* the "clock" ip and znow*/
	local k = $HG_tprf+2
	matrix M_ip =  J(1,`k',1)
	local k = $HG_tprf - 1
	matrix M_znow =J(1,`k',1)

/* set up zloc and zps*/
	if $HG_free==0{
		local i = 2
		while (`i'<=$HG_tprf){
			local n = M_nip[1, `i']
			if $HG_gauss{
				ghquad `n'
			}
			else{
				lebesque `n'
			}
			* matrix list M_zlc`n'
			* matrix list M_zps`n'
			local i = `i' + 1
		}
	}

end

program define ghquad 
* stolen from rfprobit (Bill Sribney)
	version 4.0
	local n `1'
	tempname xx ww a b
	local i 1
	local m = int((`n' + 1)/2)
	matrix M_zlc`n' = J(1,`m',0)
	matrix M_zps`n' = M_zlc`n'
	while `i' <= `m' {
		if `i' == 1 {
			scalar `xx' = sqrt(2*`n'+1)-1.85575*(2*`n'+1)^(-1/6)
		}
		else if `i' == 2 { scalar `xx' = `xx'-1.14*`n'^0.426/`xx' }
		else if `i' == 3 { scalar `xx' = 1.86*`xx'-0.86*M_zlc`n'[1,1] }
		else if `i' == 4 { scalar `xx' = 1.91*`xx'-0.91*M_zlc`n'[1,2] }
		else { 
			local im2 = `i' -2
			scalar `xx' = 2*`xx'-M_zlc`n'[1,`im2']
		}
		hermite `n' `xx' `ww'
		matrix M_zlc`n'[1,`i'] = `xx'
		matrix M_zps`n'[1,`i'] = `ww'
		local i = `i' + 1
	}
	if mod(`n', 2) == 1 { matrix M_zlc`n'[1,`m'] = 0}
/* start in tails */
	matrix `b' = (1,1)
	matrix M_zps`n' = M_zps`n'#`b'
	matrix M_zps`n' = M_zps`n'[1,1..`n']
	matrix `b' = (1,-1)
	matrix M_zlc`n' = M_zlc`n'#`b'
	matrix M_zlc`n' = M_zlc`n'[1,1..`n']

/* other alternative (start in centre) */
/*
	matrix `b' = J(1,`n',0)
	local i = 1
	while ( `i'<=`n'){
		matrix `b'[1, `i'] = M_zlc`n'[1, `n'+1-`i']
		local i = `i' + 1
	}
	matrix M_zlc`n' = `b'
	local i = 1
	while ( `i'<=`n'){
		matrix `b'[1, `i'] = M_zps`n'[1, `n'+1-`i']
		local i = `i' + 1
	}
	matrix M_zps`n' = `b'
*/
/* end other alternative */
	scalar `a' = sqrt(2)
	matrix M_zlc`n' = `a'*M_zlc`n'
	scalar `a' = 1/sqrt(_pi)
	matrix M_zps`n' = `a'*M_zps`n'
end


program define hermite  /* integer n, scalar x, scalar w */
* stolen from rfprobit (Bill Sribney)
	version 4.0
	local n "`1'"
	local x "`2'"
	local w "`3'"
	local last = `n' + 2
	tempname i p
	matrix `p' = J(1,`last',0)
	scalar `i' = 1
	while `i' <= 10 {
		matrix `p'[1,1]=0
		matrix `p'[1,2] = _pi^(-0.25)
		local k = 3
		while `k'<=`last'{
			matrix `p'[1,`k'] = `x'*sqrt(2/(`k'-2))*`p'[1,`k'-1] /*
			*/	- sqrt((`k'-3)/(`k'-2))*`p'[1,`k'-2]
			local k = `k' + 1
		}
		scalar `w' = sqrt(2*`n')*`p'[1,`last'-1]
		scalar `x' = `x' - `p'[1,`last']/`w'
		if abs(`p'[1,`last']/`w') < 3e-14 {
			scalar `w' = 2/(`w'*`w')
			exit
		}
		scalar `i' = `i' + 1
	}
	di in red "hermite did not converge"
	exit 499
end


program define lebesque
	version 5.0
	local n `1'
	tempname pt a b
	scalar `a' = 1/`n'
	matrix M_zps`n' = J(1,`n',`a')
	local i = 1
	local m = int((`n' + 1)/2)
	matrix M_zlc`n' = J(1,`m',0)
	while(`i'<=`m'){
		scalar `pt' = `i'/`n' -1/(2*`n')
		matrix M_zlc`n'[1,`i']=invnorm(`pt')
		local i = `i' + 1
	}
/* start in tails */
	matrix `b' = (1,-1)
	matrix M_zlc`n' = M_zlc`n'#`b'
	matrix M_zlc`n' = M_zlc`n'[1,1..`n']
/* other alternative: left to right */
/*
	while ( `i'<=`n'){
		matrix M_zlc`n'[1, `i'] = -M_zlc`n'[1, `n'+1-`i']
		local i = `i' + 1
	}
*/
end

program define disprand
version 6.0
* displays additional information about random effects 
* disp "running disprand "
disp " "
if "e(tplv)" == ""{
	* estimates not found
	exit
}
tempname var b se cor mn0 mm0
matrix `b' = e(b)
local names: colnames(`b')
tempname M_nrfc M_nip M_nbrf M_nffc M_b V
matrix `V' = e(V)
matrix `M_nrfc' = e(nrfc)
matrix `M_nip' = e(nip)
matrix `M_nbrf' = e(nbrf)
matrix `M_nffc' = e(nffc)
local ngeqs = e(ngeqs)
local bmat = e(bmat)
if `bmat' ==1{matrix `M_b' = e(mb)}
local bmat = e(bmat)
local iscor = e(cor)
local nxt = `M_nffc'[1,colsof(`M_nffc')]+1
local free = e(free)
local tplv = e(tplv)
local lev1 = e(lev1)
local tprf = e(tprf)
local cip = e(cip)

local nrfold = `M_nrfc'[2,1]
if `M_nbrf'[1,1]>0{
	if `lev1' == 1 {disp in gr "Variance at level 1"}
	else if `lev1' == 2 {disp in gr "Squared Coefficient of Variation"}
	else if `lev1' == 3 {disp in gr "Dispersion at level 1"}
disp in gr "-----------------------------------------------------------------------------"
	if `M_nbrf'[1,1]==1{
		scalar `var' = exp(2*`b'[1, `nxt'])
		scalar `se' = 2*`var'*sqrt(`V'[`nxt',`nxt'])
		disp in gr "  " in ye `var' " (" `se' ")"
		local nxt = `nxt' + 1
	}
	else{
		disp " "
		if `lev1'==1{disp in gr "    equation for log-standard deviaton: "}
		else if `lev1'==2{disp in gr "    equation for log-coefficient of variation"}
		else if `lev1'==3{disp in gr "    equation for log(phi)/2"}
		disp " "
		local i = 1
		while `i' <= `M_nbrf'[1,1]{
			scalar `var' = `b'[1,`nxt']
			scalar `se' = sqrt(`V'[`nxt',`nxt'])
			local nna: word `nxt' of `names'
			disp in gr "    `nna': " in ye `var' " (" `se' ")"
			local i = `i' + 1
			local nxt = `nxt' + 1 
		}
	}
}

if `tplv' > 1{
local lev = 2
if `free' == 1{
	disp " "
	disp in gr "Probabilities and locations of random effects"
}
else{
	disp " "
	disp in gr "Variances and covariances of random effects"
}
disp in gr "-----------------------------------------------------------------------------"
while (`lev' <= `tplv'){
	local nip = `M_nip'[1,`lev']
	local sof = `M_nrfc'[1,`lev'-1]
	disp " "
	local cl = `tplv' - `lev' + 1
	local cl: word `cl' of `e(clus)'
	disp in gr "***level `lev' (" in ye "`cl'" in gr ")"
	if `free' == 1{
		tempname M_zps`lev'
		matrix `M_zps`lev'' = e(zps`lev')
		local j = 2
		local zz=string(`M_zps`lev''[1,1],"%6.0gc")
		if `nip'>1{ 
			local mm "0`zz'"
		}
		else{
			local mm "1"
		}

		while `j'<=`nip'{
			local zz=string(`M_zps`lev''[1,`j'],"%6.0gc")
			local mm "`mm'" ", " "0`zz'"
			local j = `j' + 1
		}
		disp in gr "    prob: " in ye "`mm'"
	}
	local i2 = `M_nrfc'[2,`lev']
	local i = `nrfold'+1
	local num = `i2' -`i' + 1 /* number of random effects */
	if `free'==0{
		* get standard errors of variances from those of cholesky decomp.
		*disp "sechol `lev' `num' `nxt'"
		qui sechol `lev' `num' `nxt' 
	}
	local k = 1
	local ii = 1
	local nrfold = `M_nrfc'[2,`lev']
	while `i'<= `i2'{
		local n=`M_nip'[2,`i']
		if `free'==1{
			tempname M_zlc`n'
			matrix `M_zlc`n'' = e(zlc`n')
			local j = 2
			local zz=string(`M_zlc`n''[1,1],"%7.0gc")
			local mm "`zz'"
			scalar `mn0' = `M_zlc`n''[1,1]*`M_zps`lev''[1,1]
			while `j'<=`nip'{
				scalar `mn0' = `mn0' + `M_zlc`n''[1,`j']*`M_zps`lev''[1,`j']
				local zz=string(`M_zlc`n''[1,`j'],"%7.0gc")
				local mm "`mm'" ", " "`zz'"
				local j = `j' + 1
			}
			disp " "
			disp in gr "    loc`ii': " in ye "`mm'"
		}
		local j = `i'
		local jj = `ii'
		while (`j'<=`i2'){
			if `free'==1{
				local m = `M_nip'[2,`j']
				capture tempname M_zlc`m'
				matrix `M_zlc`m'' = e(zlc`m')
				scalar `mm0'=0
				local mm = 1
				while `mm'<=`nip'{
					scalar `mm0' = `mm0' + `M_zlc`m''[1,`mm']*`M_zps`lev''[1,`mm']
					local mm = `mm' + 1
				}

				local l = 1
				scalar `var' = 0
				while `l'<=`nip'{		
					scalar `var' = `var' + /*
					*/ (`M_zlc`n''[1,`l']-`mn0')*(`M_zlc`m''[1,`l']-`mm0')*`M_zps`lev''[1,`l']
					local l = `l' + 1
				}
				if `i' == `j'{
					disp in gr "  var(`ii'): " in ye `var'
					*** delete next command
					global HG_var = `var'
					local nb = `M_nbrf'[1,`ii'+`sof']
					if `nb'>1{
						disp " "
						disp in gr "    loadings for random effect " `ii'
						*disp in gr "    coefficient of"
						local load = 1
						while `load'<=`nb'-1{
							local nna: word `nxt' of `names'
							scalar `var'=`b'[1,`nxt']
							scalar `se' = sqrt(`V'[`nxt',`nxt'])
							disp in gr "    `nna': " in ye  `var' " (" `se' ")"
							local nxt = `nxt' + 1
							local load = `load' + 1
						}
						local nxt = `nxt' + 1
						disp " "
					}
				}
				else{
					disp in gr "cov(`ii',`jj'): " in ye `var'
				}
			}
			else{/* free=0 */
				*disp "k= " `k' ", i= " `i' ", j= " `j' ", ii= " `ii' ", jj= " `jj'

				scalar `var' = M_cov[`ii', `jj']
				scalar `se' = sqrt(M_se[`k', `k'])
				if `i' == `j'{
					disp " "
					disp in gr "    var(`ii'): " in ye `var' " (" `se' ")"
					local nb = `M_nbrf'[1,`ii'+`sof']
					if `nb'>1{
						disp " "
						disp in gr "    loadings for random effect " `ii'
						* disp in gr "    coefficient of"
						local load = 1
						while `load'<=`nb'-1{
							local nna: word `nxt' of `names'
							* disp "nxt = " `nxt'
							scalar `var'=`b'[1,`nxt']
							scalar `se' = sqrt(`V'[`nxt',`nxt'])
							disp in gr "    `nna': " in ye `var' " (" `se' ")"
							local nxt = `nxt' + 1
							local load = `load' + 1
						}
						disp " "
					}
					* skip variance parameter
					local nxt = `nxt' + 1
				}
				else{
					if `iscor'==0{
						disp in gr "    cov(`ii',`jj'): " in ye "fixed at 0"
					}
					else{
						scalar `cor' = `var'/sqrt(M_cov[`ii',`ii']*M_cov[`jj',`jj'])
						disp in gr "    cov(`ii',`jj'): " in ye `var' " (" `se' ")" /*
							*/ " cor(`ii',`jj'): " `cor'
						*local nxt = `nxt' + 1
					}
				}
			}

			local j = `j' + 1
			local jj = `jj' + 1
			local k = `k' + 1
		}
		local i = `i' + 1
		local ii = `ii' + 1
	}
local lev = `lev' + 1
/* skip off-diagonal cholesky parameters */
if `iscor'~=0{local nxt = `nxt' + `num'*(`num'-1)/2} /* -1? */
*disp "next nxt is " `nxt'
if `free'{
	local nxt = `nxt'+(`nip'-1)*(`num'+1)
	if `cip'==0{
		local nxt = `nxt'+`num'
	}
	local nxt = `nxt' - 1
}
*disp "next nxt is " `nxt'
}
if `tprf'>1&`bmat'==1{
	disp " "
	disp in gr "B-matrix:"
disp in gr "-----------------------------------------------------------------------------"
	disp " "
	disp " "
	* disp "nxt = " `nxt'
	local i = 1
	while `i'<`tprf'{
		local j = 1
		while `j' < `tprf'{
			if `M_b'[`i',`j']>0{
				scalar `var' =`b'[1,`nxt']
				scalar `se' = sqrt(`V'[`nxt',`nxt'])
				disp in gr "    B(`i',`j'): " in ye `var' " (" `se' ")"
				local nxt = `nxt' + 1
			}
			local j = `j' + 1
		}
		local i = `i' + 1
	}
}
if `ngeqs'>0{
	disp " "
	disp in gr "Regressions of latent variables on covariates"
	disp in gr "-----------------------------------------------------------------------------"
	disp " "
	tempname mngeqs
	matrix `mngeqs' = e(mngeqs)
	local i = 1
	while `i'<=`ngeqs'{
		local k = `mngeqs'[1,`i']
		local n = `mngeqs'[2,`i']
		disp in gr "    random effect " in ye `k' in gr " has " in ye `n' in gr " covariates:"
		local nxt2 = `nxt'+`n'-1
		local j = 1
		while `j' <= `n'{
			local nna: word `nxt' of `names'
			scalar `var'=`b'[1,`nxt']
			scalar `se' = sqrt(`V'[`nxt',`nxt'])
			disp in gr "    `nna': " in ye  `var' " (" `se' ")"
			local nxt = `nxt' + 1
			local j = `j' + 1
		}
		local i = `i' + 1
	}
}
} /* endif toplv >1 */
disp in gr "-----------------------------------------------------------------------------"
disp " "
end

program define sechol
	version 6.0
	args lev num nxt
	* num is number of random effects
	local l = `num'*(`num' + 1)/2 
	disp "lev = `lev' num = `num' nxt = `nxt' l= `l'"
	tempname b V C L zero a H M_nbrf M_nrfc ind

	matrix `M_nbrf' = e(nbrf)
	matrix `M_nrfc' = e(nrfc)
	local iscor = e(cor)
	matrix `b' = e(b)
	matrix `V' = e(V)
	local sof = `M_nrfc'[1,`lev'-1]
	local i = 1
	local k = 1
	matrix `C' = J(`l',`l',0)
	matrix `L' = J(`num',`num',0)
	matrix `ind' = `L'
	* get L matrix
	while `i' <= `num'{
		* skip loading parameters
		local nb = `M_nbrf'[1,`i'+`sof']
		local nxt = `nxt' + `nb' -1
		matrix `L'[`i',`i'] = `b'[1, `nxt']
		matrix `ind'[`i',`i'] = `nxt'
		local nxt = `nxt' + 1
		local i = `i' + 1
	}
	local i = 2
	while `i' <= `num'&`iscor'==1{
		local j = 1
		while `j' < `i'{
			matrix `L'[`i',`j'] = `b'[1, `nxt']
			matrix `ind'[`i',`j'] = `nxt'
			local nxt = `nxt' + 1
			local j = `j' + 1
		}
		local i = `i' + 1
	}
	disp "L and ind"
	matrix list `L'
	matrix list `ind'
	* get C matrix
	local ll1 = 1
	local i = 1
	while `i' <= `num'{
	local j = 1
	while `j' <= `i'{
		local nxt1 = `ind'[`i', `j']
		local ll2 = 1
		local ii = 1
		while `ii' <= `num'{
		local jj = 1
		while `jj' <= `ii'{
			local nxt2 = `ind'[`ii', `jj']
			disp "ll1 = " `ll1' " ll2 = " `ll2' " nxt1 = " `nxt1' " nxt2 = " `nxt2'
			if `iscor' == 1{
				matrix `C'[`ll1', `ll2'] = `V'[`nxt1',`nxt2']
				matrix `C'[`ll2', `ll1'] = `C'[`ll1', `ll2']
			}
			else if `i'==`j'&`ii'==`jj'{
				matrix `C'[`ll1', `ll2'] = `V'[`nxt1',`nxt2']
				matrix `C'[`ll2', `ll1'] = `C'[`ll1', `ll2']
			}
			local ll2 = `ll2' + 1
			local jj = `jj' + 1
		}
		local ii = `ii' + 1
		}
		local ll1 = `ll1' + 1
		local j = `j' + 1
	}
	local i = `i' + 1
	}

	disp "C"
	matrix list `C'
	matrix `zero' = J(`num', `num', 0)
	local k = 1
	local i = 1
	local n = `num' * (`num' + 1)/2
	matrix `H' = J(`n',`n',0)
	while `i' <= `num' {
		local j =  1
		while `j' <= `i'{
			* derivative of LL' with respect to i,j th element of L
			mat `a' = `zero'
			mat `a'[`i',`j'] = 1
			mat `a' = `a'*(`L')'
			mat `a' = `a' + (`a')' 
			disp "a"
			matrix list `a'
			local ii = 1
			local kk = 1
			while `ii'<=`num'{
				local jj = 1
				while `jj' <= `ii'{
					matrix `H'[`kk',`k'] = `a'[`ii',`jj']
					local jj = `jj' + 1
					local kk = `kk' + 1
				}
				local ii= `ii' + 1
			}
			local j = `j' + 1
			local k = `k' + 1
		}
		local i = `i' + 1
	}
	disp "H"
	matrix list `H'
	matrix M_se = `H'*`C'*(`H')'
	matrix M_cov = `L'*(`L')'
	matrix list M_se
	matrix list M_cov
	
end

program define timer
version 6.0
end



