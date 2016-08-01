{smcl}
{* *! version 2.1 9Dec2013}{...}
{viewerjumpto "Syntax" "rdrobust##syntax"}{...}
{viewerjumpto "Description" "rdrobust##description"}{...}
{viewerjumpto "Options" "rdrobust##options"}{...}
{viewerjumpto "Examples" "rdrobust##examples"}{...}
{viewerjumpto "Saved results" "rdrobust##saved_results"}{...}
{title:Title}

{p2colset 5 19 21 2}{...}
{p2col :}Local-Polynomial Regression-Discontinuity Estimation with Robust Confidence Intervals{p_end}
{p2colreset}{...}

{marker syntax}{...}
{title:Syntax}

{p 8 15 2}
{cmd:rdrobust } {it:depvar} {it:indepvar} {ifin} 
[{cmd:,} 
{cmd:c(}{it:#}{cmd:)} 
{cmd:p(}{it:#}{cmd:)} 
{cmd:q(}{it:#}{cmd:)}
{cmd:deriv(}{it:#}{cmd:)}
{cmd:fuzzy(}{it:fuzzyvar}{cmd:)}
{cmd:kernel(}{it:kernelfn}{cmd:)}
{cmd:h(}{it:#}{cmd:)} 
{cmd:b(}{it:#}{cmd:)}
{cmd:rho(}{it:#}{cmd:)}
{cmd:bwselect(}{it:bwmethod}{cmd:)}
{cmd:delta(}{it:#}{cmd:)}
{cmd:cvgrid_min(}{it:#}{cmd:)}
{cmd:cvgrid_max(}{it:#}{cmd:)}
{cmd:cvgrid_length(}{it:#}{cmd:)}
{cmd:cvplot}
{cmd:vce(}{it:vcemethod}{cmd:)}
{cmd:matches(}{it:#}{cmd:)}
{cmd:level(}{it:#}{cmd:)}
{cmd:all} 
]

{synoptset 28 tabbed}{...}

{marker description}{...}
{title:Description}

{pstd}
{cmd:rdrobust} implements a local-polynomial regression discontinuity estimator
with robust confidence intervals as proposed in{browse " http://www-personal.umich.edu/~cattaneo/papers/RD-robust.pdf ": Calonico, Cattaneo and Titiunik (2013a)}. It also computes alternative procedures available in the literature. 

{pstd}
{browse " http://www-personal.umich.edu/~cattaneo/papers/Calonico-Cattaneo-Titiunik_2013_STATA.pdf ": Calonico, Cattaneo and Titiunik (2013b)} 
provides an introduction to this command. Additional details for conventional approaches to conduct inference in the RD design can be found in Imbens and Lemieux (2008), Lee and Lemieux (2010), Dinardo and Lee (2011), and references therein.

{pstd}
A companion {browse "www.r-project.org":R} package is described in{browse " http://www-personal.umich.edu/~cattaneo/papers/Calonico-Cattaneo-Titiunik_2013_JSS.pdf ": Calonico, Cattaneo and Titiunik (2013c)}.


{marker options}{...}
{title:Options}

{phang}
{cmd:c(}{it:#}{cmd:)} specifies the RD cutoff in {it:indepvar}; default is c(0)

{phang}
{cmd:p(}{it:#}{cmd:)} specifies the order of the local-polynomial used to construct the point-estimator; default is {it:p(1)} (local linear regression)

{phang}
{cmd:q(}{it:#}{cmd:)} specifies the order of the local-polynomial used to construct the bias-correction; default is {it:q(2)} (local quadratic regression)

{phang}
{cmd:deriv(}{it:#}{cmd:)} specifies the order of the derivative of the regression function to be estimated; default is {it:deriv(0)} (Sharp RD, or Fuzzy RD if {cmd:fuzzy(.)} is also specified). Setting it equal to 1 results in estimation of a Kink RD design (or Fuzzy Kink RD if {cmd:fuzzy(.)} is also specified))

{phang}
{cmd:fuzzy(}{it:fuzzyvar}{cmd:)} is the treatment status variable used to implement Fuzzy RD estimation (or Fuzzy Kink RD if {it:deriv(1)} is also specified)

{phang}
{cmd:kernel({it:kernelfn})} is the kernel function used to construct the local-polynomial estimator(s). Options are

{synopt :{opt tri:angular; default option}}

{synopt :{opt epa:nechnikov}}

{synopt :{opt uni:form}} 
		
{phang}
{cmd:h(}{it:#}{cmd:)} directly sets the main bandwidth. If not specified, it is computed by the companion command {cmd:rdbwselect}

{phang}
{cmd:b(}{it:#}{cmd:)} directly sets the pilot bandwidth. If not specified, it is computed by the companion command {cmd:rdbwselect}

{phang}
{cmd:rho(}{it:#}{cmd:)} sets the value of {it:rho}, so that the pilot bandwidth equals {it:h/rho}. Default is {it:rho(1)} if {it:h} is 
specified but {it:b} is not. 

{phang}
{cmd:bwselect({it:bwmethod})} selects the bandwidth selection procedure to be used. By default it computes both {it:h} and {it:b},
unless {it:rho} is specified, in which case it only computes {it:h} and sets {it:b=h/rho}

{synopt :{opt CCT} implements Calonico, Cattaneo and Titiunik (2013a) bandwidth selector; default option} 

{synopt :{opt IK} uses the procedure from Imbens and Kalyanaraman (2012)}

{synopt :{opt CV} implements the cross-validation method from Ludwig and Miller (2007)}		

{phang}
{cmd:delta(}{it:#}{cmd:)} sets the quantile that defines the sample used in the cross-validation procedure. This option is used
if {cmd:bwselect({it:CV})} is specified; default is delta(0.5)

{phang}
{cmd:cvgrid_min(}{it:#}{cmd:)} sets the minimum value of the bandwidth grid used in the cross-validation procedure. This option is used
if {cmd:bwselect({it:CV})} is specified

{phang}
{cmd:cvgrid_max(}{it:#}{cmd:)} sets the maximum value of the bandwidth grid used in the cross-validation procedure. This option is used
if {cmd:bwselect({it:CV})} is specified

{phang}
{cmd:cvgrid_length(}{it:#}{cmd:)} sets the bin length of the bandwidth grid used in the cross-validation procedure. This option is used
if {cmd:bwselect({it:CV})} is specified

{phang}
{cmd:cvplot} generates a graph of the CV objective function over the grid being considered. This option is used
if {cmd:bwselect({it:CV})} is specified

{phang}
{cmd:vce({it:vcemethod})} specifies the procedure used to compute the variance-covariance matrix estimator:

{synopt :{opt nn} uses nearest-neighbor matches; default option} 

{synopt :{opt resid} uses the estimated plug-in residuals}

{phang}
{cmd:matches(}{it:#}{cmd:)} sets the number of nearest-neighbor matches for the variance-covariance matrix estimator; 
default is matches(3)

{phang}
{cmd:level(}{it:#}{cmd:)} set confidence level; default is level(95)

{phang}
{cmd:all}  implements three different procedures: conventional RD estimates with conventional standard errors, 
bias-corrected estimates with conventional standard errors, and bias-corrected estimates with robust standard errors.

		
	
    {hline}
	
		
{marker examples}{...}
{title:Example: Cattaneo, Frandsen and Titiunik (2013) Incumbency Data}


    Setup
{phang2}{cmd:. use rdrobust_RDsenate.dta}{p_end}

{pstd}Robust RD Estimation using CCT bandwidth selection procedure{p_end}
{phang2}{cmd:. rdrobust vote margin}{p_end}

{pstd}All three RD Estimation methods, with CCT bandwidth selection procedure{p_end}
{phang2}{cmd:. rdrobust vote margin, all}{p_end}

{pstd}Robust RD Estimation with both bandwidths set to 15{p_end}
{phang2}{cmd:. rdrobust vote margin, h(15)}{p_end}

{pstd}Robust RD Estimation using IK bandwidth selection procedure{p_end}
{phang2}{cmd:. rdrobust vote margin, bwselect(IK)}{p_end}


    Other syntax examples
	
{pstd}Estimation for sharp kink RD{p_end}
{phang2}{cmd:. rdrobust y x, deriv(1)}{p_end}
	
{pstd}Estimation for fuzzy RD{p_end}
{phang2}{cmd:. rdrobust y x, fuzzy(t)}{p_end}

{pstd}Estimation for fuzzy kink RD{p_end}
{phang2}{cmd:. rdrobust y x, fuzzy(t) deriv(1)}{p_end}
	
{marker saved_results}{...}
{title:Saved results}

{pstd}
{cmd:rdrobust} saves the following in {cmd:e()}:

{synoptset 20 tabbed}{...}
{p2col 5 20 24 2: Macros}{p_end}
{synopt:{cmd:e(c)}}cutoff value{p_end}
{synopt:{cmd:e(N_l)}}sample size used to the left of the cutoff{p_end}
{synopt:{cmd:e(N_r)}}sample size used to the right of the cutoff{p_end}
{synopt:{cmd:e(N)}}overall sample size used{p_end}
{synopt:{cmd:e(p)}}order of the polynomial used for estimation of the regression function{p_end}
{synopt:{cmd:e(q)}}order of the polynomial used for estimation of the bias of the regression function estimator{p_end}
{synopt:{cmd:e(h_bw)}}bandwidth used for estimation of the regression function{p_end}
{synopt:{cmd:e(b_bw)}}bandwidth used for estimation of the bias of the regression function estimator{p_end}
{synopt:{cmd:e(tau_cl)}}conventional local-polynomial RD estimate{p_end}
{synopt:{cmd:e(tau_bc)}}bias-corrected local-polynomial RD estimate{p_end}
{synopt:{cmd:e(se_cl)}}conventional standard error of the local-polynomial RD estimate{p_end}
{synopt:{cmd:e(se_rb)}}robust standard error of the local-polynomial RD estimate{p_end}
{synopt:{cmd:e(pv_cl)}}p-values associated with conventional local-polynomial RD estimate{p_end}
{synopt:{cmd:e(pv_bc)}}p-values associated with bias-corrected local-polynomial RD estimate{p_end}
{synopt:{cmd:e(pv_rb)}}p-values associated with robust local-polynomial RD estimate{p_end}
{synopt:{cmd:e(level)}}confidence level{p_end}
	
For a Fuzzy RD, the structural estimates are saved in the following in {cmd:e()}:

{synopt:{cmd:e(tau_F_cl)}}conventional local-polynomial Fuzzy RD estimate{p_end}
{synopt:{cmd:e(tau_F_bc)}}bias-corrected local-polynomial Fuzzy RD estimate{p_end}
{synopt:{cmd:e(se_F_cl)}}conventional standard error of the local-polynomial Fuzzy RD estimate{p_end}
{synopt:{cmd:e(se_F_rb)}}robust standard error of the local-polynomial Fuzzy RD estimate{p_end}
{synopt:{cmd:e(pv_F_cl)}}p-values associated with conventional local-polynomial Fuzzy RD estimate{p_end}
{synopt:{cmd:e(pv_F_bc)}}p-values associated with bias-corrected local-polynomial Fuzzy RD estimate{p_end}
{synopt:{cmd:e(pv_F_rb)}}p-values associated with robust local-polynomial Fuzzy RD estimate{p_end}



{title:References}

{phang}
Calonico, S., Cattaneo, M. D., and R. Titiunik. 2013a. Robust Nonparametric Confidence Intervals for Regression-Discontinuity Designs. University of Michigan, Department of Economics.
{browse " http://www-personal.umich.edu/~cattaneo/papers/RD-robust.pdf"}.

{phang}
Calonico, S., Cattaneo, M. D., and R. Titiunik. 2013b. Robust Data-Driven Inference in the Regression-Discontinuity Design. University of Michigan, Department of Economics. 
{browse " http://www-personal.umich.edu/~cattaneo/papers/Calonico-Cattaneo-Titiunik_2013_STATA.pdf"}.

{phang}
Calonico, S., Cattaneo, M. D., and R. Titiunik. 2013c. rdrobust: An R Package for Robust Inference in Regression-Discontinuity Designs. University of Michigan, Department of Economics. 
{browse " http://www-personal.umich.edu/~cattaneo/papers/Calonico-Cattaneo-Titiunik_2013_JSS.pdf "}.

{phang}
Cattaneo, M. D., Frandsen, B., and R. Titiunik. 2013. Randomization Inference in the Regression Discontinuity Design: An Application to the Study of Party Advantages in the U.S. Senate. University of Michigan, Department of Economics.
{browse "http://www-personal.umich.edu/~cattaneo/papers/RndInfRD.pdf"}.

{phang}
Dinardo, J., and D. S. Lee. 2011. Program Evaluation and Research Designs. In Handbook of Labor Economics, ed. O. Ashenfelter and D. Card, vol. 4A, 463-536. Elsevier Science B.V.

{phang}
Imbens, G., and T. Lemieux. 2008. Regression Discontinuity Designs: A Guide to Practice. Journal of Econometrics 142(2): 615-635.

{phang}
Imbens, G. W., and K. Kalyanaraman. 2012. Optimal Bandwidth Choice for the Regression Discontinuity Estimator. Review of Economic Studies 79(3): 933-959.

{phang}
Lee, D. S., and T. Lemieux. 2010. Regression Discontinuity Designs in Economics. Journal of Economic Literature 48(2): 281-355.

{phang}
Ludwig, J., and D. L. Miller. 2007. Does Head Start Improve Children's Life Chances? Evidence from a Regression Discontinuity Design. Quarterly Journal of Economics 122(1): 159-208.


{title:Authors}

{phang}
Sebastian Calonico, University of Michigan, Ann Arbor, MI.
{browse "mailto:calonico@umich.edu":calonico@umich.edu}.

{phang}
Matias D. Cattaneo, University of Michigan, Ann Arbor, MI.
{browse "mailto:cattaneo@umich.edu":cattaneo@umich.edu}.

{phang}
Rocio Titiunik, University of Michigan, Ann Arbor, MI.
{browse "mailto:titiunik@umich.edu":titiunik@umich.edu}.


