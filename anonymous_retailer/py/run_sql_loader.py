import os
import subprocess

def run_sql_loader(program="", log='../output/make.log', options={}, stream=None):
    progname = os.path.splitext(os.path.basename(program))[0]
    default_log  = '../temp/' + progname + '.log'
    default_bad  = '../temp/' + progname + '.bad'
    default_user = '/'

    # construct list of options with default values
    logfile = options.pop('log', default_log)
    baddir  = options.pop('bad', default_bad)
    userid  = options.pop('userid', default_user)

    loader_call = [
        'sqlldr',
        'control=' + program, 
        'userid=' + userid, 
        'log=' + logfile,
        'bad=' + baddir
    ]
    
    if not len(options) == 0: 
        for opt in options:
            loader_call.append(opt + '=' + options[opt])

    # Mask user password for printing info to log file
    if userid != default_user:
        masked_user = userid[:userid.find('/')] + '/*****'
    else:
        masked_user = userid
    
    mask_loader_call = [
        'sqlldr',
        'control=' + program, 
        'userid=' + masked_user, 
        'log=' + logfile,
        'bad=' + baddir
    ]
    
    if stream is not None:
        stream_call = stream.split(' ')

        print "\n\nEXECUTE: " + " ".join(stream_call + mask_loader_call)
        p1 = subprocess.Popen(stream_call, stdout=subprocess.PIPE)
        subprocess.check_call(loader_call, stdin=p1.stdout)
    else:
        print "\n\nEXECUTE: " + " ".join(mask_loader_call)
        subprocess.check_call(loader_call, shell=False)

    with open(log, mode='ab') as log_fh:
        log_fh.write(open(program, 'rU').read())
        log_fh.write(open(logfile, 'rU').read())
    os.unlink(logfile)