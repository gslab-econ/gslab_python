#delim ;
prog def eclplot, rclass;
version 10.0;
/*
  Create plot of estimates and confidence limits
  (vertical or horizontal)
  against a numeric parameter ID variable..
*! Author: Roger Newson
*! Date: 11 June 2012
*/

*
 Define maximum number of estimate and confidence limit plots
 and lists of options for these estimates and confidence limits plots
*;
local msupby=15;
local estoptsi "";
local cioptsi "";
forv i1=1(1)`msupby' {;
  local estoptsi `"`estoptsi' ESTOPTS`i1'(string asis)"';
  local cioptsi `"`cioptsi' CIOPTS`i1'(string asis)"';
};
* Parse syntax *;
syntax varlist(numeric min=4 max=4) [if] [in] [, HORizontal
  EPLOTtype(string) RPLOTtype(string) noCIForeground
  ESTOPTS(string asis) CIOPTS(string asis)
  ADDPLOT(string asis) BADDPLOT(string asis) PLOT(string asis) noGRaph
  BY(string asis)
  supby(string asis)
  `estoptsi' `cioptsi'
  * ];
/*
 -varlist- is a list of 4 variables
  (estimate, lower confidence limit, upper confidence limit,
  and numeric parameter ID variable to plot them against).
 -horizontal- specifies that a horizontal CI plot will be drawn
  (instead of the default vertical CI plot).
 -eplottype- specifies the plot typr used to draw the estimates
   (defaulting to -scatter- to give unconnected symbols
   and no areas, bars or spikes).
 -rplottype- specifies the range plot type used to draw the confidence limits
  (defaulting to -rcap- to give capped CI plots).
 -nociforeground- specifies whether or not the confidence intervals
   are in the foreground (with the estimates in the background).
 -estopts- specifies the estimates options
  (to be passed to -graph twoway scatter- to control the estimate points)
 -ciopts- specifies the confidence interval options
  (to be passed to -graph twoway `rplottype' - to control the confidence limits).
 -addplot- specifies other plots to be added to the generated graph.
 -baddplot- specifies other plots to be added to the generated graph
  in the background.
 -plot- is an alternative way of specifying -addplot-.
 -nograph- specifies that the graph should not be drawn
  (useful for building a -twoway- command from -r()- elements).
 -by()- is the by-option for the graph
  (which is supplied with a default legend() suboption
  if this suboption is absent).
 -supby()- specifies that superimposed multiple CI plots
  are to be produced,
  one for each value of a single variable.
 -estoptsi- specifies estimates options
  for each superimposed multiple CI plot
  (to be added to -estopts()-).
 -cioptsi- specifies confidence interval options
  for each superimposed multiple CI plot
  (to be added to -ciopts()-)
*/

*
 Set -addplot()- option if given as -plot()- option
*;
if `"`addplot'"'=="" {;
  local addplot `"`plot'"';
};
else if `"`plot'"'!="" {;
  disp as error "Options addplot() and plot() are alternatives and cannot both be specified";
  error 498;
};

*
 Store extra -twoway- options in macro `twoptions-
*;
local twoptions `"`options'"';

*
 Check estimate and range plot types
 and -ciforeground- option
 and set to default if empty
 and unabbreviate if necessary
