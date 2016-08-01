{smcl}
{* 02july2008}{...}
{hline}
help for {hi:eclplot}{right:(Roger Newson)}
{right:dialog:  {dialog eclplot:{bf:eclplot}} {dialog eclplot_98s:small {bf:eclplot} dialog for Windows 98/ME users} }
{hline}


{title:Plot estimates with confidence limits}

{p 8 21 2}{cmd:eclplot} {it:estimate_varname clmin_varname clmax_varname parmid_varname} {ifin} [{cmd:,}
{cmdab:hor:izontal}
{cmdab:eplot:type}{cmd:(}{it:eplot_type}{cmd:)}
{cmdab:rplot:type}{cmd:(}{it:rplot_type}{cmd:)}
{cmdab::no}{cmdab:cif:oreground}
{break} {cmd:estopts(}[{it:eplot_options}] [, {it:weight}]{cmd:)}
{break} {cmd:ciopts(}[{it:rplot_options}] [, {it:weight}]{cmd:)}
{break} {cmd:supby(}{it:supby_varname} [, {it:supby_suboptions}]{cmd:)}
{break} {cmd:estopts1(}[{it:eplot_options}] [, {it:weight}]{cmd:)} ... {cmd:estopts15(}[{it:eplot_options}] [, {it:weight}]{cmd:)}
{break} {cmd:ciopts1(}[{it:rplot_options}] [, {it:weight}]{cmd:)} ... {cmd:ciopts15(}[{it:rplot_options}] [, {it:weight}]{cmd:)}
{break} {cmd:addplot(}{it:plot}{cmd:)} {cmd:plot(}{it:plot}{cmd:)} {cmd:baddplot(}{it:plot}{cmd:)} {cmdab::no}{cmdab:gr:aph}
{break} {it:{help twoway_options}} ]

{pstd}
where {it:estimate_varname}, {it:clmin_varname} and {it:clmax_varname}
are names of numeric variables containing parameter estimates, lower confidence limits, upper confidence limits,
respectively, to be plotted on one axis,
{it:parmid_varname} is a parameter identity variable
to determine the position of each confidence interval on the other axis,
{it:eplot_type} is

{pstd}
{cmdab:sc:atter} | {cmdab:co:nnected} | {cmdab:li:ne} | {cmdab:ar:ea} | {cmdab:ba:r} | {cmdab:sp:ike} | {cmdab:dr:opline}

{pstd}
and {it:rplot_type} is

{pstd}
{cmdab:ra:rea} | {cmdab:rb:ar} | {cmdab:rs:pike} | {cmdab:rc:ap} | {cmdab:rcaps:ym} | {cmdab:rsc:atter} | {cmdab:rl:ine} | {cmdab:rco:nnected}

{pstd}
The {it:{help twoway_options}} are as specified for {helpb twoway};
see help for {it:{help twoway_options}}.


{title:Description}

{pstd}
{cmd:eclplot} creates a plot of estimates with lower and upper confidence limits
on one axis against another variable on the other axis.
The estimates and lower and upper confidence limits are stored in three variables,
with one observation per confidence interval plotted.
Data sets with such variables may be created by
the {helpb parmest} package (downloadable from {help ssc:SSC}), or by {helpb statsby}
or {helpb postfile} in official Stata.
The user has a choice of plotting the confidence intervals horizontally or vertically,
a choice of estimate plot types for the estimates,
and a choice of range plot types for the confidence intervals,
and may also overlay the confidence interval plot
with other plots using the {help addplot_option:addplot option}.
In default, {cmd:eclplot} does not print a legend unless multiple superimposed confidence interval plots are requested,
and has "sensible" settings for axis titles and labels
(see help for {it:{help axis_title_options}} and {it:{help axis_options}}).
However, these defaults may be overridden, using the {it:{help twoway_options}}.


{title:Options}

{p 4 8 2}
{cmd:horizontal} specifies that the confidence intervals must be plotted horizontally,
with the estimates and confidence limits on the horizontal axis and the other variable on the vertical axis.
In default, if {cmd:horizontal} is not specified,
the confidence intervals are plotted vertically,
with the estimates and confidence limits on the vertical axis
and the other variable on the horizontal axis.

