/**********************************************************
*
* INSERT_TAG.ADO: Inserts HTML tags into log file
*
**********************************************************/

program insert_tag
    version 12
    syntax anything(name=tag) [, open close prefix(str)]
    
    if ( "`open'"=="" & "`close'"=="" ) | ( "`open'"!="" & "`close'"!="" ) {
        di as error "Either the open or close options must be provided"
        exit 198
    }
    
    if wordcount("`tag'")!=1 {
        di as error "Tag must be single string"
        exit 198
    }
    
    if "`tag'"=="" {
        di as error "Tag must be provided"
        exit 198
    }
    
    if "`prefix'"!="" {
        local tag = "`prefix'" + "_" + "`tag'"
    }
   else {
        local tag = "textfill_" + "`tag'"
    }
    
    if "`open'"!="" {
        di "<`tag'>"
    }
    else {
        di "</`tag'>"
    }
end


