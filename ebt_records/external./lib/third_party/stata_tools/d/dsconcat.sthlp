{smcl}
{.-}
help for {cmd:dsconcat} {right:(Roger Newson)}
{.-}


{title:Concatenate a list of Stata data files into the memory}

{p 8 21 2}
{cmd:dsconcat} {it:filename_list}  [ {cmd:,}
{cmdab:ap:pend}
{cmdab:sub:set}{cmd:(}[{varlist}] {ifin}{cmd:)} {break}
{cmdab:dsi:d}{cmd:(}{it:{help newvarname}}{cmd:)} {cmdab:dsn:ame}{cmd:(}{it:{help newvarname}}{cmd:)}
{cmdab:obs:seq}{cmd:(}{it:{help newvarname}}{cmd:)}
{cmdab:nol:abel} {cmdab:nonote:s} {cmdab:nold:sid}
{cmd:fast}
]

{pstd}
where {it:filename_list} is a list of filenames separated by spaces.
If any filename in the list is specified without an extension, then
{hi:.dta} is assumed.


{title:Description}

{pstd}
{cmd:dsconcat} is a multiple-file version of {helpb use} or {helpb append}.
It takes, as input, a list of filenames,
assumed to belong to Stata data files,
and creates a new dataset in memory,
containing a concatenation of the input data files,
which may either replace any existing dataset in memory
or be appended to any existing dataset in memory.
The new dataset contains all variables in all the input datasets (or a subset of variables
specified by the {cmd:subset()} option), and all observations in all the input datasets
(or a subset of observations specified by the {cmd:subset()} option),
ordered primarily by source dataset and secondarily by order of observations within each source dataset.
For any one variable in the output dataset in memory,
values of that variable are set to missing in any observation from an input dataset
not containing that variable.
Optionally, {cmd:dsconcat} creates new variables specifying,
for each observation, its input dataset of origin,
and/or the sequential order of the observation in its input dataset of origin.


{title:Options}

{p 4 8 2}
{cmd:append} specifies that the input datasets in files are to be appended to the existing dataset in memory,
if there is an existing dataset in memory.
If {cmd:append} is not specified, then any existing dataset in memory is overwritten.
Note that, if {cmd:append} is specified and there is no existing dataset in memory,
then the datasets in the input files are still concatenated into the memory,
as if {cmd:append} was not specified.

{p 4 8 2}
{cmd:subset(}[{varlist}] {ifin}{cmd:)}
specifies a subset of variables and/or observations
in each of the input file datasets, to be included in the concatenated output dataset in memory.
The value of the {cmd:subset()} option is a combination of a {varlist}
and/or an {helpb if} qualifier and/or an {helpb in} qualifier.
Each of these is optional. 
However, they must be valid for all input datasets,
according to the rules used by the {helpb use} command.
Note that, if the {cmd:append} and {cmd:subset()} options are both specified,
then the {cmd:subset()} option only applies to observations and variables from the input file datasets,
and does not remove any observations or variables from the existing dataset in memory.
To do this, the user must use {helpb keep} or {helpb drop} before using {helpb dsconcat}.

{p 4 8 2}
{cmd:dsid(}{it:{help newvarname}}{cmd:)} specifies a new integer variable to be created,
containing, for each observation in the new dataset, the sequential order, in the
{it:filename_list}, of the input dataset of origin of the observation.
This sequential order is equal to 0 for observations from the original dataset in memory,
which are included only if the {cmd:append} option is specified,
and is equal to a positive integer for observations from the input file datasets.
If {cmd:noldsid} is not specified, then
{cmd:dsconcat} creates a value label for the {it:{help newvarname}} with the same name,
assigning, to each positive integer {hi:i} from 1 to the number of input filenames
in the {it:filename_list}, a label equal to the filename of the {hi:i}th input dataset.
If a value label of that name already exists in one of the input datasets, and
{cmd:nolabel} is not specified, then {cmd:dsconcat} adds new labels,
but does not replace existing labels.

{p 4 8 2}
{cmd:dsname(}{it:{help newvarname}}{cmd:)} specifies a new string variable containing,
for each observation in the new dataset, the name of the input dataset of origin
of that observation, truncated if necessary to the {help limits:maximum string variable length}
in the version of Stata being used.
This new string variable is equal to an empty string ({cmd:""}) for observations from the existing dataset in memory,
which are included only if the {cmd:append} option is specified.

{p 4 8 2}
{cmd:obsseq(}{it:{help newvarname}}{cmd:)} specifies a new integer variable containing,
for each observation in the new dataset, the sequential order of that observation
in its input dataset of origin.
If the {cmd:subset()} option is specified, then
the sequential order of each observation from an input file dataset
is defined as its sequential order within the subset of observations in the original file dataset
specified by the {cmd:subset()} option,
excluding observations in the original file dataset excluded by the {cmd:subset()} option.

{p 4 8 2}
{cmd:nolabel} prevents {cmd:dsconcat}
from copying {help label:value label} definitions from the input file datasets.
Note that, if the {cmd:append} option is also specified,
then the {cmd:nolabel} option does not affect value labels in the original dataset in memory.

{p 4 8 2}
{cmd:nonotes} prevents {cmd:dsconcat}
from copying {help notes} from the input file datasets.
Note that, if the {cmd:append} option is also specified,
then the {cmd:nonotes} option does not affect notes in the original dataset in memory.

