{smcl}
{hline}
help for {hi:plotmatrix}
{hline}

{title:Plot values of a matrix as different coloured blocks}

{p 8 27}
{opt plotmatrix}
,
{opt m:at(matrix_name)}
[
{opt s:plit(numlist)}
{opt c:olor(colorstyle)}
{opt allcolors(color list)}
{opt nodiag}
{opt addbox(numlist)}
{opt u:pper}
{opt l:ower}
{opt d:istance(varname)}
{opt du:nit(string)}
{opt maxt:icks(#)}
{opt freq}
{opt formatcells(%fmt)}
]

{p}

{title:Description}

{p 0 0}
This command will display the values of a matrix using {hi:twoway area}.
Each value of the matrix will be represented by a coloured rectangular block.
A legend is automatically created using percentiles but the user can also
specify how to split the data.

{p 0 0}
For genetic data there is an additional function to show the genomic distances between markers. 
The genomic position is entered using the {hi:distance()} option. 

{title:Updating this command}

{p 0 0} 
To obtain the latest version click the following to uninstall the old version

{stata ssc uninstall plotmatrix}

And click here to install the new version

{stata ssc install plotmatrix}

{title:Options}

{p 0 0}
{cmdab:m:at}{cmd:(}{it:matrix_name}{cmd:)} specifies the name of the matrix to plot. Note that for matrices e(b) and e(V) the user must create a new matrix using the {help matrix} command.

{p 0 0}
{cmdab:s:plit}{cmd:(}{it:numlist}{cmd:)} specifies the cutpoints used in the legend. Note that if the matrix contains values outside the range of the number list then the values will not be plotted. 
The default will be a number list containing the min, max and 10 other percentiles.

{p 0 0}
{cmdab:c:olor}{cmd:(}{it:string}{cmd:)} specifies the colour of the blocks used. The default colour is bluish gray. Note that RGB and CMYK colors are not accepted and colors should be specified by the word list 
in {help colorstyle} e.g. brown.

{p 0 0}
{cmdab:allcolors}{cmd:(}{it:string}{cmd:)} specifies the colours of the blocks used. Note you need to specify all the colours rather than a single colour used by
the color() option.

{p 0 0}
{cmdab:nodiag} specifies that the diagonal of the matrix is not represented in the graph.

{p 0 0}
{cmdab:addbox}{cmd:(}{it:numlist}{cmd:)} specifies that areas of the graph will be enclosed within a box. 
The arguments of this option are groups of 4 numbers representing the (y,x) points of two extreme vertices of the box.

{p 0 0}
{cmdab:u:pper} specifies that only the upper diagonal matrix be plotted.

{p 0 0}
{cmdab:l:ower} specifies that only the lower diagonal matrix be plotted.

{p 0 0}
{cmdab:d:istance}{cmd:(}{it:varname}{cmd:)} specifies the physical distances between rows/columns in the 
matrix. This is mostly useful for plotting a pairwise LD matrix to include the genomic distances between markers.

{p 0 0}
{cmdab:du:nit}{cmd:(}{it:string}{cmd:)} specifies the units of the distances specified in the {hi:distance} 
variable. The default is Megabases but can be any string.

{p 0 0}
{opt maxt:icks(#)} specifies the maximum number of ticks on both the y and x axes. The default is 8.

{p 0 0}
{opt freq} specifies that the matrix values are displayed within each coloured box.

{p 0 0}
{opt formatcells(%fmt)} specifies the format of the displayed matrix values within each coloured box.

{title:Examples}

{p 0 0}
Plotting the values of a variance covariance matrix


{p 2}
{stata sysuse auto}   <--- click this {bf:first} to load data

{p 2}
{stata reg price mpg trunk weight length turn, nocons}

{p 2}
{stata mat regmat = e(V)}

{p 2}
{stata plotmatrix, m(regmat) c(green) ylabel(,angle(0))}

{p 2}
{stata plotmatrix, m(regmat) allcolors(green*1 green*0.8 green*0.6 green*0.4 red*0.4 red*0.6 red*0.8 red*1.0 ) ylabel(,angle(0))}

{p 2}
To make the plot above more square use the aspect() option but you might want to make the text smaller in the legend so that 
the y-axis is closer to the interior of the plot.

{p 2}
{stata plotmatrix, m(regmat) allcolors(green*1 green*0.8 green*0.6 green*0.4 red*0.4 red*0.6 red*0.8 red*1.0 ) ylabel(,angle(0)) aspect(1) legend(size(*.4) symx(*.4))}

{p 2}
Plotting the values of a correlation matrix of a given varlist

{p 2}
{stata matrix accum R = price mpg trunk weight length turn , nocons dev}

{p 2}
{stata matrix R = corr(R)}

{p 2}
{stata plotmatrix, m(R) s(-1(0.25)1) c(red)}

By specifying the freq option the correlations are additional printed within each
coloured box. Negating the need for a legend. 
{p 2}
{stata plotmatrix, m(R) s(-1(0.25)1) c(red) freq legend(off)}
{stata plotmatrix, m(R) s(-1(0.25)1) c(red) freq aspect(1) legend(size(*.4) symx(*.4))}

With additional formatting on the cells
{stata plotmatrix, m(R) s(-1(0.25)1) c(red) freq formatcells(%5.2f) aspect(1) legend(size(*.4) symx(*.4))}

{title:Genetic Examples}

{p 0 0}
Plotting the values of a point-wise LD map (see command {bf:pwld}), with boxes around two areas defined by variables 1-5 and variables 11-18.

{p 2 0}
{inp:.pwld l1_1-l76_2, mat(grid)}

{p 2 0}
{inp:.plotmatrix, mat(grid) split( 0(0.1)1 ) c(gray) nodiag addbox(1 1 5 5 11 11 18 18)}

{p 0 0}
Using the same data as above there were also map positions within the variable {hi:posn}. Thus the genomic
map could be displayed as a diagonal axis with the following command

{p 2 0}
{inp:.plotmatrix , mat(grid) split( 0(0.1)1 ) c(gray) nodiag save l distance(posn) dunit(Mb)}


{title:Author}

{p}
Adrian Mander, MRC Biostatistics Unit, Cambridge, UK.

Email {browse "mailto:adrian.mander@mrc-bsu.cam.ac.uk":adrian.mander@mrc-bsu.cam.ac.uk}

{title:See Also}
Related commands:

{p 2 2}
{help plotbeta} (if installed), 
{help cdfplot} (if installed), 
{help graphbinary} (if installed), 
{help palette_all} (if installed).


