*! Date        : 24 Apr 2014
*! Version     : 1.20
*! Author      : Adrian Mander
*! Email       : adrian.mander@mrc-bsu.cam.ac.uk
*! Description : Plot matrices/Heat maps

/*
v 1.15 24Nov2008  Bug -- had to specify a cmiss(n) option on the boxes and moved it to version 10.1 (not sure if this is necessary)
v 1.16 20Oct2009  Bug - there is a problem with people using set dp comma added a check to stop the program
v 1.17  6May2011  Add - allow frequencies to be plotted on screen
v 1.18 21May2012  Add option to allow all colours to be specified using the allcolors() option.
v 1.19  8Mar2013  Add a formatcells() option to alter the printing style of the matrix values
v 1.20 24Apr2014  Bug? -- skipping allcolors if the graph is null is now removed
*/

prog def  plotmatrix
version 10.1
syntax , Mat(name) [,Split(numlist) Color(string) ALLCOLORS(string) NODIAG SAVE ADDBOX(numlist) Upper Lower Distance(varname) DUnit(string) MAXTicks(integer 8) FREQ FORMATCELLS(string) *]
local twoway_opt "`options'"
set more off
preserve

if "`color'"=="" local color "emidblue"

/****************************************************************************
 * Check for the dp formatting statement 
 ****************************************************************************/
if c(dp)=="comma" {
  di "{error} This command can not be used in conjunction with the comma formatted numbers "
  di "Please use set dp period"
  exit(198)
}

/****************************************************************************
 * A single variable contains the map positions in ORDER
 * i.e. the dataset has to have rows in the order of the SNPs of the matrix
 ****************************************************************************/
if "`dunit'"=="" local dunit "Mb"
if "`distance'"~="" {
  local ny = rowsof(`mat')
  local nx = colsof(`mat')
  local lenx = `nx'/8

  /* Set up the coords of the genomic region line */
  local angle = _pi/2.5
  local y1 = -0.5+`lenx'*sin(`angle')
  local x1 = 2+`lenx'*cos(`angle')
  local y2 = -`ny'+0.5+`lenx'*sin(`angle')
  local x2 = `nx'+1+`lenx'*cos(`angle')

  qui keep `distance'
  qui save dist,replace

  qui su `distance'
  local mapmin = `r(min)'
  local mapmax = `r(max)'
  local mapspan : di %6.1f `mapmax'-`mapmin'
  qui gen line = _n
  qui expand 3
  sort line
  qui replace `distance' = . if mod(_n,3)==0
  qui gen disty = `distance'
  qui gen distx = `distance'
  qui by line: replace distx = line+1 if _n==1
  qui by line: replace disty = -line+1 if _n==1
  qui by line: replace disty  = `y1' + (`distance'-`mapmin')/(`mapmax'-`mapmin')*(`y2'-`y1')  if _n==2
  qui by line: replace distx = `x1' + (`distance'-`mapmin')/(`mapmax'-`mapmin')*(`x2'-`x1') if _n==2
  qui keep disty distx

  /* create the map axis */
  local obs = _N+3
  qui set obs `obs'
  local lineno = `obs'-2
  qui replace disty  = `y1' in `lineno'
  qui replace distx = `x1' in `lineno++'
  qui replace disty  = `y2' in `lineno'
  qui replace distx = `x2' in `lineno'
  qui save dist,replace

  local y = -0.3*`ny'
  local x= 0.7*`nx'
  di "`mapspan'"
  local xtratxt `"|| (line disty distx, cmissing(n) clw(*.2) text(`y' `x' "`mapspan' `dunit'", orient(horizontal))) "'
}

drop _all

/* Find matrix dimensions and col/row names */
local ny = rowsof(`mat')
local nx = colsof(`mat')
local ynames: rowfullnames `mat'
local xnames: colfullnames `mat'
qui svmat `mat', names(matcol) 
if "`split'" ~= "" _mkdata, s(`split') nc(`nx')
else  _mkdata, nc(`nx')

di "SPLIT `r(split)'"

if "`nodiag'"~="" {
  qui replace col1=. if _stack==y
  qui replace cb=. if _stack==y
}

/***************************************************** 
 * put the numlist of values in split macro 
 *****************************************************/
if "`split'"=="" local split "`r(split)'"

/*Go through the colour cutoffs to create the legend list?*/
local count 1
foreach num of numlist `split' {
  if `count' > 1 local lablist `"`lablist' "`prev'-`num'" "'
  local `count++'
  local prev `num'
}
local lablist `"`lablist' "`prev'" "' 

