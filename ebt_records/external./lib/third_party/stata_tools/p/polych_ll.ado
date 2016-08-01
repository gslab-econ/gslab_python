pro def polych_ll
   version 8.1
   
   args lf rho
   
   #delimit ;
   qui replace __POLYpi = 
                   binorm(__POLY1hi,__POLY2hi,`rho') -
                   binorm(__POLY1lo,__POLY2hi,`rho') -
                   binorm(__POLY1hi,__POLY2lo,`rho') +
                   binorm(__POLY1lo,__POLY2lo,`rho')
   ;
   #delimit cr
   qui replace `lf' = ln( __POLYpi )

end
