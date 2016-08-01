*! version 1.0.6 02aug2011
* fixed  st_addvar():  3300 error for dbase str variables
*	over 244 in length
* -----version 1.0.5 13jul2011------
* Removed memory error for Stata 12
* Fix bug with dbase files generating error
*	bufget():  3300  argument out of range
* ------version 1.0.4 13may2008-----
* Stata 10.1 -_ID variable will automatically be
* created in the dbf file.
* Added support for line and point shp files
program define shp2dta
	version 9

	syntax using/ , DATAbase(string) COORdinates(string) ///
			[replace GENCentroids(name) genid(name)]

					// Check for shape file
	if (strpos(`"`using'"', ".")==0) {
			local using `"`using'.shp"'
	}
	local shp_file `"`using'"'
					// Create macros for the .dbf file
	local dbf_file : subinstr local shp_file `".shp"' `".dbf"'

					// Confirm shp and dbf file exist
	confirm file `"`shp_file'"'
	confirm file `"`dbf_file'"'

					// Preserve and clear data in memory
	preserve
	drop _all

					// Read shp file
	mata: read_shp(`"`shp_file'"')

					// Compress, sort, and save coordinates
	qui {
		compress
		tempname TEMP
		generate long `TEMP' = _n
		sort _ID `TEMP'
		drop `TEMP'
		local cfilename : subinstr local coordinates `".dta"' `""'
		save `"`cfilename'"', `replace'
	}

					// Clear coordinates dataset
	drop _all

					// Read dbf file
	mata: read_dbf(`"`dbf_file'"')

					// Compress and save database dataset
	qui {
		if `"`genid'"' != "" {
			generate long `genid' = _n
			sort `genid'
		}
		else {
			if (_caller() > 10.0) {
				generate long _ID = _n
				sort _ID
			}
		}
		compress
		local dfilename : subinstr local database `".dta"' `""'
		save `"`dfilename'"', `replace'
	}

					// Create centroids x and y variables
	if "`gencentroids'"!="" {
		if `"`genid'"' == "" {
			dis as error ///
				"you must also specify the genid(name) option"
			exit(198)
		}
		quietly {
use `"`cfilename'"', clear
bys _ID: gen float TEMPa=(_X*_Y[_n+1])-(_X[_n+1]*_Y) if _n>1 & _n<_N
bys _ID: gen float _AREA=sum(TEMPa)
bys _ID: replace _AREA=_AREA[_N]/2
bys _ID: gen float TEMPx=(_X+_X[_n+1])*(_X*_Y[_n+1]-_X[_n+1]*_Y) if _n>1 & _n<_N
bys _ID: gen float _CX=sum(TEMPx)
bys _ID: replace _CX=_CX[_N]/(6*_AREA)
bys _ID: gen float TEMPy=(_Y+_Y[_n+1])*(_X*_Y[_n+1]-_X[_n+1]*_Y) if _n>1 & _n<_N
bys _ID: gen float _CY=sum(TEMPy)
bys _ID: replace _CY=_CY[_N]/(6*_AREA)
collapse _CX _CY, by(_ID)
rename _ID `genid'
rename _CX x_`gencentroids'
rename _CY y_`gencentroids'
lab var `genid' "Area ID"
lab var x_`gencentroids' "x-coordinate of area centroid"
lab var y_`gencentroids' "y-coordinate of area centroid"
sort `genid'
merge `genid' using `"`dfilename'"'
drop _merge
compress
save `"`dfilename'"', replace
		}
	}
end

/* -------------------------------------------------------------------- */
local BUFSIZE	200
version 9.0
mata:

void read_shp(string scalar shp_file)
{
	real scalar		fh_in
	transmorphic colvector	C
	real rowvector		parts

	real scalar field_code, length, ver, type, x, y, num_bytes, start_byte
	real scalar record_num, content_length, next_record
	real scalar num_parts, num_points, num_of_obs, i, j, cols, points
	real scalar pstart, pend, sobs, obs, n
	real scalar bufsize, numofbufs, numPointsInPart

	// Open shape file .shp, open buffer, and set byte order
	fh_in = fopen(shp_file, "r")
	C = bufio()
	bufbyteorder(C, 1)

	// Get field code and file length from shape file
	field_code = fbufget(C, fh_in, "%4b")
	fseek(fh_in, 24, -1)
	length = fbufget(C, fh_in, "%4b")

	// Change byte order and get version and shape type
	bufbyteorder(C, 2)
	ver = fbufget(C, fh_in, "%4b")
	type = fbufget(C, fh_in, "%4b")

	// Check shape file header for field code and version
	if (field_code!=9994 | ver!=1000) {
		errprintf("%s: invalid shape file\n", shp_file)
		exit(610)
	}

	// Check for shape type
	if (type != 1 & type != 3 & type != 5) {
errprintf("%s: point, polyine, or polygon shapefile required\n", shp_file)
		exit(610)
	}

	// Go to byte 100
	fseek(fh_in, 100, -1)

	// Calculate the number of bytes
	num_bytes = (length * 16)/8

	if (st_numscalar("c(stata_version)") < 12 ) {
		if (num_bytes >= st_numscalar("c(memory)")) {
			errprintf("insufficient memory\n")
			errprintf("{p 4 4 2}\n")
			errprintf("To process this data, Stata will need at \n")
			errprintf("least %g megs of memory.\n",
				num_bytes/(1024^2))
			errprintf("{p_end}\n")
			exit(901)
		}
	}

	// Create variables
	(void) st_addvar(("long","double","double"), ("_ID", "_X", "_Y"))

	// Loop over bytes to get each record and create observation counter
	start_byte = 100
	obs = 1

	while (start_byte < num_bytes) {

		// Change byte order and get record number and length
		bufbyteorder(C, 1)
		fseek(fh_in, start_byte, -1)

		record_num = fbufget(C, fh_in, "%4b")
		content_length = fbufget(C, fh_in, "%4b")

		// Find start of next record
		next_record = ((content_length+4)*16) / 8

		// Change byte order and get shapetype
		bufbyteorder(C, 2)
		type = fbufget(C, fh_in, "%4b")

		if (type != 1 & type != 3 & type != 5) {
errprintf("%s: point, polyline, or polygon shapefile required\n", shp_file)
			exit(610)
		}
		if (type == 1) {
			// Get the id X Y values
			st_addobs(1)
			st_store(obs, (1,2,3),
				(obs,fbufget(C, fh_in, "%8z", 1, 2)))
			obs = obs + 1
		}
		else {
			// Get the number of parts and points for the record
			fseek(fh_in, 32, 0)
			num_parts  = fbufget(C, fh_in, "%4b")
			num_points = fbufget(C, fh_in, "%4b")

			// Create rowvector of parts array
			parts = fbufget(C, fh_in, "%4b", num_parts)

			// Get the number of obs and add to dataset
			num_of_obs = num_points + num_parts
			st_addobs(num_of_obs)

			// Loop of parts row vector
			cols = cols(parts)
			points = num_points

			for (i=1; i<=cols; i++) {
				if (i==cols) {
					numPointsInPart = points
				}
				else {
					pstart          = parts[i]
					pend            = parts[i + 1]
					numPointsInPart = pend - pstart
				}

				// Store the first obs of part as missing
				st_store(obs, (1,2,3), (record_num, ., .))
				sobs = obs++

				// Store X and Y obs in `BUFSIZE' block chunks
				bufsize = `BUFSIZE'
				numofbufs = floor(numPointsInPart/bufsize)

				for (j=1; j<=numofbufs; j++) {
					st_store((obs,obs+bufsize-1), (2,3),
						fbufget(C, fh_in, "%8z",
							bufsize, 2))
					obs = obs + bufsize
				}

				// Store the remander of observations
				bufsize = numPointsInPart - numofbufs*bufsize
				if (bufsize) {
					st_store((obs,obs+bufsize-1), (2,3),
						fbufget(C, fh_in, "%8z",
							bufsize, 2))
					obs = obs + bufsize
				}
				n = obs - sobs

				// Fill in record num for part
				st_store((sobs,obs-1), 1, J(n,1,record_num))
				points = points - (pend - pstart)
			}
		}
		// Go to next record
		start_byte = start_byte + next_record
	}

	fclose(fh_in)
}


void read_dbf(string scalar dbf_file)
{

	real matrix   length_decimal
	real scalar   fh_in
	string scalar vname, vlength, format, rlength
	string scalar val
	transmorphic  colvector C

	real scalar   ver, year, num_of_records, num_bytes_header
	real scalar   num_bytes_record, field_des_bytes, num_of_vars
	real scalar   next_var, next_type, next_length, vars_types
	real scalar   k, i, j, type, vlen, bufsize, numofbufs, obs, lines
	real scalar   start_str, num_vlength


	// Open dBASE file .dbf, open buffer, and set byte order
	fh_in = fopen(dbf_file, "r")
	C = bufio()
	bufbyteorder(C, 1)

	// Get .dbase version
	ver = fbufget(C, fh_in, "%1b")
	bufbyteorder(C, 2)

	// Get year of file
	year = fbufget(C, fh_in, "%1bu") + 1900

	if (ver!=3| year<1900 | year>2050) {
		errprintf("%s: invalid dbase (.dbf) file\n", dbf_file)
		exit(610)
	}

	// Number of records in the table
	fseek(fh_in, 4, -1)
	num_of_records = fbufget(C, fh_in, "%4bu")

	// Number of bytes in the header.
	num_bytes_header = fbufget(C, fh_in, "%2bu")

	// Number of bytes in the record
	num_bytes_record = fbufget(C, fh_in, "%2bu")

	// Starting value of descriptor bytes and number of vars
	field_des_bytes = num_bytes_header - 33
	num_of_vars = field_des_bytes/32

	// Set starting byte postion for fields of descriptor bytes
	next_var = 32
	next_type = 43
	next_length = 48

	// Create matrix for var names and types
	vars_types = J(num_of_vars,2,"")

	// Create matrix for var length
	length_decimal = J(num_of_vars,1,.)

	//Loop over each descriptor
	for (i=1; field_des_bytes!=0; i++) {
		// Get var name
		fseek(fh_in, next_var, -1)
		vars_types[i,1] = fbufget(C, fh_in, "%11s")

		// Get var type
		fseek(fh_in, next_type, -1)
		vars_types[i,2] = fbufget(C, fh_in, "%5s")

		// Get var length
		fseek(fh_in, next_length, -1)
		length_decimal[i,1] = fbufget(C, fh_in, "%1bu")

		next_var    = next_var + 32
		next_type   = next_type + 32
		next_length = next_length + 32

		field_des_bytes = field_des_bytes - 32
	}

	// Create dataset
	st_addobs(num_of_records)

	// Create variables
	for(i=1; i<=num_of_vars; i++ ) {
		vname   = strtrim(vars_types[i,1])
		type    = vars_types[i,2]
		vlength = strofreal(length_decimal[i,1])
		format  = "str" + vlength
		num_vlength = strtoreal(vlength)

		if (num_vlength > st_numscalar("c(maxstrvarlen)")) {
			printf("{text}variable %s truncated\n", vname)
			format = "str" + "244"
		}
		if (type == "C")  (void) st_addvar(format, vname)
		else if (type == "L")  (void) st_addvar("format", vname)
		else if (type == "N")  (void) st_addvar("double", vname)
		else if (type == "F")  (void) st_addvar("float",  vname)
		else if (type == "D")  (void) st_addvar("long",   vname)
		else  {
			errprintf("%s: invalid dBASE data type\n", dbf_file)
			exit(610)
		}

	}

	// Go to start of obserations
	fseek(fh_in, num_bytes_header, -1)

	// Read observations in 200 block chunks
	bufsize = 200
	numofbufs = floor(num_of_records/bufsize)

	obs = 1
	for (k=1; k<=numofbufs; k++) {
		rlength = strofreal(num_bytes_record)
		format = "%" + rlength + "s"
		lines = fbufget(C, fh_in, format, bufsize, 1)

		for(i=1; i<=bufsize; i++) {
			start_str = 2
			for(j=1; j<=num_of_vars; j++) {
				type    = vars_types[j,2]
				vlen    = length_decimal[j,1]
				val     = strtrim(substr(lines[i,1],
						start_str, vlen))

				if (type=="C" | type=="L") {
					st_sstore(obs,j,val)
				}
				else	st_store(obs,j, strtoreal(val))
				start_str = start_str + vlen
			}
			obs++
		}
	}

	// Store the remander of observations
	bufsize = num_of_records - numofbufs*bufsize
	if (bufsize) {
		rlength = strofreal(num_bytes_record)
		format = "%" + rlength + "s"
		lines = fbufget(C, fh_in, format, bufsize, 1)
		for(i=1; i<=bufsize; i++) {
			start_str = 2
			for(j=1; j<=num_of_vars; j++) {
				type = vars_types[j,2]
				vlen = length_decimal[j,1]
				val  = strtrim(substr(lines[i,1],
						start_str, vlen))

				if (type == "C" | type == "L") {
					st_sstore(obs,j,val)
				}
				else {
					st_store(obs,j, strtoreal(val))
				}
				start_str = start_str + vlen
			}
			obs++
		}
	}

	fclose(fh_in)
}
end
