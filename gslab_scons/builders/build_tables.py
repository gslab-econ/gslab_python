import gslab_scons.misc as misc
from gslab_fill import tablefill


def build_tables(target, source, env):
    '''Build a SCons target by filling a table

    This function uses the tablefill function from gslab_fill to produced a 
    filled table from (i) an empty table in a LyX file and (ii) text files 
    containing data to be used in filling the table. 

    Parameters
    ----------
    target: string or list 
        The target(s) of the SCons command.
    source: string or list
        The source(s) of the SCons command. The first source specified
        should be the LyX file specifying the table format. The subsequent 
        sources should be the text files containing the data with which the
        tables are to be filled. 
    env: SCons construction environment, see SCons user guide 7.2
    '''
    # Prelims
    source = misc.make_list_if_string(source)
    target = misc.make_list_if_string(target)
    
    # Set up source file (table format)
    source_file = str(source[0])
    misc.check_code_extension(source_file, '.lyx')

    # Set up target file (filled table)
    target_file = str(target[0])
    misc.check_code_extension(target_file, '.lyx')
    
    tablefill(input    = ' '.join([str(i) for i in source[1:]]), 
              template = source_file, 
              output   = target_file)
    return None
