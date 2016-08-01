*! 1.0.0  17apr2000  jw/ics
program define renamev
	version 6
	
	gettoken oldname newdef : 0, quotes
	unab oldname : `oldname'
	
	* newdef is new varname ?
	capt confirm new var `newdef'
	if !_rc {
		RenVar `oldname' `newdef' 
		exit
	}
	* newdef is old varname
	capt confirm var `newdef'
	if !_rc {
		exit 110
	}
	
	* newdef should be string_expression
	local newname = `newdef'
	local newname : word 1 of `newname'
	local tail    = substr("`newname'",9,.)
	local newname = substr("`newname'",1,8)
	RenVar `oldname' `newname'
end

program define RenVar
	args oldname newname
	if "`newname'" != "`oldname'" {
		di in gr "`oldname' -> `newname'" in ye "`tail'"
		rename `oldname' `newname' 
	}
end	
exit

