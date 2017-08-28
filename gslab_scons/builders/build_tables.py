import os
import gslab_scons.misc as misc
from gslab_fill import tablefill
from gslab_scons import log_timestamp
from gslab_scons._exception_classes import ExecCallError

def build_tables(target, source, env):
    '''Build a SCons target by filling a table

    This function uses the tablefill function from gslab_fill to produced a 
    filled table from (i) an empty table in a LyX/Tex file and (ii) text files 
    containing data to be used in filling the table. 

    Parameters
    ----------
    target: string or list 
        The target(s) of the SCons command.
    source: string or list
        The source(s) of the SCons command. The first source specified
        should be the LyX/Tex file specifying the table format. The subsequent 
        sources should be the text files containing the data with which the
        tables are to be filled. 
    env: SCons construction environment, see SCons user guide 7.2
    '''
    # Prelims
    source = misc.make_list_if_string(source)
    target = misc.make_list_if_string(target)

    start_time  = misc.current_time()
    
    # Set up source file (table format)
    source_file = str(source[0])
    misc.check_code_extension(source_file, ['.lyx', '.tex'])

    # Set up input string (list of data tables)
    input_string = ' '.join([str(i) for i in source[1:]])

    # Set up target file (filled table)
    target_file = str(target[0])
    target_dir  = misc.get_directory(target_file)    
    misc.check_code_extension(target_file, ['.lyx', '.tex'])
    try:
        log_ext = '_%s' % env['log_ext']
    except KeyError:
        log_ext = ''
    log_file = os.path.join(target_dir, ('sconscript%s.log' % log_ext))
    
    # Command call
    output  = tablefill(input    = input_string, 
                        template = source_file, 
                        output   = target_file)
    
    with open(log_file, 'wb') as f:
        f.write(output)
        f.write("\n\n")
        
    # Close log
    if "traceback" in str.lower(output): # if tablefill.py returns an error   
        command = """tablefill(input    = %s, 
                         template = %s, 
                         output   = %s)""" % (input_string, source_file, target_file)         
        message = misc.command_error_msg("tablefill.py", command)
        raise ExecCallError(message)
    
    # Check if targets exist after build
    # misc.check_targets(target)
    
    end_time = misc.current_time()    
    log_timestamp(start_time, end_time, log_file)

    return None