{p 4 8 2}
{cmd:eplottype(}{it:eplot_type}{cmd:)} specifies the estimate plot type used to plot the estimates.
The value of this option may be any one of the {helpb twoway} plot types {helpb twoway_scatter:scatter},
{helpb twoway_connected:connected}, {helpb twoway_line:line}, {helpb twoway_area:area},
{helpb twoway_bar:bar}, {helpb twoway_spike:spike}, and {helpb twoway_dropline:dropline}.
If the {cmd:eplottype()} option is not specified, then it is set to {helpb twoway_scatter:scatter},
and the estimates are drawn as symbols.

{p 4 8 2}
{cmd:rplottype(}{it:rplot_type}{cmd:)} specifies the range plot type used to plot the confidence intervals.
The value of this option may be any one of the range plot types allowed by {helpb twoway},
namely {helpb twoway_rarea:rarea}, {helpb twoway_rbar:rbar},
{helpb twoway_rspike:rspike}, {helpb twoway_rcap:rcap}, {helpb twoway_rcapsym:rcapsym},
{helpb twoway_rscatter:rscatter}, {helpb twoway_rline:rline}, and {helpb twoway_rconnected:rconnected}.
If the {cmd:rplottype} option is not specified, then it is set to {helpb twoway_rcap:rcap},
and the confidence limits are drawn with capped spikes.

{p 4 8 2}
{cmd:nociforeground} specifies whether the confidence intervals are in the foreground
(where they can overwrite the estimates) or in the background (where the estimates can overwrite them).
If neither {cmd:ciforeground} nor {cmd:nociforeground} is specified,
then a sensible default is decided as follows.
First, the {cmd:eplottype()} option is assigned a group rank,
which is 1 for {helpb twoway_scatter:scatter}, {helpb twoway_connected:connected} and {helpb twoway_line:line},
2 for {helpb twoway_dropline:dropline} and {helpb twoway_spike:spike}, 3 for {helpb twoway_bar:bar},
and 4 for {helpb twoway_area:area}.
Then, the {cmd:eplottype()} option is assigned a group rank,
which is 1 for {helpb twoway_rscatter:rscatter}, {helpb twoway_rconnected:rconnected} and {helpb twoway_rline:rline},
2 for {helpb twoway_rcapsym:rcapsym}, {helpb twoway_rcap:rcap} and {helpb twoway_rspike:rspike},
3 for {helpb twoway_rbar:rbar}, and 4 for {helpb twoway_rarea:rarea}.
Then, the {cmd:nociforeground} option is set to {cmd:ciforeground} if the {cmd:rplottype()} group rank
is equal to or less than the {cmd:eplottype()} group rank, and is set to {cmd:nociforeground} otherwise.
The default rule can therefore be described as
"symbols and connecting lines in front of spikes in front of bars in front of areas",
and was chosen to minimize the probability of important information being hidden.

{p 4 8 2}
{cmd:estopts(}[{it:eplot_options}] [, {it:weight}]{cmd:)} specifies any plot options for the plotting of the estimates.
These options may be any of the options allowed for the estimate plot type
specified by the {cmd:eplottype()} option.
To find more about the options allowed by each estimate plot type, see help for
{helpb twoway} and for the individual plot types
{helpb twoway_scatter:scatter},
{helpb twoway_connected:connected}, {helpb twoway_line:line}, {helpb twoway_area:area},
{helpb twoway_bar:bar}, {helpb twoway_spike:spike}, and {helpb twoway_dropline:dropline}.
The optional {it:weight} is a {help weight:weight specification}, of the general form
{cmd:[}{it:weighttype}={it:expression}{cmd:]},
where {it:weighttype} may be {cmd:aweight}, {cmd:fweight} or {cmd:pweight},
and {it:expression} is a Stata expression or variable name.
If it is present, and if the user has also specified the {cmd:eplottype()} option
as {helpb twoway_dropline:dropline}, {helpb twoway_scatter:scatter} or {helpb twoway_connected:connected},
then it specifies that the marker symbol sizes will be weighted
by the value of the {it:expression}, which must be non-negative.
The {it:weight} can be useful for creating Cochrane forest plots for meta-analyses,
in which the marker symbol is often proportional to the study size.