*;
if `"`eplottype'"'=="" {;local eplottype "scatter";};
if `"`rplottype'"'=="" {;local rplottype "rcap";};
if length(`"`eplottype'"')<2 {;
  disp as error "eplottype() must be specified by at least 2 letters";
  error 498;
};
local found=0;
foreach PT in scatter connected line area bar spike dropline {;
  if !`found' & strpos("`PT'",`"`eplottype'"')==1 {;
    local eplottype "`PT'";
    local found=1;
  };
};
if length(`"`rplottype'"')<2 {;
  disp as error "rplottype() must be specified by at least 2 letters";
  error 498;
};
local found=0;
foreach PT in  rarea rbar rspike rcap rcapsym rscatter rline rconnected {;
  if !`found' &  strpos("`PT'",`"`rplottype'"')==1 {;
    local rplottype "`PT'";
    local found=1;
  };
};
if "`ciforeground'"=="" {;
  * Rank for -eplottype()- *;
  if inlist("`eplottype'","scatter","connected","line") {;local eplotrank=1;};
  else if inlist("`eplottype'","dropline","spike") {;local eplotrank=2;};
  else if inlist("`eplottype'","bar") {;local eplotrank=3;};
  else if inlist("`eplottype","area") {;local eplotrank=4;};
  else {;local eplotrank=5;};
  * Rank for -rplottype()- *;
  if inlist("`rplottype'","rscatter","rconnected","rline") {;local rplotrank=1;};
  else if inlist("`rplottype'","rcapsym","rcap","rspike") {;local rplotrank=2;};
  else if inlist("`rplottype'","rbar") {;local rplotrank=3;};
  else if inlist("`rplottype","rarea") {;local rplotrank=4;};
  else {;local rplotrank=5;};
  * Compare ranks *;
  if `rplotrank'<=`eplotrank' {;
    local ciforeground "ciforeground";
  };
  else {;
    local ciforeground "nociforeground";
  };
};

*
 Variables to plot and their labels
*;
local estimate:word 1 of `varlist';
local clmin:word 2 of `varlist';
local clmax:word 3 of `varlist';
local parmid:word 4 of `varlist';
local estlab:var lab `estimate';
if `"`estlab'"'=="" {;local estlab "`estimate'";};
local parmlab:var lab `parmid';
if `"`parmlab'"'=="" {;local parmlab "`parmid'";};

*
 -if- and -in- qualifiers
*;
local ifin "";
if `"`if'"'!="" & `"`in'"'!="" {;
  local ifin `"`if' `in'"';
};
else if `"`if'"'!="" {;
  local ifin `"`if'"';
};
else if `"`in'"'!="" {;
  local ifin `"`in'"';
};

*
 Call _eclplot to generate subcommand list in macro -subcmd-
 and generate default legend in macro -deflegend-
*;
if `"`supby'"'=="" {;
  *
   Single estimate amd confidence limit plot
  *;
  _eclplot `estimate' `clmin' `clmax' `parmid', `horizontal' eplottype(`eplottype') rplottype(`rplottype') `ciforeground'
    estopts(pstyle(p1) `estopts') ciopts(pstyle(p2) `ciopts');
  local subcmd `"`r(subcmd)'"';
  local deflegend "legend(off)";
};
else {;
  *
   Superimposed multiple estimate and confidence limit plots
  *;
  *
   Parse -supby()- suboptions
  *;
  local 0 `"`supby'"';
  syntax varname [ , Missing Truncate(passthru) SPAceby(real 0) OFFset(real 0) ];
  local supbyvar "`varlist'";
  *
   Create superimposed plot sequence variable
  *;
  tempvar supseqvar;
  tempname supseqlab;
  qui egen `supseqvar'=group(`supbyvar') `ifin', `missing' label lname(`supseqlab') `truncate';
  qui summ `supseqvar';
  local nsupby=r(max);
  if missing(`nsupby') {;
    disp as error "No valid values for supby() variable: `supbyvar'";
    error 2000;
  };
  else if `nsupby'>`msupby' {;
    disp as error "Number of superimposed plots (`nsupby') greater than maximum of `msupby'";
    error 498;
  };
  *
   Create legend order and default legend
  *;
  local legord "";
  forv i1=1(1)`nsupby' {;
    * Key sequence number for estimates plot *;
    local keyseq=2*`i1';
    if "`ciforeground'"=="ciforeground" {;
      local keyseq=`keyseq'-1;
    };
    local keytext: label (`supseqvar') `i1';
    * Add -keytext- to legend order if quotable in double quotes *;
    cap local junk1=`"`macval(keytext)'"';
    if _rc==0 {;
      local legord `"`legord' `keyseq' `"`macval(keytext)'"'"';
    };
    else {;
      local legord `"`legord' `keyseq' `""'"';
    };
  };
  local deflegend `"legend(order(`legord'))"';
  *
   Create parameter position variable
  *;
  if `offset'==0 & `spaceby'==0 {;
    local parmpos "`parmid'";
  };
  else {;
    tempvar parmpos;
    qui clonevar `parmpos'=`parmid' `ifin';
    qui replace `parmpos' = `parmpos' + `offset' + `spaceby'*(`supseqvar'-1) `ifin';
  };
  *
   Create subcommand list
  *;
  _parse comma estop0 estwt0 : estopts;
  _parse comma ciop0 ciwt0 : ciopts;
  forv i1=1(1)`nsupby' {;
    *
     Estimate and confidence limit style sequences
     (THIS SHOULD WORK IF -msupby- IS A POSITIVE ODD INTEGER)
    *;
    local cistyle=2*`i1';
    local eststyle=`cistyle'-1;
    local cistyle=mod(`cistyle'-1,`msupby')+1;
    local eststyle=mod(`eststyle'-1,`msupby')+1;
    * Create estimate and CI options and weights *;
    _parse comma estop estwt: estopts`i1';
    _parse comma ciop ciwt: ciopts`i1';
    if `"`estwt'"'=="" {;local estwt `"`estwt0'"';};
    if `"`ciwt'"'=="" {;local ciwt `"`ciwt0'"';};
    local estop `"pstyle(p`eststyle') `estop0' `estop'"';
    local ciop `"pstyle(p`cistyle') `ciop0' `ciop'"';
    * Call -_eclplot- and add subcommands *;
    _eclplot `estimate' `clmin' `clmax' `parmpos',
      `horizontal' eplottype(`eplottype') rplottype(`rplottype') `ciforeground'
      estopts(`estop' `estwt') ciopts(`ciop' `ciwt') supseqvar(`supseqvar') supseqnum(`i1');
    if `i1'==1 {;
      local subcmd `"`r(subcmd)'"';
    };
    else {;
      local subcmd `"`subcmd' || `r(subcmd)'"';
    };
  };
};

