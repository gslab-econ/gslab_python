*! 1.0.0  01Mar1999  Jeroen Weesie/ICS
program define placevar
   version 6.0
   syntax varlist(min=1) [, After(varname) Before(varname) First Last]

   if "`after'`before'`first'`last'" == "" {
      local first 1
   }

	if "`first'" ~= "" {
      order `varlist'
      exit
   }

   * check that -pl- does not occur in -vlist-
   local place `after'`before'
   if "`place'" ~= "" {
      local temp : subinstr local varlist "`place'" "", /*
         */ word count(local nch)
      if `nch' > 0 {
         di in re "`place' should not occur the list of variables to be moved"
         exit 198
      }
   }

   * eliminate -varlist- from -all-
   unab all : _all
   tokenize `varlist'
   while "`1'" ~= "" {
      local all : subinstr local all "`1'" "", word
      mac shift
   }

   * re-assemble varlist in new order
   if "`last'" ~= "" {
      local order "`all' `varlist'"
   }
   else {
      tokenize `all'
      while "`1'" ~= "" {
         if "`1'" == "`place'" {
            mac shift
            if "`before'" ~= "" {
               * local moves the front
               local order "`order' `varlist' `place'"
            }
            else {
               * local moves the front
               local order "`order' `place' `varlist'"
            }
            local 1
         }
         else {
            local order "`order' `1'"
            mac shift
         }
      }
   }

   * apply new ordering
   order `order'
end