{p 4 8 2}
{cmd:ciopts(}[{it:rplot_options}] [, {it:weight}]{cmd:)} specifies any plot options for drawing the confidence limits.
These options may be any of the options allowed for the range plot type specified by the
{cmd:rplottype()} option, which may be any of the range plot options allowed by {helpb twoway},
and defaults to {helpb twoway_rcap:rcap}.
For instance, the user may specify the width of the caps on each confidence limit.
To find more about the options allowed by each range plot type, see help for
{helpb twoway}, for {helpb twoway_scatter:scatter}, and for the individual range plot types
{helpb twoway_rarea:rarea}, {helpb twoway_rbar:rbar},
{helpb twoway_rspike:rspike}, {helpb twoway_rcap:rcap}, {helpb twoway_rcapsym:rcapsym},
{helpb twoway_rscatter:rscatter}, {helpb twoway_rline:rline}, and {helpb twoway_rconnected:rconnected}.
The optional {it:weight} is a {help weight:weight specification}, of the general form
{cmd:[}{it:weighttype}={it:expression}{cmd:]},
where {it:weighttype} may be {cmd:aweight}, {cmd:fweight} or {cmd:pweight},
and {it:expression} is a Stata expression or variable name.
If it is present, and if the user has also specified the {cmd:rplottype()} option
as {helpb twoway_rcapsym:rcapsym}, {helpb twoway_rscatter:rscatter} or {helpb twoway_rconnected:rconnected},
then it specifies that the cap symbol sizes will be weighted
by the value of the {it:expression}, which must be non-negative.