*
 Add -addplot()- or -plot()- options to subcommand list if necessary
*;
if `"`addplot'"'!="" {;
  local subcmd `"`subcmd' || `addplot'"';
};
else if `"`plot'"'!="" {;
  local subcmd `"`subcmd' || `plot'"';
};

*
 Add -baddplot()- option to subcommand list if necessary
*;
if `"`baddplot'"'!="" {;
  local subcmd `"`baddplot' || `subcmd'"';
};

*
 Modify by-option if present
*;
if `"`by'"'!="" {;
  cap noi _parseby `by';
  if _rc!=0 {;
    disp as error `"Invalid by-option: by( `by' )"';
    error 498;
  };
  local byvarlist `"`r(byvarlist)'"';
  local bylegend `"`r(bylegend)'"';
  local bysubopts `"`r(bysubopts)'"';
  if `"`bylegend'"'=="" {;
    if `"`supby'"'=="" {;
      local bylegend "legend(off)";
    };
    else {;
      local bylegend "legend(on)";
    };
  };
  local by `"by(`byvarlist', `bylegend' `bysubopts')"';
};

*
 Generate -twoway- options list
*;
if "`horizontal'"=="horizontal" {;
  local twowayopts `"yscale(reverse) ylabel(, valuelabel angle(0)) ytitle(`"`parmlab'"') xtitle(`"`estlab'"') `by' `deflegend' `twoptions'"';
};
else {;
  local twowayopts `" xlabel(, valuelabel) ytitle(`"`estlab'"') xtitle(`"`parmlab'"') `by' `deflegend' `twoptions'"';
};

* -twoway- command *;
local cmd `"twoway `subcmd' || `ifin' , `twowayopts'"';

*
 Generate plots
*;
if "`graph'"!="nograph" {;
  `cmd';
};

*
 Save command, subcommands and twoway options in -r()-
*;
return local cmd `"`cmd'"';
return local twowayopts `"`twowayopts'"';
return local ifin `"`ifin'"';
return local allplots `"`subcmd'"';
return local plot `"`plot'"';
return local baddplot `"`baddplot'"';
return local addplot `"`addplot'"';

end;

program _eclplot, rclass;
version 10.0;
/*
  Input features of estimates and confidence limits plots
  and output subcommand pair defining estimate and confidence limits plot
  in -r(subcmd)-
*/

syntax varlist(numeric min=4 max=4) [, HORizontal
  EPLOTtype(string) RPLOTtype(string) noCIForeground
  ESTOPTS(string asis) CIOPTS(string asis)
  SUPSEQVAR(varname numeric) SUPSEQNUM(integer 1)
  ];
