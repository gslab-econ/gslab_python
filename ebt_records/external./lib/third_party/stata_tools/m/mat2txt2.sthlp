{smcl}
{* $Id$ }
{* $Date$}{...}
{cmd:help mat2txt2}
{hline}

{title:Title}

{p2colset 5 18 20 2}{...}
{p2col:{hi:mat2txt2 }{hline 2}}Export matrix to text file.{p_end}
{p2colreset}{...}

{title:Syntax}


{p 8 16 2}
{cmdab:mat2txt2} {it:mname} [{it:mname2 mname3...}] [{cmdab:using} {it:filename}]   [, options]

	
{synoptset 20 tabbed}{...}
{synopthdr}
{synoptline}
{syntab:Text file formatting options}
{synopt:{opt del:imit}({it:char})}Specify a column delimiter.{p_end}
{synopt:{opt com:ma}}Synonym for {opt delimit}(,).{p_end}
{synopt:{opt t:ab}}Synonym for {opt delimit}(_tab), the default.{p_end}
{synopt:{opt f:ormat(%fmt)}}Specify Stata display formats for the data values.{p_end}

{syntab:Title and note options}
{synopt :{opt tit:le(text)}}Specifies text to be included before anything else is written to the file.{p_end}
{synopt :{opt mat:names}}Specify that matrix name is included in output above the matrix.{p_end}
{synopt :{opt not:e(text)}}Specifies text to be included after everything else is written to the file.{p_end}
{synopt :{opt file:stamp}}Prints filename at top of the file (this request is ignored if using -handle- options).{p_end}
{synopt :{opt tim:estamp}}Add the date and time to the bottom of the file.{p_end}

{syntab:Row and column label options}
{synopt :{opt rowcl:ean}}Suppress the display of matrix row names.{p_end}
{synopt :{opt colcl:ean}}Suppress the display of matrix column names.{p_end}
{synopt :{opt cl:ean}}Shorthand for "{opt rowclean} {opt colclean}".{p_end}
{synopt :{opt rowl:abel}}Attempt to replace row labels with a corresponding variable/value labels.{p_end}
{synopt :{opt coll:abel}}Attempt to replace column labels with a corresponding variable/value labels.{p_end}
{synopt :{opt l:abel}}Shorthand for "{opt rowlabel} {opt collabel}".{p_end}

{syntab:File location*}
{synopt :{opt using}  }Specify a {it:filename} for output.{p_end}
{synopt :{opt h:andle(handle_name)}}Specify the name of a {help file} handle, to which the output will be added.{p_end}

{syntab:Additional options with {opt using} {it:filename}}
{synopt :{opt rep:lace}}allows overwriting an existing {it:filename}.{p_end}
{synopt :{opt app:end}}specifies that output is to be appended onto an existing {it:filename}.{p_end}
{synoptline}
{pstd}You must specify a {help using} filename or the {opt handle} option, but not both.{p_end}
{p2colreset}{...}


{title:Description}

{pstd}{cmd:mat2txt2} exports one or more Stata matrices to a text file for use in other programs
such as word processors or spreadsheets.  Matrix row and column names, as well as the matrix data 
values are exported to a delimited ASCII file.  The user may, optionally, specify a title and/or a 
note to add text to the file before and/or after the matrix (matrices).  Display formats may be specified.  

{pstd}The typical use is to specify a filename with the {help using} qualifier.  If this is
the case, the file can be appended to an existing file or replace an existing file. 
Alternatively, {opt handle(handle_name)} specifies the name of a {help file} handle.  
The program assumes that this file has already been opened for output.  The program then adds the 
specified output, without closing the file.  

{pstd}The {opt clean} option supresses all column and row labels. 
If the row or column labels contain variable names, consider using the {opt label} option; 
in this case, the variable label is substituted in place of the variable name. 

{pstd}{it:matname} may include estimation matrices such as e(b) and e(V).
Users may also export more than one matrix; in this case,
the title, note, and timestamp is included only once.

{pstd}After the command is finished, it provides links for the user to click to
view the file in Stata's viewer or with the default Windows program.


{title:Examples}

{phang}{cmd:. mat2txt2 mycorr1 using myfilename.csv }{p_end}
{phang}{cmd:. mat2txt2 mycorr1 using myfilename.txt, tab title(Table 1)}{p_end}

{phang}{cmd:. regress y x1 x2 x3}{p_end}
{phang}{cmd:. mat2txt2 e(b) e(V) using "c:\data\output file.csv", replace matname timestamp} {p_end}

{phang}{cmd:. file open myhandle using "c:\data\output file.csv",  } {p_end}
{phang}{cmd:. mat2txt2 e(b) e(V) , h(myhandle)} {p_end}
{phang}{cmd:. file close myhandle} {p_end}


{title:Other Information}
{* $Id$ }
{phang}Author: Keith Kranker{p_end}

{phang}$Date${p_end}

{psee}
Credits: This program is an updated/modified version of the file {stata findit mat2txt:mat2txt.ado}
by Michael Blasnik (M. Blasnik & Associates, Boston, MA) and Ben Jann (ETH Zurich).  

{psee}
Changes from the original program are additions to the base program or cosmetic changes: {break}
(1) Updated syntax to {it:mat2txt2 matname using ... , options }{break}
(2) Allow multiple matrices. Allow e() and r() matrices. {break}
(3) Replace cells equal to .z with empty cells {break}
(4) Options to choose file delimiter. 
(5) Matnames and Timestamp options {break}
(6) Allow user to click on a link to view or open the output file.{break}
(7) Handle option (Version 1.1+) {break}
(8) Clean option (Verson 1.2+) {break}
(9) Label option (Verson 1.3+){break}
(10) Default delimiter is "_tab"  (previously ",") (Version 1.3+)  {break}
(11) Filestamp option (Verson 1.4+) {break}
(12) Rowclean, colclean, rowlabel, and collabel options (Verson 1.5+) {break}


{title:Also see}

{psee}
Help:  
{help matrix}, {help estimates}, {help file}, {help shellout}, 
{help mat2txt} (if {stata findit mat2txt:installed})
{p_end}

This command works well with {help meantab}.
