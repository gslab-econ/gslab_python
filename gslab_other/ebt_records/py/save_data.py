import os
import pandas as pd

def save_data(pd_object, filename, data_key, ftype = 'csv', 
              log = None, save = True, return_object = False, 
              mode = 'ab', **kwargs):

    ftype = ftype.lower()
    valid_ftypes = ['csv', 'hdf5', 'dta']
    if not ftype in valid_ftypes:
        print "File type must be 'hdf5', 'csv' or 'dta'\n"
        err_msg = 'File type ' + ftype + ' is not supported'
        raise NotImplementedError(err_msg)

    # check that key is non-missing and uniquely identifying

    keyvars = pd_object.loc[:,data_key]
    if len(data_key[0]) > 1: key_str = ' '.join(data_key)
    else: key_str = data_key 
    if keyvars.duplicated().any():
        err_msg = 'Variables: ' + key_str + ' do not uniquely identify the observations'
        raise StandardError(err_msg)

    is_null = keyvars.isnull().any()
    if is_null.any():
        null_vars = is_null.ix[is_null].index.tolist()
        null_vars_str = ' '.join(null_vars)
        err_msg = 'Variables: ' + null_vars_str + ' should never be missing'

    # place the key at the top of the stack and sort by key
    if len(data_key[0]) == 1: data_key = [data_key]
    varlist   = pd.Series(pd_object.columns)
    reordered = data_key + varlist[~varlist.isin(data_key)].tolist()
    pd_object = pd_object.loc[:,reordered]
    pd_object = pd_object.sort(data_key)

    object_description = pd_object.describe(include = 'all').T
    object_description = object_description.loc[:,['count','mean','std','min','max']]
    delimiter = "=" * 98

    if save is False: prefix = 'Object: '
    if save is True: prefix = 'File: '
    key = kwargs.get('key')

    print delimiter
    print prefix + filename
    print 'Key: '  + key_str
    if ftype == 'hdf5': print 'Store key: ' + key
    print delimiter
    print object_description
    print '\n\n'
    
    if save is False: return pd_object
    if not 'temp' in filename:
        is_valid_path = False
        is_writable = getattr(log, 'write', False)
        if log is None: 
            log = '../output/data_file_manifest.log'
            is_valid_path = True
        elif is_writable is not False:
            log_fh = log
        else:
            is_valid_path = True

        if (is_valid_path is False) and (is_writable is False):
            err_msg = 'Argument "log" must be a valid path or an instance with a "write" attribute'
            raise StandardError(err_msg)

        if is_valid_path is True:
            log_fh = open(log, mode = 'ab')

        print >> log_fh, delimiter
        print >> log_fh, prefix + filename
        print >> log_fh, 'Key: '  + key_str
        if ftype == 'hdf5': print >> log_fh, 'Store key: ' + key
        print >> log_fh, delimiter
        print >> log_fh, object_description
        print >> log_fh, '\n\n'

        if is_valid_path is True:
            log_fh.close()

    include_index = kwargs.pop('index', False)
    if ftype == 'csv' : pd_object.to_csv(filename, index = include_index, **kwargs)
    if ftype == 'hdf5': pd_object.to_hdf(filename, **kwargs)
    if ftype == 'dta' : pd_object.to_stata(filename, write_index = include_index, **kwargs)
    if return_object is not False: return pd_object