/*
 -varlist- is a list of 4 variables
  (estimate, lower confidence limit, upper confidence limit,
  and numeric parameter ID variable to plot them against).
 -horizontal- specifies that a horizontal CI plot will be drawn
  (instead of the default vertical CI plot).
 -eplottype- specifies the plot typr used to draw the estimates
   (defaulting to -scatter- to give unconnected symbols
   and no areas, bars or spikes).
 -rplottype- specifies the range plot type used to draw the confidence limits
  (defaulting to -rcap- to give capped CI plots).
 -nociforeground- specifies whether or not the confidence intervals
   are in the foreground (with the estimates in the background).
 -estopts- specifies the estimates options
  (to be passed to -graph twoway scatter- to control the estimate points)
 -ciopts- specifies the confidence interval options
  (to be passed to -graph twoway `rplottype' - to control the confidence limits).
 -supseqvar- specifies a variable containing sequence order
  for superimposed multiple plots.
 -supseqnum- specifies a sequence order for the current superimposed plot.
*/

* Variables to plot *;
local estimate:word 1 of `varlist';
local clmin:word 2 of `varlist';
local clmax:word 3 of `varlist';
local parmid:word 4 of `varlist';

*
 Specify current superimposed plot
*;

if "`supseqvar'"=="" {;
  local andsup "";
};
else {;
  local andsup " & `supseqvar'==`supseqnum'";
};

*
 Generate estimate plot subcommand
*;
if inlist(`"`eplottype'"',"area","bar","spike","dropline") {;
  * Orientation decided by "horizontal" and "vertical" options *;
  if "`horizontal'"=="horizontal" {;
    local eplotcmd `"`eplottype' `estimate' `parmid' if  !missing(`estimate') & !missing(`parmid')`andsup' , horizontal `estopts'"';
  };
  else {;
    local eplotcmd `"`eplottype' `estimate' `parmid' if  !missing(`estimate') & !missing(`parmid')`andsup' , vertical `estopts'"';
  };
};
else if inlist(`"`eplottype'"',"scatter","connected","line") {;
  * Orientation decided by variable order *;
  if "`horizontal'"=="horizontal" {;
    local eplotcmd `"`eplottype' `parmid' `estimate'  if  !missing(`estimate') & !missing(`parmid')`andsup' , `estopts'"';
  };
  else {;
    local eplotcmd `"`eplottype' `estimate' `parmid'  if  !missing(`estimate') & !missing(`parmid')`andsup' , `estopts'"';
  };
};
else {;
  * Impossible to decide how to decide orientation *;
  disp as error `"Unknown estimate plot type - `eplottype'"';
  error 498;
};

*
 Generate confidence limit plot subcommand
*;
if "`horizontal'"=="horizontal" {;
  local rplotcmd `"`rplottype' `clmax' `clmin' `parmid' if  !missing(`clmin') & !missing(`clmax') & !missing(`parmid')`andsup' , horizontal `ciopts'"';
};
else {;
  local rplotcmd `"`rplottype' `clmax' `clmin' `parmid' if  !missing(`clmin') & !missing(`clmax') & !missing(`parmid')`andsup' , vertical `ciopts'"';
};

*
 Combine 2 subcommands to form subcommand list
*;
if "`ciforeground'"=="nociforeground" {;
  * Confidence limits in background *;
  local subcmd `"`rplotcmd' || `eplotcmd'"';
};
else {;
  * Confidence limits in foreground *;
  local subcmd `"`eplotcmd' || `rplotcmd'"';;
};

*
 Return subcommand pair
*;
return local subcmd `"`subcmd'"';

end;

prog def _parseby, rclass;
version 10.0;
/*
  Parse a by-option
  returning its varlist in r(byarlist), its legend() suboption in r(bylegend),
  and its other suboption in r(bysubopts).
*/

syntax varlist [, LEGend(passthru) * ];
/*
 -varlist- is the list of by-variables.
 -legend()- is the legend suboption of the by-option.
*/

return local byvarlist `"`varlist'"';
return local bylegend `"`legend'"';
return local bysubopts `"`options'"';

end;
