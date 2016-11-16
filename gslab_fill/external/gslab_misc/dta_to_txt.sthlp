{smcl}
{* *! version 1.0  19sep2009}{...}
{cmd:help dta_to_txt}
{hline}

{title:Title}

{p2colset 5 21 23 2}{...}
{p2col :{hi:dta_to_txt} {hline 2}}Write dta file to text{p_end}
{p2colreset}{...}


{title:Syntax}

{p 8 17 2}
{cmdab:dta_to_txt}
[{it:varlist}]
{ifin}
{cmd:,} {opt sav:ing(filename)} {it:options}


{synoptset 21 tabbed}{...}
{synopthdr}
{synoptline}
{syntab :Main}
{synopt :{cmdab:dta("}{it:filename}{cmd:")}} use {it:filename} as
        dta file to output to text{p_end}
{synopt :{cmdab:title("}{it:str}{cmd:")}}print {it:str} as
         title in output file before writing data{p_end}
{synopt :{opt c:omma}}output in comma-separated (instead of tab separated)
format{p_end}
{synopt :{cmdab:delim:iter("}{it:char}{cmd:")}}use {it:char} as
         delimiter{p_end}
{synopt :{opt non:ames}}do not write variable names on the first line{p_end}
{synopt :{opt nol:abel}}output numeric values (not labels) of labeled
variables{p_end}
{synopt :{opt noq:uote}}do not enclose strings in double quotes{p_end}

{p2coldent :+ {opt replace}}overwrite existing {it:filename}{p_end}
{p2coldent :+ {opt append}}append to existing {it:filename}{p_end}

{synoptline}
{p 4 6 2}
If your {it:filename} contains embedded spaces, remember to enclose
it in double quotes.{p_end}
{p 4 6 2}
If your {it:inputfile} is not specified, dta_to_txt writes the current file in memory


{title:Description}

{pstd}
{opt dta_to_txt} is exactly like {opt outsheet}, except that it allows any .dta file to
be specified as input and allows the output to be appended to a text file rather than
just replacing it. It also allows a title to be written on the first line.

