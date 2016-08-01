*! Principal component analysis based on polychoric correlations
*! Author: Stas Kolenikov, skolenik@unc.edu. Version 1.0

program define polychoricpca, rclass
  
  syntax varlist(numeric min=2) [aw pw fw /], [SCore(passthru) NSCore(passthru) nolog *]
  
  if "`score'"!="" & "`nscore'"=="" {
     di as err "how many score variables?"
     exit 198
  }
  
  if "`exp'"=="" {
     tempvar ww
     qui g byte `ww'=1
     local exp `ww'
     local weight pw
  }
  
  polychoric `varlist' [`weight'=`exp'] , pca nolog `score' `nscore' `options'
  return add
  
end
