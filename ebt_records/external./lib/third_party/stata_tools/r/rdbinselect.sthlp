{smcl}
{* *! version 2.1 9Dec2013}{...}
{viewerjumpto "Syntax" "rdbinselect##syntax"}{...}
{viewerjumpto "Description" "rdbinselect##description"}{...}
{viewerjumpto "Options" "rdbinselect##options"}{...}
{viewerjumpto "Examples" "rdbinselect##examples"}{...}
{viewerjumpto "Saved results" "rdbinselect##saved_results"}{...}
{title:Title}

{p2colset 5 19 21 2}{...}
{p2col :} Data-driven optimal length selector of evenly-spaced bins employed to approximate the underlying regression functions in RD Estimation{p_end}

{p2colreset}{...}

{marker syntax}{...}
{title:Syntax}

{p 8 15 2}
{cmd:rdbinselect } {it:depvar} {it:indepvar} {ifin} 
[{cmd:,} 
{cmd:c(}{it:#}{cmd:)} 
{cmd:p(}{it:#}{cmd:)}
{cmd:lowerend(}{it:#}{cmd:)} 
{cmd:upperend(}{it:#}{cmd:)} 
{cmd:scale(}{it:#}{cmd:)}
{cmd:scalel(}{it:#}{cmd:)}
{cmd:scaler(}{it:#}{cmd:)}
{cmd:numbinl(}{it:#}{cmd:)}
{cmd:numbinr(}{it:#}{cmd:)}
{cmd:generate(}{it:id_var meanx_var meany_var}{cmd:)}
{cmd:graph_options(}{it:gphopts}{cmd:)}
{it:hide}]


{synoptline}

{marker description}{...}
{title:Description}

{pstd}
{cmd:rdbinselect} implements a data-driven optimal length choice of evenly-spaced bins used to approximate the underlying regression functions 
in RD estimation, employing the results in{browse " http://www-personal.umich.edu/~cattaneo/papers/Cattaneo-Farrell_2013_JoE.pdf ": Cattaneo and Farrell (2013, Theorem 3)}.

{pstd}
{browse " http://www-personal.umich.edu/~cattaneo/papers/Calonico-Cattaneo-Titiunik_2013_STATA.pdf ": Calonico, Cattaneo and Titiunik (2013a)} 
provides an introduction to this command. For review on RD methods see Imbens and Lemieux (2008), Lee and Lemieux (2010), 
Dinardo and Lee (2011), and references therein.

{pstd}
A companion {browse "www.r-project.org":R} package is described in{browse " http://www-personal.umich.edu/~cattaneo/papers/Calonico-Cattaneo-Titiunik_2013_JSS.pdf ": Calonico, Cattaneo and Titiunik (2013b)}.

{marker options}{...}
{title:Options}

{phang}
{cmd:c(}{it:#}{cmd:)} specifies the RD cutoff in {it:indepvar}; default is c(0)

{phang}
{cmd:p(}{it:#}{cmd:)} specifies the order of the global-polynomial used to approximate the population conditional
mean functions for control and treated units; default is p(4)

{phang}
{cmd:lowerend(}{it:#}{cmd:)} sets the lower bound for {it:indepvar} to the left of the cutoff; default is its minimum value

{phang}
{cmd:upperend(}{it:#}{cmd:)} sets the upper bound for {it:indepvar} to the right of the cutoff; default is its maximum value

{phang}
{cmd:scale(}{it:#}{cmd:)} specifies a multiplicative factor to be used with the optimal number of bins selected. Specifically, 
the number of bins used for the treatment and control groups will be <{cmd:scale(}{it:#}{cmd:)} * J+ > and <{cmd:scale(}{it:#}{cmd:)} * J- >, 
where J denotes the optimal numbers of bins originally computed for each group.

{phang}
{cmd:scalel(}{it:#}{cmd:)} specifies a multiplicative factor to be used with the optimal number of bins selected to the left of the cutoff. Specifically, 
the number of bins used will be <{cmd:scalel(}{it:#}{cmd:)} * J- >.

{phang}
{cmd:scaler(}{it:#}{cmd:)} specifies a multiplicative factor to be used with the optimal number of bins selected to the right of the cutoff. Specifically, 
the number of bins used will be <{cmd:scaler(}{it:#}{cmd:)} * J+ >.

{phang}
{cmd:numbinl(}{it:#}{cmd:)} directly specifies the number of bins selected to the left of the cutoff. 

{phang}
{cmd:numbinr(}{it:#}{cmd:)} directly specifies the number of bins selected to the right of the cutoff.

{phang}
{cmd:generate({it:id_var} {it:meanx_var} {it:meany_var})} specifies the names for new generated variables with a unique bin id,
the sample-mean within bins of the running variable, and the sample-mean within bins of the outcome variable, respectively. 
For {it:id_var}, negative interger values are assigned to control units and positive interger values to treated ones.

{phang}
{cmd:graph_options(}{it:gphopts}{cmd:)} specifies graph-options to be passed on to the underlying graph command.

{phang}
{cmd:hide} omit the final RD plot


	{hline}


{marker examples}{...}
{title:Example: Cattaneo, Frandsen and Titiunik (2013) Incumbency Data}

    
    Setup
{phang2}{cmd:. use rdrobust_RDsenate.dta}{p_end}

{pstd}Basic specification with title{p_end}
{phang2}{cmd:. rdbinselect vote margin, graph_options(title(RD Plot))}{p_end}

{pstd}Setting lower and upper bounds on the running variable{p_end}
{phang2}{cmd:. rdbinselect vote margin, lowerend(-50) upperend(50)}{p_end}



{marker saved_results}{...}
{title:Saved results}

{pstd}
{cmd:rdbinselect} saves the following in {cmd:e()}:

{synoptset 20 tabbed}{...}
{p2col 5 20 24 2: Macros}{p_end}
{synopt:{cmd:e(J_star_l)}} number of bins to the left of the cutoff{p_end}
{synopt:{cmd:e(J_star_r)}} number of bins to the right of the cutoff{p_end}
{synopt:{cmd:e(binlength_l)}} length of bins to the left of the cutoff{p_end}
{synopt:{cmd:e(binlength_r)}} length of bins to the right of the cutoff{p_end}

{synoptset 20 tabbed}{...}
{p2col 5 20 24 2: Matrices}{p_end}
{synopt:{cmd:e(gamma_p1_l)}} coefficients of the {it:p}-th order polynomial estimated to the left of the cutoff{p_end}
{synopt:{cmd:e(gamma_p1_r)}} coefficients of the {it:p}-th order polynomial estimated to the right of the cutoff{p_end}



{title:References}

{phang}
Calonico, S., Cattaneo, M. D., and R. Titiunik. 2013a. Robust Data-Driven Inference in the Regression-Discontinuity Design. University of Michigan, Department of Economics. 
{browse " http://www-personal.umich.edu/~cattaneo/papers/Calonico-Cattaneo-Titiunik_2013_STATA.pdf"}.

{phang}
Calonico, S., Cattaneo, M. D., and R. Titiunik. 2013b. rdrobust: An R Package for Robust Inference in Regression-Discontinuity Designs. University of Michigan, Department of Economics. 
{browse " http://www-personal.umich.edu/~cattaneo/papers/Calonico-Cattaneo-Titiunik_2013_JSS.pdf "}.

{phang}
Cattaneo, M. D., and M. H. Farrell. 2013.  Optimal Convergence Rates, Bahadur Representation, and Asymptotic Normality of Partitioning Estimators. Journal of Econometrics 174(2): 127-143.
{browse "http://www-personal.umich.edu/~cattaneo/papers/Cattaneo-Farrell_2013_JoE.pdf"}.

{phang}
Cattaneo, M. D., Frandsen, B., and R. Titiunik. 2013. Randomization Inference in the Regression Discontinuity Design: An Application to the Study of Party Advantages in the U.S. Senate. University of Michigan, Department of Economics.
{browse "http://www-personal.umich.edu/~cattaneo/papers/RndInfRD.pdf"}.

{phang}
Dinardo, J., and D. S. Lee. 2011. Program Evaluation and Research Designs. In Handbook of Labor Economics, ed. O. Ashenfelter and D. Card, vol. 4A, 463-536. Elsevier Science B.V.

{phang}
Imbens, G., and T. Lemieux. 2008. Regression Discontinuity Designs: A Guide to Practice. Journal of Econometrics 142(2): 615-635.

{phang}
Lee, D. S., and T. Lemieux. 2010. Regression Discontinuity Designs in Economics. Journal of Economic Literature 48(2): 281-355.



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


