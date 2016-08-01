program define polyser_ll
   version 8.1
   
   args lf rho   

   #delimit ;
   qui replace `lf' = 
      ln(
        (
            norm( (__POLY2hi - `rho'*$ML_y1)/sqrt(1-`rho'*`rho') ) -
            norm( (__POLY2lo - `rho'*$ML_y1)/sqrt(1-`rho'*`rho') )
        ) * normden($ML_y1)
      )
   ;
   #delimit cr

end
