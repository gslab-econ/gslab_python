rng(0)
test = rand(1)
command_line_arg = getenv('CL_ARG')
save(sprintf('../build/test%s.mat', command_line_arg))
exit