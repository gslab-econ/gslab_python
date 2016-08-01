{smcl}

{* * ! version 1.0 7-23-2011}{...}
{cmd:help gsum}
{hline}

{title:Title}

{p2colset 5 18 20 2}{...}
{p2col :{hi:gsum} {hline 2}}Summary statistics for grouped data{p_end}
{p2colreset}{...}

{title:Syntax}
{p 8 17 2}
{cmd:gsum} {varlist} {ifin} {weight} {cmd:,} [{it:options}] [{it:group definitions}]

{synoptline}

{syntab:{it:Specifiying Group Ranges}}

{syntab:{cmd:gsum} accepts variables with codes from 0 to 25 (integers only).}

{syntab:Elements of {it:group definitions} can be {it:g0(#-#)}, {it:g1(#-#)}...{it:g#(#-#)} where {it:g#} identifies the group number and {it:(#-#)} identifies a numeric range.}

{syntab:If, however, {it:varlist} has each category labeled in the format of {it:#-#}, {cmd:gsum} can simply use these values.}

{syntab:If you do not specify {it:group definitions}, {cmd:gsum} will look for labels.}

{syntab:If you do specify {it:group definitions}, {cmd:gsum} will ignore the labels.}

{synoptset 26 tabbed}{...}
{synopthdr}
{synoptline}

{synopt :{cmd:quantiles({it:q q ...})}} the set of quantiles to be calculated, the default set is 0.25, 0.50, and 0.75. {p_end}

{synopt :{cmd:gen({it:newvarlist})}} create new variable called {it:newvarlist} containing the midpoints. {p_end}

{synopt :{cmd:table}} display the value table. {p_end}

{synopt :{cmd:save({it:filename})}} save the value table to {it:filename}. {p_end}

{synoptline}

{title:Description}

{pstd}{cmd:gsum} calculates summary statistics for an ordinal variable where each category represents a
range of a conceptually continuous variable. {cmd:gsum} provides the weighted {it:N}, the mean, the standard deviation, and quantiles 0.25, 0.50 (the median),
and 0.75 (you can specify any set of quantiles you want).  Each quantile is available as both the midpoint of the
category in which the quantile falls, or as a linear interpolation of that quantile based on methods presented
by Blalock (1979).

{pstd}{cmd:gsum} can also produce a value table (which can also be saved) listing each category, the range, the
midpoint of that range, the number of cases, the weight of each case, and the cumulative distribution function (CDF).

{pstd}For an extra tool, {cmd:gsum} can also create a new variable that contains the midpoints.

{pstd}{cmd:gsum} accepts any type of {weight} and is byable.

{pstd}For example, you may have a variable {it:age_cat} where 1
represents 18-24 years of age, 2 represents 25-44 years of age, and 3 represents 45-100 years of age.
You can use {cmd:gsum} to calculate summary statistics such as the mean, median, and standard deviation.

{title:Examples}

{pstd}Use the 2010 GSS data on age

{phang}{cmd:. use gssage.dta, clear} {p_end}

{pstd}If the variable {it:age_cat} is labled correctly,

{phang}{cmd:. gsum age_cat} {p_end}

{pstd}Or, if you are not sure,

{phang}{cmd:. gsum age_cat, g1(18-24) g2(25-44) g3(45-100)} {p_end}

{pstd}To use weights,

{phang}{cmd:. gsum age_cat [pweight = wtssall]} {p_end}

{pstd}To see the value table,

{phang}{cmd:. gsum age_cat, table} {p_end}

{pstd}To save the value table in the file {it:valuetable.dta},

{phang}{cmd:. gsum age_cat, save(valuetable.dta)} {p_end}

{pstd}To create the variable {it:midpoint_age_cat},

{phang}{cmd:. gsum age_cat, gen(midpoint_age_cat)} {p_end}

{pstd}You can also enter in data from a frequency table.  For example, there is a table in Blalock (1979) that shows the frequency of cases for different income ranges:

         Income Range  Frequency
         {hline 23}
         1950-2950        17
         2950-3950        26
         3950-4950        38
         4950-5950        51
         5950-6950        36
         6950-7950        21
         {hline 23}
         Total           189

{pstd}You can input this table into Stata as a categorical variable and frequencies:

{phang}{cmd:. clear} {p_end}
{phang}{cmd:. input y f} {p_end}
{phang}{cmd:1. 1 17 } {p_end}
{phang}{cmd:2. 2 26 } {p_end}
{phang}{cmd:3. 3 38 } {p_end}
{phang}{cmd:4. 4 51 } {p_end}
{phang}{cmd:5. 5 36 } {p_end}
{phang}{cmd:6. 6 21 } {p_end}
{phang}{cmd:7. end  } {p_end}

{pstd}You can then label the categories

{phang}{cmd:. label def money  1 "1950-2950" 2 "2950-3950"  3 "3950-4950" 4 "4950-5950" 5 "5950-6950" 6 "6950-7950"} {p_end}
{phang}{cmd:. label val y money}

{pstd}Then use frequency weights

{phang}{cmd:. gsum y [fweight = f], table quantiles(0.50)}

{title:Saved results}

{pstd}
{cmd:gsum} saves the following in {cmd:r()}:

{synoptset 20 tabbed}{...}
{p2col 5 20 24 2: Scalars}{p_end}
{synopt:{cmd:r(N)}}the number of observations{p_end}
{synopt:{cmd:r(sum_W)}}the sum of the weights{p_end}
{synopt:{cmd:r(mean)}}the mean{p_end}
{synopt:{cmd:r(var)}}the variance{p_end}
{synopt:{cmd:r(sd)}}the standard deviation{p_end}
{synopt:{cmd:r(mn)}}the minimum{p_end}
{synopt:{cmd:r(mx)}}the maximum{p_end}
{synopt:{cmd:r(qi{it:q})}}the {it:q} quantile using the interpolation method{p_end}
{synopt:{cmd:r(qm{it:q})}}the {it:q} quantile using the midpoint method{p_end}

{title:Acknowledgments}

The algorithms used in this program are based on
{phang}Blalock, H.M. 1979. Social Statistics.  2nd Ed. McGraw-Hill: New York

{title:Contact}

{pstd}This program was written by Eric Hedberg, National Opinion Research Center at the University of Chicago.  
Any questions or comments can be directed to ech@uchicago.edu.