{p 4 8 2}
{cmd:supby(}{it:supby_varname} [, {it:supby_suboptions}]{cmd:)} specifies that multiple superimposed plots
of estimates and confidence limits will be created,
one for each value of the variable {it:supby_varname}, with distinct styles.
There can be up to 15 superimposed plots.
Unless the user specifies otherwise, a legend will be created,
identifying each plot with a value of the variable {it:supby_varname}.
The suboptions of the {cmd:supby()} option are listed below under
{helpb eclplot##supby_subopts:Suboptions of the supby() option}.

{p 4 8 2}
{cmd:estopts1(}[{it:eplot_options}] [, {it:weight}]{cmd:)} ... {cmd:estopts15(}[{it:eplot_options}] [, {it:weight}]{cmd:)}
are only used if a {cmd:supby()} option is specified.
They specify plot options specific to the individual superimposed estimates plots,
additional to the plot options specified for all estimate plots by the {cmd:estopts()} option.
If the {it:weight} is specified, then it overrides any {it:weight} specified by the {cmd:estopts()} option.

{p 4 8 2}
{cmd:ciopts1(}[{it:rplot_options}] [, {it:weight}]{cmd:)} ... {cmd:ciopts15(}[{it:rplot_options}] [, {it:weight}]{cmd:)}
are only used if a {cmd:supby()} option is specified.
They specify plot options specific to the individual superimposed confidence limit plots,
additional to the plot options specified for all confidence limit plots by the {cmd:ciopts()} option.
If the {it:weight} is specified, then it overrides any {it:weight} specified by the {cmd:ciopts()} option.

{p 4 8 2}
{cmd:addplot(}{it:plot}{cmd:)} provides a way to add additional plots to the generated graph
in the foreground (in front of the estimates and confidence intervals).
For instance, a user may wish to display sample numbers in the plot,
alongside the confidence intervals.
See help for {it:{help addplot_option}}.

{p 4 8 2}
{cmd:plot(}{it:plot}{cmd:)} is an obsolete alternative name for the {cmd:addplot()} option,
used by earlier versions of {cmd:eclplot}.
It is provided so that old do-files will still run.

{p 4 8 2}
{cmd:baddplot(}{it:plot}{cmd:)} provides a way to add additional plots to the generated graph
in the background (behind the estimates and confidence intervals).

{p 4 8 2}
{cmd:nograph} specifies that no graph will be drawn.
This option is useful if the user is building a {helpb twoway} command
from subcommands returned in {hi:r()} by {cmd:eclplot}
(see {helpb eclplot##saved_results:Saved results} below).

{p 4 8 2}
{it:twoway_options} are any of the options documented in help for {it:{help twoway_options}}.
These include options for titling the graph (see help for {it:{help title_options}}),
options for saving the graph to disk (see help for {it:{help saving_option}}),
the {cmd:legend()} option (see help for {it:{help legend_option}}),
and the {cmd:by()} option (see help for {it:{help by_option}}).
In default, {cmd:eclplot} sets the {cmd:legend()} option to {cmd:legend(off)}
(implying no legend) if the {cmd:supby()} option is not specified,
and sets the contents of the legend to contain a key for each value of the {cmd:supby()} variable
if {cmd:supby()} is specified.
If the user specifies a {cmd:by()} option without a {cmd:legend()} suboption,
then the {cmd:legend()} suboption is set by default to {cmd:legend(off)} if {cmd:supby()} is not specified,
and to {cmd:legend(on)} if {cmd:supby()} is specified.
Therefore, in default, {cmd:eclplot} draws a legend if and only if the user specifies the {cmd:supby()} option.
THese defaults add to and/or override any defaults set by the {helpb scheme:graphics scheme} currently in use,
and can in turn be added to and/or overridden using options set by the user.


{marker supby_subopts}{...}
{title:Suboptions of the {cmd:supby()} option}

{pstd}
The {cmd:supby()} option has the syntax

{p 8 21 2}{cmd:supby(} {it:supby_varname} [ , {cmdab:m:issing} {cmdab:t:runcate}{cmd:(}{it:num}{cmd:)}
{cmdab:spa:ceby}{cmd:(}{it:num}{cmd:)} {cmdab:off:set}{cmd:(}{it:num}{cmd:)} ]
{cmd:)}

{pstd}
The suboptions are as follows:

{p 4 8 2}
{cmd:missing} specifies that superimposed plots will be produced for missing values of the variable {it:supby_varname}.

{p 4 8 2}
{cmd:truncate(}{it:num}{cmd:)} specifies that, in the {help legend_option:legend},
the values of the variable {it:supby_varname} will be truncated to the length {it:num}.

{p 4 8 2}
{cmd:spaceby(}{it:num}{cmd:)} specifies a number, in units of the parameter identification variable {it:parmid_varname},
by which the superimposed plots corresponding to successive values of the variable {it:supby_varname}
will be spaced on the axis corresponding to the parameter identification variable.
This option is used to prevent multiple superimposed plots from obscuring each other.
If {cmd:spaceby()} is not specified, then it is set to zero, implying no spacing.

{p 4 8 2}
{cmd:offset(}{it:num}{cmd:)} specifies a number, in units of the parameter identification variable {it:parmid_varname},
by which the superimposed plot corresponding to the first value of the variable {it:supby_varname}
will be displaced from the value implied by the variable {it:parmid_varname}.
This number may be positive or negative.
If {cmd:offset()} is not specified, then it is set to zero,
implying that the plot corresponding to the first value of the variable {it:supby_varname}
will not be displaced from its true value.
In general, the positions of the plots on the axis corresponding to the parameter identification variable {it:parmid_varname}
is given by the formula

{p 8 8 2}
{it:parmpos = parmid_varname + offset + spaceby*(supby_seqnum-1)}

{p 8 8 2}
where {it:parmpos} is the position of the plot on the axis, {it:offset} is the value of the {cmd:offset()} suboption,
{it:spaceby} is the value of the {cmd:spaceby{}} option, and {it:supby_seqnum} is the ascending sequential order
of the value of the variable {it:supby_varname} corresponding to the plot.


{title:Remarks}

{pstd}
{cmd:eclplot} plots confidence intervals against another variable.
More information about {cmd:eclplot}, and about the creation of datasets for input to {cmd:eclplot},
can be found in Newson (2003), Newson (2004), Newson (2005) and Newson (2006).

{pstd}
Data sets used by {cmd:eclplot} may be created manually using a spreadsheet.
However, they may also be created by the {helpb parmest}
package, downloadable from {help ssc:SSC}.
The {helpb parmest} package stores results from an {help estimates:estimation command}
as an output dataset (or resultsset).
(See also help for {help _estimates} or {helpb ereturn}.)
It creates a dataset with one observation per model parameter,
or one observation per parameter per by-group,
and data on parameter names, estimates, confidence limits, and other parameter attributes.
The other variable, against which the confidence intervals are plotted,
may be any numeric variable, but is often a categorical factor
included as a predictor in the model fitted by the estimation command
using the {helpb xi} utility.
To reconstruct such a categorical factor in a {helpb parmest} output dataset,
the user may use the {helpb factext} and {helpb descsave} packages, also downloadable from {help ssc:SSC}.
Alternatively, the user may use the {helpb parmest} package, possibly with the {helpb label} option,
and then use the {helpb sencode} package (also downloadable from {help ssc:SSC})
to encode the {hi:parm} or {hi:label} string variable in the output dataset
to a numeric variable, which may be plotted by {cmd:eclplot}
against the estimates and confidence limits.

{pstd}
Under Windows 98/ME, the {dialog eclplot:default {bf:eclplot} dialog} should not be used,
as it requires too much memory.
Windows 98 users who want to use dialogs with {cmd:eclplot}
should therefore use the {dialog eclplot_98s:small {bf:eclplot} dialog for Windows 98/ME users}.
(See help for {help smalldlg} for technical details on small dialogs for Windows 98/ME users.)

{pstd}
Under Stata 7, the present author usually plotted confidence intervals using either
the {help graph7:Stata 7 graph command} (with the {cmd:connect()} option) or
Nicholas J. Cox's {helpb hplot} package, downloadable from {help ssc:SSC}.
The {helpb hplot} package is a very comprehensive package for general horizontal plots.
The {cmd:eclplot} package, on its own, cannot entirely supersede {helpb hplot},
but the two packages perform overlapping sets of functions,
and may possibly be viewed as being complementary.


{title:Examples}

{pstd}
The following examples use the {hi:auto} data, shipped with official Stata
(see help for {helpb sysuse}).
A regression model is fitted for the {it:Y}-variable {hi:mpg}
(miles per gallon), predicted by the categorical variables {hi:rep78} (repair record) and {hi:foreign}.
The {helpb parmby} command of the {helpb parmest} package is used to create an output dataset (or resultsset)
with one observation per parameter and data on estimates and confidence limits.
The {helpb sencode} package is used to create a numeric variable (with value labels),
encoding the model parameter corresponding to each observation.
Finally, {cmd:eclplot} is used to display the confidence intervals.
The first example uses parameter names to label a vertical confidence interval plot.
The second example uses parameter labels to label a horizontal confidence interval plot.
The third example uses parameter labels to label a horizontal "detonator plot".

{p 4 8 2}{cmd:. sysuse auto,clear}{p_end}
{p 4 8 2}{cmd:. parmby "xi:regress mpg i.foreign i.rep78", label norestore}{p_end}
{p 4 8 2}{cmd:. sencode parm,gene(parmid)}{p_end}
{p 4 8 2}{cmd:. eclplot estimate min95 max95 parmid}{p_end}

{p 4 8 2}{cmd:. sysuse auto,clear}{p_end}
{p 4 8 2}{cmd:. parmby "xi:regress mpg i.foreign i.rep78", label norestore}{p_end}
{p 4 8 2}{cmd:. sencode label,gene(parmlab)}{p_end}
{p 4 8 2}{cmd:. eclplot estimate min95 max95 parmlab, hori}{p_end}

{p 4 8 2}{cmd:. sysuse auto,clear}{p_end}
{p 4 8 2}{cmd:. parmby "xi:regress mpg i.foreign i.rep78", label norestore}{p_end}
{p 4 8 2}{cmd:. sencode label, gene(parmlab)}{p_end}
{p 4 8 2}{cmd:. eclplot estimate min95 max95 parmlab, hori eplot(bar)}{p_end}

{pstd}
The following advanced example fits the same model to the same data with a different parameterization,
and uses the {helpb descsave} and {helpb factext} packages as well as {helpb parmby}.
It creates two confidence interval plots.
The first plot displays two confidence intervals for the mean mileage levels
expected for cars from the USA and from elsewhere with {hi:rep78==0}.
The second plot displays confidence intervals
for the difference in mileage expected for each non-zero level of {hi:rep78},
with a dotted reference line on the horizontal axis,
indicating the difference of zero expected if {hi:rep78} has no independent effect on {hi:mpg}.
The plots demonstrate the use of the options {cmd:estopts} and {cmd:ciopts}
and the use of the {it:{help twoway_options}}.

{p 4 8 2}{cmd:. sysuse auto,clear}{p_end}
{p 4 8 2}{cmd:. tab foreign,gene(orig_) nolabel}{p_end}
{p 4 8 2}{cmd:. tempfile tf0}{p_end}
{p 4 8 2}{cmd:. descsave foreign rep78,do(`tf0')}{p_end}
{p 4 8 2}{cmd:. parmby "xi:regress mpg orig_* i.rep78,noconst",label norestore}{p_end}
{p 4 8 2}{cmd:. factext,do(`tf0')}{p_end}
{p 4 8 2}{cmd:. eclplot estimate min95 max95 foreign,hori estopts(msize(vlarge)) ciopts(msize(vlarge)) yscale(range(-1 2)) ylab(0 1) xtitle("Mean mileage per gallon")}{p_end}
{p 4 8 2}{cmd:. eclplot estimate min95 max95 rep78,hori estopts(msize(vlarge)) ciopts(msize(vlarge)) yscale(range(1 6)) xline(0,lpattern(dot)) xtitle("Mean difference (miles per gallon)")}{p_end}

{pstd}
The following example also uses {helpb parmby} and {helpb sencode}.
It demonstrates the use of the {cmd:supby()} option of {cmd:eclplot}
to produce multiple superimposed detonator plots.

{p 4 8 2}{cmd:. sysuse auto, clear}{p_end}
{p 4 8 2}{cmd:. tabulate rep78, gene(rep78_)}{p_end}
{p 4 8 2}{cmd:. parmby "regress mpg rep78_*, noconst", by(foreign) label norestore}{p_end}
{p 4 8 2}{cmd:. sencode label if parm!="_cons", gene(parmlab)}{p_end}
{p 4 8 2}{cmd:. lab var parmlab "Repair record 1978"}{p_end}
{p 4 8 2}{cmd:. lab var estimate "Mean mileage (mpg)"}{p_end}
{p 4 8 2}{cmd:. eclplot estimate min95 max95 parmlab, eplot(bar) estopts(barwidth(0.25)) supby(foreign, spaceby(0.25)) xscale(range(0 6)) xlabel(1(1)5, angle(30))}{p_end}
{p 4 8 2}{cmd:. more}{p_end}
{p 4 8 2}{cmd:. eclplot estimate min95 max95 parmlab, eplot(bar) ciopts(blcolor(black)) estopts(barwidth(0.25)) estopts1(bcolor(red)) estopts2(bcolor(blue)) supby(foreign, spaceby(0.25)) xscale(range(0 6)) xlabel(1(1)5, angle(30))}{p_end}
{p 4 8 2}{cmd:. more}{p_end}


{marker saved_results}{...}
{title:Saved results}

{pstd}
{cmd:eclplot} saves the following results in {cmd:r()}:

{synoptset 15 tabbed}{...}
{p2col 5 15 19 2: Macros}{p_end}
{synopt:{cmd:r(addplot)}}Contents of the {helpb addplot_option:addplot()} option{p_end}
{synopt:{cmd:r(baddplot)}}Contents of the {cmd:baddplot()} option{p_end}
{synopt:{cmd:r(plot)}}Contents of the {cmd:plot()} option{p_end}
{synopt:{cmd:r(allplots)}}Sequence of {helpb twoway} plot subcommands generated by {cmd:eclplot}{p_end}
{synopt:{cmd:r(ifin)}}{helpb if} and/or {helpb in} qualifiers{p_end}
{synopt:{cmd:r(twowayopts)}}{help twoway_options:twoway options} generated by {cmd:eclplot}{p_end}
{synopt:{cmd:r(cmd)}}{helpb twoway} command generated by {cmd:eclplot}{p_end}
{p2colreset}{...}

{pstd}
{cmd:eclplot} works by constructing a {helpb twoway} command, which it then executes,
unless {cmd:nograph} is specified.
Users can use the saved {helpb twoway} plot subcommands, qualifiers and options to build {helpb twoway} commands of their own.
The result {cmd:r(allplots)} contains a sequence of {helpb twoway} plot subcommands separated by {cmd:||}.
The result {cmd:r(cmd)} contains a command, which can be specified by the {help macro:macro expression}

{p 4 8 2}{cmd:twoway `r(allplots)' || `r(ifin)' , `r(twowayopts)'}{p_end}

{pstd}
and which is executed by {cmd:eclplot} to produce the plot.
Note that, if the {cmd:supby()} option is specified,
then {cmd:r(allplots)} will contain {help tempvar:temporary variable names},
belonging to temporary variables used within {cmd:eclplot},
and therefore cannot be used to build new {helpb twoway} plot commands.


{title:Acknowledgements}

{pstd}
I would like to thank Jean Marie Linhart and James Hassell of StataCorp
for their very helpful advice on writing the dialogs for {cmd:eclplot},
and also Vince Wiggins of StataCorp for his very helpful advice on writing {cmd:eclplot}.


{title:Author}

{pstd}
Roger Newson, Imperial College London, UK.
Email: {browse "mailto:r.newson@imperial.ac.uk":r.newson@imperial.ac.uk}


{title:References}

{phang}
Newson, R.  2003.  Confidence intervals and {it:p}-values for delivery to the end user.
{it:The Stata Journal} 3(3): 245-269.
Pre-publication draft downloadable from
{net "from http://www.imperial.ac.uk/nhli/r.newson":Roger Newson's website at http://www.imperial.ac.uk/nhli/r.newson}.

{phang}
Newson, R.  2004.  From datasets to resultssets in Stata.
Presented at {browse "http://ideas.repec.org/s/boc/usug04.html" :the 10th United Kingdom Stata Users' Group Meeting, London, 29 June, 2004}.
Also downloadable from
{net "from http://www.imperial.ac.uk/nhli/r.newson":Roger Newson's website at http://www.imperial.ac.uk/nhli/r.newson}.

{phang}
Newson, R.  2005.  Generalized confidence interval plots using commands or dialogs.
Presented at {browse "http://ideas.repec.org/s/boc/usug05.html" :the 11th United Kingdom Stata Users' Group Meeting, London, 17 May, 2005}.
Also downloadable from
{net "from http://www.imperial.ac.uk/nhli/r.newson":Roger Newson's website at http://www.imperial.ac.uk/nhli/r.newson}.

{phang}
Newson, R.  2006.  Resultssets, resultsspreadsheets, and resultsplots in Stata.
Presented at {browse "http://ideas.repec.org/s/boc/dsug06.html" :the 4th German Stata Users' Group Meeting, Mannheim, 31 March, 2006}.
Also downloadable from
{net "from http://www.imperial.ac.uk/nhli/r.newson":Roger Newson's website at http://www.imperial.ac.uk/nhli/r.newson}.


{title:Also see}

{p 4 13 2}
{bind: }Manual: {hi:[G] graph intro}, {hi:[G] graph twoway}
{p_end}
{p 4 13 2}
On-line: help for {helpb twoway}, {helpb graph}, {helpb graph_intro}, {helpb graph7}, {it:{help addplot_option}}{break}
help for {helpb parmest}, {helpb sencode}, {helpb factext}, {helpb descsave}, {helpb hplot} if installed
{p_end}
