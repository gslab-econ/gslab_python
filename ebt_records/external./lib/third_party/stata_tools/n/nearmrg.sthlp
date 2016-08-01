{smcl}
{* 29jan2012} {...}
{hline}
help for {hi:nearmrg}
{hline}

{title:Nearest match merging of datasets}


{p 4 8 2}{cmd:nearmrg} [{it:varlist}] {cmd:using} {cmd:,}
	{cmdab:n:earvar(}{it:varname}{cmd:)} [ {cmdab:lim:it(}{it:real}{cmd:)} {cmdab:g:enmatch(}{it:newvarname}{cmd:)} 
	{cmdab:low:er} {cmdab:up:per} {cmdab:ro:undup} {cmdab:type:(}{it:mergetype}{cmd:)} {it: mergeoptions}] {p_end}


{title:Description}

{p}{cmd:nearmrg} performs nearest match merging of two datasets on the values of the numeric variable {it:nearvar}.  {cmd:nearmrg} was designed as a way to use 
lookup tables that have binned or rounded values on the variable of interest.{p_end}

{p}The user specifies whether the master dataset should be matched with observations in the using dataset with the value closest and higher (or {bf: upper}) than each {it:nearvar} value, or observations nearest and {bf:lower} than near values.{{p_end}}

{p} Since the {it:nearvar} must be a numeric variable, be sure to convert any time-date string variables to their numeric equivalent (see {help datetime}).  Variables may be specified in an optional {it:varlist} and these variables are treated as  standard merge variable which must match exactly. This option allows nearest matching  within subsets defined by the varlist.  {cmd:nearmrg} requires Stata 11+ since it utilizes the newer {help merge} command syntax. {p_end}


{title:Options}

{p 0 4}{cmd:nearvar()} is required and specifies the variable in the master and using datasets that is to be 
matched as closely as possible.  {cmd:nearvar()} is not optional and must be unique in the using 
dataset, but not necessarily in the master dataset.{p_end}


{p 0 4}{cmd:limit()} is optional and specifies a limit to how far away from the master dataset value the matched using dataset value can be.  For a {cmd:nearvar()} that represents days or date-time, you can specify "limit(90)" to limit matches to within 90 days of the matching date.{p_end}


{p 0 4}{cmd:lower, upper, roundup} are mutually exclusive options that alter the default approach to defining the nearest match 
for {cmd:nearvar}.  {cmd:lower} matches to the closest value of {cmd:nearvar} in the using dataset that is less than 
or equal to {cmd:nearvar} in the master dataset.  {cmd:upper} matches to the closest value that is greater than or 
equal to {cmd:nearvar}.  {cmd:roundup} breaks distance ties by always selecting the higher value instead of the default
lower value.  If none of these options are specified, {cmd:nearmrg} matches to the closest observation defined as minimizing
the absolute difference between {cmd:nearvar} in the master and using datasets.  {p_end}

{p 0 4}{cmd:type()} is an advanced option that overrides the default {it:mergetype} {bf:m:1}.  See the help {help merge} documentation for information on the other available {it:mergetype}s (e.g., m:1, 1:m, m:m, 1:1).{p_end}

{p 0 4}{cmd:genmatch()} is optional and specifies that a new variable should be created in the master datset that identifies the 
specific value of {cmd:nearvar} in the using dataset that was matched.  {p_end}

{p 0 4}{cmd:mergeoptions} allows the user to specify any of the standard Stata {help merge} options (such as
{cmd:update} or {cmd: replace}).  See {help merge} for more on these options.{p_end}



{title:Example}

//Find car prices in "autoexpense.dta" within $50 of "auto.dta"//

**1:  create 'using' data**
webuse autoexpense.dta, clear
rename make make2
sa "using.dta", replace

**2:  merge to auto.dta by price**
sysuse auto.dta, clear
nearmrg  using "using.dta", upper nearvar(price) genmatch(usingmatch) limit(50) 
list make* price  usingmatch _m if inrange(_m, 3, 5)





{title:Authors}
{p 2 6 4}Current version of {bf:nearmrg} (updated for Stata 11+ merge syntax) is written and maintained by:{p_end}
	
	{bf:Eric A. Booth}
	Public Policy Research Institute
	Texas A&M University
	ebooth@tamu.edu
	http://www.eric-a-booth.com


	{p 6 6 4}*Original {bf:nearmrg} package appeared in 2003 and was co-authored by:{p_end}
	 Michael Blasnik
	 M Blasnik & Associates
	 michael.blasnik@verizon.net
	
	 Katherine Smith
	 Clinical Epidemiology and Biostatistics Unit
	 Murdoch Childrens Research Institute
	 katherine.smith@mcri.edu.au


{title:Also See}

{p 0 19}On-line:  help for {help merge}{p_end}