/*************************************************************************************** 
 * The colour list...get the levels and produce the colours 
 *  ncolleg is the number of columns in legend
 *  size is the number of colors
 *  colorlist is the list of colours
 *
 *  cb is created in the _mkdata command and it is _n per color level according to split
 *  BUT clevels will only see the observed values and groupings not used will be missed
 *
 * work out the number of specified colours and change intensities around them.. 
 * OR if you specify a colorlist
 * then you make the intensity of 1 
 ***************************************************************************************/

qui levelsof cb, local(clevels)

local colorlist ""
local ccc 1
local size:list sizeof clevels
local no_spec_cols: list sizeof color
local new_size = int(`size'/`no_spec_cols'+0.999)
local spcol 1

/*****************************************************
 * Work out the color levels 
 * this is where the set dp is problematic
 *****************************************************/

foreach temp of local clevels {
  if `spcol'>`no_spec_cols' local spcol 1
  local cind`temp' `ccc'
  local cbak = `ccc++'-1
  local fact = int(255 -  200/`new_size'*`cbak')
  local fact2 = int( (255 -  200/`new_size'*`cbak')/2 )
  local fact3 = int( (255 -  200/`new_size'*`cbak')/3 )  
  if `spcol'==1 & `new_size'~=1 local intensity : di %4.2f (255/`new_size'*`cbak')/175+0.15
  if `spcol'==1 & `new_size'==1 local intensity : di %4.2f 1
  if `size'==1 local intensity "1"
  if "`color'"=="" local colorlist `" `colorlist' "`fact3' `fact2' `fact'" "'
  if "`color'"~="" {
    local scolor: word `spcol' of `color'
    local colorlist `" `colorlist' `scolor'*`intensity' "'
    local `spcol++'
  }
}

local ncolleg = int(sqrt(`cbak')+1)
local txt ""
local i 1
/*************** This next part is OK if allcolors is empty*****************/
  if "`allcolors'"=="" {
    foreach c of local clevels {
      qui count if  cb==`c'
      if r(N)>0 {
        if "`done`c''" == "" {
          local clab: word `c' of `lablist'
          local clegord "`clegord' `i'"
          local cleg `" `cleg' label(`i' "`clab'")"'
          local numb`c' `i'
        }
      local `i++'
      local done`c' "done"
      if "`allcolors'"~="" {
        local bc: word `cind`c'' of `allcolors'  /* ALL COLORS mention*/
      }
      else {
        local bc:word `cind`c'' of `colorlist'
      }
      local bc `""`bc'""'

      if "`upper'"~="" local xtraif " & y<=_stack"
      if "`lower'"~="" local xtraif " & y>=_stack"
 
      local txt`c' "area yy xx if cb==`c' & col1~=. `xtraif',cmiss(n) bfintensity(100) blw(vvvthin) bc(`bc') nodropb"

      if `"`txt'"'=="" local txt `"(`txt`c'')"'
      else {
        local txt `"`txt'||(`txt`c'')"'
      }
      local gsty "`gsty' p1area"
     }
   }
  }
  /***** this if if allcolors is specified then we make sure missing graphs still abide by the allcolors list */
  else { 
    su cb
    local maxc "`r(max)'"
     forv c=1/`maxc' {
      qui count if  cb==`c'
      if r(N)>0 {
        if "`done`c''" == "" {
          local clab: word `c' of `lablist'
          local clegord "`clegord' `i'"
          local cleg `" `cleg' label(`i' "`clab'")"'
          local numb`c' `i'
        }
      local `i++'
      local done`c' "done"
      local bc: word `c' of `allcolors'  /* ALL COLORS mention*/
      local bc `""`bc'""'

      if "`upper'"~="" local xtraif " & y<=_stack"
      if "`lower'"~="" local xtraif " & y>=_stack"
 
      local txt`c' "area yy xx if cb==`c' & col1~=. `xtraif',cmiss(n) bfintensity(100) blw(vvvthin) bc(`bc') nodropb"

      if `"`txt'"'=="" local txt `"(`txt`c'')"'
      else {
        local txt `"`txt'||(`txt`c'')"'
      }
      local gsty "`gsty' p1area"
     }
   }

  }

/* Reconstruct the order of the legend */
foreach cord of local clevels {
  local corder "`corder'`numb`cord'' "
}

/* Create the labelling on the axes */
local nulab `maxticks'
local i 1
local nx:list sizeof xnames
local modx = int(`nx'/`nulab'+1)
foreach var of local xnames {
  if mod(`i',`modx')==1 local xlab `"`xlab'`i' "`var'" "'
  if `nx'<=`nulab' local xlab `"`xlab'`i' "`var'" "'
  local `i++'
}

local i 0
local ny:list sizeof ynames
local mody = int(`ny'/`nulab'+1)
foreach var of local ynames {
  if mod(`i',`mody')==0 local ylab `"`ylab'`i' "`var'" "'
  if `ny'<=`nulab' local ylab `"`ylab'`i' "`var'" "'
  local i=`i'-1
}

/**************************************************************** 
 * To add boxes around certain regions 
 * EACH option requires top left and bottom right coordinates
 ****************************************************************/
if "`addbox'"~="" {
  qui gen boxy=.
  qui g boxx=.
  local obs = 1
  tokenize `addbox'
  while "`1'"~="" {
    qui replace boxy = -1*(`1'-1.5) in `obs'
    qui replace boxx = `2'-0.5 in `obs++'
    qui replace boxy = -1*(`1'-1.5) in `obs'
    qui replace boxx = `4'+0.5 in `obs++'
    qui replace boxy = -1*(`3'-0.5) in `obs'
    qui replace boxx = `4'+0.5 in `obs++'
    qui replace boxy = -1*(`3'-0.5) in `obs'
    qui replace boxx = `2'-0.5 in `obs++'
    qui replace boxy=. in `obs'
    qui replace boxx=. in `obs++'
    mac shift 4
  }
  local txt "`txt'|| (area boxy boxx, blw(medthick) bc(black) bfc(none) nodropb cmiss(n))"
}

/********************************************************
 * The Freq option
 *  Want to display the values of the cells as the text 
 *  within each box
 *  ALSO the user can alter these formats
 ********************************************************/
if "`freq'"~="" {
  gen newy = -1*y+1
  if "`formatcells'"~="" format col1 `formatcells'
  local txt "`txt'||(scatter newy _stack, mlab(col1) mlabcolor(black) mlabposition(0) ms(i))"
} 
/* Saving the dataset that makes plotmatrix */
if "`save'"~="" qui save plotmatrix,replace
if "`distance'"~=""  {
  append using dist
  local txt `"`txt' `xtratxt'"'
}
/* The graphing command */
qui twoway `txt', legend(on `cleg' order(`corder') cols(`ncolleg')) xlabel(`xlab') ylabel(`ylab', nogrid) xtitle("") ytitle("") graphregion( c(white) lp(blank)) `twoway_opt'

restore
end

/************************************************ 
 *
 * Make the dataset that will create the boxes 
 *
 *************************************************/

prog def _mkdata, rclass
syntax [varlist] [, Split(numlist) NC(integer 0)]

/* 
Create percentiles if split is not specified
nc is the number of columns.. if there is only one column just do a rename otherwise stack the columns
*/

if `nc'==1 {
  rename `varlist' col1
  qui g _stack = 1
}
else qui stack `varlist', into(col1) clear

/*
 Split option here allows for the calculation of the legend, percentiles are 
 defaults
*/

qui su col1
local min: di %5.3f (`r(min)'-0.001)
local max: di %5.3f (`r(max)'+0.001)
if "`split'"=="" {
  di as text "Percentiles are used to create legend"
  qui _pctile col1, p( 1 5(10)95 99)
  local i 1
  local split "`min' "
  while r(r`i')~=. {
    local entry:di %5.3f `r(r`i++')'
    local split "`split'`entry' "
  }
  local split "`split' `max'"
}
return local split = "`split'"  

local diff 0.5
qui bysort _stack:g y=_n
qui expand 5
qui bysort _stack y: g yy=-1*cond(_n==1 | _n==2, y+`diff', cond( _n==3 | _n==4, y-`diff',.))+1
qui bysort _stack y: g xx=cond(_n==1 | _n==4, _stack+`diff', cond(_n==3 | _n==2, _stack-`diff',.))

qui g cb =.
qui g colorleg =""
local var "col1"
local pcent 0

foreach num of numlist `split' {
  if `pcent'~=0 {
    qui replace cb = cond( `var'<`num' & `var'>=`prev', `pcent',cb) 
    qui replace colorleg =  cond( `var'<`num' & `var'>=`prev', "`prev'-`num'",colorleg)
  }
  local prev = `num'
  local `pcent++'
}
qui replace cb= cond( `var'==`prev', `pcent',cb)  /* This is the extra very last value*/
qui replace colorleg =  cond( `var'==`prev' , "`prev'",colorleg)

end


