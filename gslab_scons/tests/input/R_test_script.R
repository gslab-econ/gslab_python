args = commandArgs(trailingOnly = TRUE)
cat(args[1])

NCols=5
NRows=5 
x<-matrix(runif(NCols*NRows), ncol=NCols)
write(x, 'output.txt')
cat('Test script complete')