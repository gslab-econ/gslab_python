from gslab_builder import GSLabBuilder

from gslab_fill import tablefill


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
    builder_attributes = {
        'name': 'Tablefill',
        'valid_extensions': ['.lyx', '.tex'],
        'exec_opts':  '-interaction nonstopmode -jobname'
    }
    builder = TableBuilder(source, target, env, **builder_attributes)
    builder.execute_system_call()
    return None

class TableBuilder(GSLabBuilder):
    '''
    '''
    def __init__(self, source, target, env, name = '', valid_extensions = [], exec_opts = ''):
        '''
        '''
        super(TableBuilder, self).__init__(source, target, env, name = name, 
                                          valid_extensions = valid_extensions,
                                          exec_opts = exec_opts)
        self.input_string = ' '.join([str(i) for i in source[1:]])
        self.target_file  = self.target[0]
        return None


    def add_call_args(self):
        self.call_args = None
        return None

    def do_call(self):
        '''
        '''
        output = tablefill(input    = self.input_string, 
                           template = self.source_file, 
                           output   = self.target_file)
        with open(self.log_file, 'wb') as f:
            f.write(output)
            f.write('\n\n')
        if 'traceback' in str.lower(output): # if tablefill.py returns an error   
            command = 'tablefill(input    = %s,\n' \
                      '          template = %s,\n' \
                      '          output   = %s)' \
                      % (self.input_string, self.source_file, self.target_file)         
            self.raise_system_call_exception(command = command)
        return None
