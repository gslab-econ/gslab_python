{smcl}
{* 18feb2004 M Blasnik}{...}
{hline}
help for {hi:matrix_to_txt}
{hline}

{title:Export Matrix to Text File}

{p 8 13 2}{cmd:matrix_to_txt} {cmd:,} {cmdab:m:atrix:(}{it:matrixname}{cmd:)}
	{cmdab:sav:ing:(}{it:filename}{cmd:)} [
	{cmdab:t:itle:(}{it:text}{cmd:)} {cmdab:not:e:(}{it:text}{cmd:)}
        {cmdab:f:ormat:(}{it:formatlist}{cmd:)} {cmdab:rep:lace} {cmdab:app:end} {cmdab:usec:olnames} {cmdab:user:ownames}]


{title:Description}

{p 4 4 2}
{cmd:matrix_to_txt} exports a Stata matrix to a text file for use in other programs
such as word processors or spreadsheets.  The matrix row and column names
as well as the matrix data values are exported to a tab delimited ASCII file.
The user may optionally specify a title and/or a note to add text to the file
before and/or after the matrix.  Display formats may be specified.  The data may
be appended to an existing file or replace an existing file. [Modified by MG from mat2txt


{title:Options}

{p 4 8 2}
{cmd:matrix(}{it:matrixname}{cmd:)} is required as it specifies the name of the matrix
to export.  To save estimation results, first copy the matrix out from e() into a
regular Stata matrix, then export that matrix.

{p 4 8 2}
{cmd:saving(}{it:filename}{cmd:)} is required as it provides the name of the ASCII
file to save. If no file extension is provided, .txt will be added to the end of the filename.

{p 4 8 2}
{cmd:title(}{it:text}{cmd:)} specifies text to be output before the matrix is written
to the file.

{p 4 8 2}
{cmd:note(}{it:text}{cmd:)} specifies text to be output after the matrix is written
to the file.

{p 4 8 2}
{cmd:format(}{it:formatlist}{cmd:)} allows the user to specify Stata display formats
for the data values.  If one value is specified, all columns are output with that
format.  If more than one space-delimited format is listed, they are mapped 1-to-1
to the columns of the matrix.

{p 4 8 2}
{cmd:replace} allows overwriting an existing file.

{p 4 8 2}
{cmd:append} specifies that output is to be appended onto an existing file.

{p 4 8 2}
{cmd:usecolnames} specifies that output is to include column headers.

{p 4 8 2}
{cmd:userownames} specifies that output is to include row names.

{title:Examples}

    {cmd:. matrix_to_txt, matrix(mycorr1) saving(mytable) title(Table 1. Correlations) }
    {cmd:. matrix_to_txt, matrix(mycoef1) saving(mytable) append title(Table 2. Coeffs, Std Errs, and t stats) format(%6.0f %6.1f %5.3f) }

to get summary statistics produced by tabstat into a tab delimited file:

    {cmd:. tabstat price weight, by(foreign) stats(sum) save}
    {cmd:. tabstatmat matvars}
    {cmd:. matrix_to_txt, matrix(matvars) saving(mytable1) }

(note: tabstatmat is available from SSC)


{title:Authors}

{p 4 4 2}
Michael Blasnik (M. Blasnik & Associates, Boston, MA) {break}
Email: {browse "mailto:michael.blasnik@verizon.net":michael.blasnik@verizon.net}

{p 4 4 2}
Ben Jann (ETH Zurich) {break}
Email: {browse "mailto:jann@soz.gess.ethz.ch":jann@soz.gess.ethz.ch}

{p 4 4 2}
Matthew Gentzkow {break}

