*! mixlog_d1 1.0.0 10Oct2007
*! author arh

program define mixlog_d1 
	version 9.2
	args todo b lnf g negH

	mata: mixl_ll("`b'")
	scalar `lnf' = r(ll)

	if (`todo'==0 | `lnf'>=.) exit
	matrix `g' = r(gradient)

	if (`todo'==1 | `lnf'>=.) exit
	matrix `negH' = r(invcov)
end

version 9.2
mata: 
void mixl_ll(string scalar B_s)
{
	external mixl_X
	external mixl_Y
	external mixl_T
	external mixl_CSID
	external mixl_WGT

	external mixl_nrep
	external mixl_np
	external mixl_kfix
	external mixl_krnd
	external mixl_krln
	external mixl_burn
	external mixl_robust
	external mixl_cluster
	external mixl_corr
	external mixl_wgttyp

	nrep = mixl_nrep
	np = mixl_np
	kfix = mixl_kfix
	krnd = mixl_krnd
	krln = mixl_krln
	burn = mixl_burn
	robust = mixl_robust
	cluster = mixl_cluster
	corr = mixl_corr
	wgttyp = mixl_wgttyp

	B = st_matrix(B_s)'

	kall = kfix + krnd
	
	if (kfix > 0) {
		MFIX = B[|1,1\kfix,1|]
		MFIX = MFIX :* J(kfix,nrep,1)	
	}

	MRND = B[|(kfix+1),1\kall,1|]
	
	if (corr == 1) {
		external mixl_ncho
		ncho = mixl_ncho 
		SRND = invvech(B[|(kall+1),1\(kall+ncho),1|]) :* lowertriangle(J(krnd,krnd,1))
	}
	else {
		SRND = diag(B[|(kall+1),1\(kfix+2*krnd),1|])
	}

	P = J(np,1,0)

	if (corr == 1) {
		G = J(np,(kall+ncho),0)
	}
	else {
		G = J(np,(kfix+2*krnd),0)
	}

	i = 1
	for (n=1; n<=np; n++) {
		ERR = invnormal(halton(nrep,krnd,(1+burn+nrep*(n-1)))')
		if (kfix > 0) BETA = MFIX \ (MRND :+ (SRND*ERR))
		else BETA = MRND :+ (SRND*ERR)
		if (krln > 0) {
			if ((kall-krln) > 0) {
				BETA = BETA[|1,1\(kall-krln),nrep|] \ exp(BETA[|(kall-krln+1),1\kall,nrep|])
			}
			else {
				BETA = exp(BETA)
			}
		}
		R = J(1,nrep,1)

		if (corr == 1) {
			M = J((kall+ncho),nrep,0)
		}
		else {
			M = J((kfix+2*krnd),nrep,0)
		}

		t = 1
		nc = mixl_T[i,1]
		for (t=1; t<=nc; t++) {

			YMAT = mixl_Y[|i,1\(i+mixl_CSID[i,1]-1),cols(mixl_Y)|]
			XMAT = mixl_X[|i,1\(i+mixl_CSID[i,1]-1),cols(mixl_X)|]

			EV = exp(XMAT*BETA)
			EV = (EV :/ colsum(EV))	
			R = R :* colsum(YMAT :* EV)

			PMAT = YMAT :- EV
			for (j=1; j<=kall; j++) {
				if (j <= (kall-krln)) {
					M[j,.] = M[j,.] :+ colsum(PMAT :* XMAT[.,j])
				}
				else {
					M[j,.] = M[j,.] :+ colsum(PMAT :* XMAT[.,j]) :* BETA[j,.]
				}
			}
			if (corr == 1) {
				num = 1
				for (j=1; j<=krnd; j++) {
					for (k=j; k<=krnd; k++) {
						if (k <= (krnd-krln)) {
							M[(kall+num),.] = M[(kall+num),.] :+ colsum(PMAT :* XMAT[.,(kfix+k)]) :* ERR[j,.]
						}
						else {
							M[(kall+num),.] = M[(kall+num),.] :+ colsum(PMAT :* XMAT[.,(kfix+k)]) :* BETA[(kfix+k),.] :* ERR[j,.]
						}
						num = num + 1
					}
				}
			}
			else {
				for (j=1; j<=krnd; j++) {
					if (j <= (krnd-krln)) {
					 	M[(kall+j),.] = M[(kall+j),.] :+ colsum(PMAT :* XMAT[.,(kfix+j)]) :* ERR[j,.]
					}
					else {
					 	M[(kall+j),.] = M[(kall+j),.] :+ colsum(PMAT :* XMAT[.,(kfix+j)]) :* BETA[(kfix+j),.] :* ERR[j,.]
					}
				}
			}
			i = i + mixl_CSID[i,1]
		}
		P[n,1] = mean(R',1)
		G[n,.] = (1 :/ mean(R',1)) :* mean((R:*M)',1)
	}
	st_numscalar("r(ll)", colsum(mixl_WGT:*ln(P)))
	st_matrix("r(gradient)", colsum(mixl_WGT:*G))	

	if ((robust == 1) | (cluster == 1)) {
		external mixl_V
		if (cluster == 1) {
			external mixl_CLUST
			external mixl_nclust
			nclust = mixl_nclust 
			G = mixl_bysum(G,mixl_CLUST,mixl_WGT,nclust)
			st_matrix("r(invcov)", invsym((nclust/(nclust-1))*(mixl_V*cross(G,G)*mixl_V)))
		}
		else {
			if ((wgttyp == "iweight") | (wgttyp == "pweight")) {
				st_matrix("r(invcov)", invsym((np/(np-1))*(mixl_V*cross(G,(mixl_WGT:^2),G)*mixl_V)))
			}
			else {
				npw = colsum(mixl_WGT)
				st_matrix("r(invcov)", invsym((npw/(npw-1))*(mixl_V*cross(G,mixl_WGT,G)*mixl_V)))
			}
		}
	}
}
end	

version 9.2
mata:
function mixl_bysum(G,CLUST,WGT,nclust)
{
	SRTO = order(CLUST,1)

	G = G[SRTO,.]
	CLUST = CLUST[SRTO,1]
	WGT = WGT[SRTO,1]

	S = J(nclust,cols(G),0)
	S[1,.] = WGT[1,.]:*G[1,.]

	j = 2
	n = 1
	while (j <= rows(G)) {
		if (CLUST[j,1] == CLUST[(j-1),1]) {
			S[n,.] = S[n,.] :+ WGT[j,.]:*G[j,.]
			j = j + 1
		}
		else {
			n = n + 1
			S[n,.] = S[n,.] :+ WGT[j,.]:*G[j,.]
			j = j + 1
		}
	}
	return(S)
}
end

exit




			


