#delim ;
prog def dsconcat, rclass;
version 10.0;
/*
 Concatenate a sequence of data sets (or subsets of data sets) into the memory,
 optionally creating additional variables identifying, for each obs,
 the data set from which that obs originated
 and/or the sequential order of that obs within its original data set.
*! Author: Roger Newson
*! Date: 24 July 2009
*/

*
 Extract file list and leave command line ready to be syntaxed
*;
local ndset=0;
gettoken dscur 0 : 0,parse(", ");
while `"`dscur'"'!="" & `"`dscur'"'!="," {;
  local ndset=`ndset'+1;
  local ds`ndset' `"`dscur'"';
  gettoken dscur 0 : 0,parse(" ,");
};
local 0 `", `0'"';
if `ndset'<=0 {;
  disp as error "No input data sets have been specified";
  error 498;
};

* Crack syntax of rest of input line *;
syntax [ , APpend DSId(string) DSName(string) OBSseq(string) noLabel noNOTEs noLDsid SUBset(string asis) fast ];
/*
 -append- indicates that the input file will be appended to the existing dataset in memory,
  instead of overwriting the existing dataset.
 -dsid()- is name of new integer variable containing data set ID,
  with value label of the same name if possible, specifying data set names.
 -dsname()- is name of new string variable containing data set names.
 -obsseq()- is name of new integer variable
  containing sequential order of obs within original data set.
 -nolabel- specifies that labels are not to be copied
  from the input file datasets.
 -nonotes- specifies that notes are not to be copied
  from the input file datasets.  
 -noldsid- specifies that the -dsid- variable will not have value labels
  (this is useful if the input datasets are numerous and/or repeated
  and/or have incomprehensible -tempfile- names).
 -subset()- specifies a subset string
  (ie a combination of -varlist-, -if- clause and -in- clause,
  allowing the user to select a subset of variables and/or observations
  from each of the input data sets to be concatenayed).
 -fast- is an option for programmers,
  specifying that the existing dataset is not to be preserved,
  or restored if -dsconcat- fails or the user presses -break-.
*/

if "`fast'"=="" | ("`append'"!="" & `"`subset'"'!="") {;preserve;};

*
 Create intermediate input dataset filenames,
 creating temporary datasets for concatenation if -subset()- is specified
*;
if `"`subset'"'=="" {;
  * Intermediate dataset filenames set to input dataset filenames *;
  forv i1=1(1)`ndset' {;
    local ids`i1' `"`ds`i1''"';
  };
};
else {;
  forv i1=1(1)`ndset' {;
    tempfile ids`i1';
    cap use `subset' using `"`ds`i1''"', clear `label';
    if _rc!=0 {;
      disp as error "Error reading input data set: " as result `"`ds`i1''"'
       _n as error "Subset string: " as result `"`subset'"';
      error 498;
    };
    qui save `"`ids`i1''"';
  };
  if "`append'"!="" {;
    restore, preserve;
  };
};

*
 Define temporary variables
 (to be created and renamed to corresponding options
 if and only if none of the input data sets
 contain a variable of the same name)
*;
tempvar dsidt dsnamet obsseqt;

*
 Concatenate input data sets in list
*;
*
 Input first data set if -append- is not specified
 and initialize newvar options if specified
*;
if "`append'"=="" {;
  qui use `"`ids1'"',clear `label';
  qui notes drop _dta;
  qui notes drop *;
  local firstapp=2;
};
else {;
  local firstapp=1;
};
local sortedby: sortedby;
* Create newvar options if requested *;
if `"`dsid'"'!="" {;
  qui {;
    gene long `dsidt'=`firstapp'-1;
    lab var `dsidt' "Input dataset";
  };
};
if `"`ds1'"'!="" {;
  qui {;
    gene str1 `dsnamet'="";
    if "`append'"=="" {;
      replace `dsnamet'=`"`ds1'"';
    };
    lab var `dsnamet' "Input dataset file name";
  };
};
if `"`obsseq'"'!="" {;
  qui {;
    gene long `obsseqt'=_n;
    lab var `obsseqt' "Observation sequence in input data set";
  };
};
local nobs=_N;
* Append other data sets *;
forv i1=`firstapp'(1)`ndset' {;
  qui append using `"`ids`i1''"',`label' `notes';
  local nobsp=`nobs'+1;
  if `"`dsid'"'!="" {;
    qui replace `dsidt'=`i1' in `nobsp'/l;
  };
  if `"`ds`i1''"'!="" {;
    qui replace `dsnamet'=`"`ds`i1''"' in `nobsp'/l;
  };
  if `"`obsseq'"'!="" {;
    qui replace `obsseqt'=_n-`nobs' in `nobsp'/l;
  };
  local nobs=_N;
};

*
 Compress temporary variables
 and rename them to the corresponding user-supplied options if possible
*;
foreach V in dsid dsname obsseq {;
  if `"``V''"'!="" {;
    qui compress ``V't';
    rename ``V't' ``V'';
  };
};

* Create value label for -dsid- if required *;
if `"`dsid'"'!="" & "`ldsid'"!="noldsid" {;
  forv i1=1(1)`ndset' {;
    cap lab def `dsid' `i1' `"`ds`i1''"', add;
  };
  lab val `dsid' `dsid';
};

if "`fast'"=="" | ("`append'"!="" & `"`subset'"'!="") {;restore,not;};

return scalar ndset=`ndset';
return scalar nobs=`nobs';
return local sortedby "`sortedby'";

end;