{p 4 8 2}
{cmd:noldsid} specifies that the new variable generated by the {cmd:dsid()} option will
have no {help label:value label}.
This implies that the values of the new variable specified by the
{cmd:dsid()} option will be listed as dataset sequence numbers, not as dataset names.
This option is useful if the input datasets are very numerous
and/or are repeated and/or are {help tempfile:temporary files} with uninformative names.
It is ignored if no {cmd:dsid()} option is specified.

{p 4 8 2}
{cmd:fast} is an option for programmers.
It specifies that any existing dataset in the memory will not necessarily be restored,
if {cmd:dsconcat} fails or the user presses {help break:Break}.
If {cmd:fast} is not specified, then the existing dataset is restored
if {cmd:dsconcat} fails or the user presses {help break:Break},
and this precaution requires a certain amount of time-consuming file processing.
Note that the {cmd:fast} option is ignored
if the {cmd:append} option and the  {cmd:subset()} option are both specified,
because then a certain amount of file processing is necessary,
even if {cmd:dsconcat} terminates without error or interruption.


{title:Remarks}

{pstd}
{cmd:dsconcat} is a multi-file version of {helpb use} or {helpb append}.
However, {cmd:dsconcat} is different from {helpb use} in that, unless the {cmd:append} option is specified,
{cmd:dsconcat} overwrites existing datasets in memory automatically (as {helpb collapse} and {helpb contract} do),
instead of requiring a {cmd:clear} option (as {helpb use} does).

{pstd}
{cmd:dsconcat} does not sort the data, or check uniqueness of observations in the concatenated dataset.
Therefore, users are advised to use the {helpb keyby} package, downloadable from {help ssc:SSC},
if they wish to enforce the relational database model,
and create datasets whose observations are sorted and identified by a list of variables known as a primary key.
In the relational database model, a dataset is viewed as a mathematical function,
whose domain is the set of available combinations of values of the primary key variables,
and whose range is the set of all possible combinations of values
for the variables not included in the primary key.
See {hi:Examples} below for an example using the {helpb keybygen} module of the {helpb keyby} package.


{title:Examples}

{p 8 12 2}{cmd:. dsconcat auto1 auto2 auto3 auto4, dsid(dsseq) obs(obsnum)}{p_end}
{p 8 12 2}{cmd:. sort dsseq obsnum}{p_end}

{p 8 12 2}{cmd:. dsconcat "Microsoft is inferior" Unix_is_superior IdontknowaboutMacOS}{p_end}

{p 8 12 2}{cmd:. dsconcat auto1 auto2 auto3 auto4, append dsid(dsseq) obs(obsseq)}{p_end}

{pstd}
The following example creates a dataset containing variables {hi:make}, {hi:foreign}, {hi:mpg}
and {hi:weight} in the first 53 observations of each of the datasets {hi:auto1}, {hi:auto2},
{hi:auto3} and {hi:auto4}, with the input dataset name stored in the new string variable {hi:dslab}:

{p 8 12 2}{cmd:. dsconcat auto1 auto2 auto3 auto4, subset(make foreign mpg weight in 1/53) dsn(dslab)}{p_end}

{pstd}
The following example uses the saved result {cmd:r(sortedby1)} (see {hi:Saved results} below),
saved by {cmd:dsconcat},
together with the {helpb keybygen} module of the {helpb keyby} package,
which can be downloaded from {help ssc:SSC}.
The concatenated dataset eventually created in memory has observations
sorted primarily in the order of the input dataset from which the observation was input
(specified by the new variable {cmd:dsseq}),
secondarily by the variable (or variables) defining the {help sort:sort order} of the first input dataset {cmd:auto1},
and thirdly by the order of the observation within its by-group in the input dataset
(specified by the new variable {cmd:obsseq}).
The {helpb keybygen} command ensures that the observations in the dataset are identified uniquely
by the values of the variables defining the sort order.

{p 8 12 2}{cmd:. dsconcat auto1 auto2 auto3 auto4, dsid(dsseq) noldsid}{p_end}
{p 8 12 2}{cmd:. keybygen dsseq `r(sortedby)', gene(obsseq)}{p_end}
{p 8 12 2}{cmd:. describe}{p_end}


{title:Saved results}

{pstd}
{cmd:dsconcat} saves the following in {cmd:r()}:

{synoptset 20 tabbed}{...}
{p2col 5 20 24 2: Scalars}{p_end}
{synopt:{cmd:r(nobs)}}total number of observations in concatenated dataset{p_end}
{synopt:{cmd:r(ndset)}}number of input dataset files{p_end}

{p2col 5 20 24 2: Macros}{p_end}
{synopt:{cmd:r(sortedby)}}list of variables specifying sort order of first input dataset{p_end}
{p2colreset}{...}

{pstd}
The result {cmd:r(sortedby)} contains the sort order of the dataset in memory,
if the {cmd:append} option is specified.
or the sort order of the dataset in the first input file,
if the {cmd:append} option is not specified.
Note that {cmd:dsconcat} does not perform any sorting of the data.
It is the user's responsibility to do this,
possibly using the result {cmd:r(sortedby)}.


{title:Author}

{pstd}
Roger Newson, Imperial College London, UK.
Email: {browse "mailto:r.newson@imperial.ac.uk":r.newson@imperial.ac.uk}


{title:Also see}

{psee}
{bind: }Manual: {hi:[D] append}, {hi:[D] drop}, {hi:[D] save}, {hi:[D] use}
{p_end}
{psee}
On-line: {helpb append}, {helpb keep}, {helpb drop}, {helpb save}, {helpb use}{break}
         {helpb keyby}, {helpb keybygen} if installed
{p_end}
