options noxwait xsync mlogic mprint;
options obs =  max;

data infile_data;          
	Infile "./input/test_data.txt"  MISSOVER;
	Input
		COLUMN1				$1-2
		COLUMN2 			$4-5
    ;
run;

proc contents data = infile_data short;
run;

 proc export data = infile_data  outfile= "./out_data.csv"
    dbms=csv  replace;