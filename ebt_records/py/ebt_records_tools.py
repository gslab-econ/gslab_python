import pandas as pd
import numpy  as np
from save_data import save_data

pd.options.mode.chained_assignment = 'raise'

TRANSACTIONS_START_MONTH = '2008-10' 
TRANSACTIONS_END_MONTH   = '2012-09'

PY_MONTHS = pd.period_range(start = TRANSACTIONS_START_MONTH,
                            end   = TRANSACTIONS_END_MONTH,
                            freq  = 'M')
PY_MONTHS_AS_INT = pd.DataFrame({
                       'month'     : PY_MONTHS,
                       'month_int' : range(1,PY_MONTHS.size+1)
                   })

def mask_id(data, rawname, maskname, apply_to = None):
    mask_fname = "../external_links/anonymous_crosswalks/" + maskname + '.csv'
    masked_id  = pd.read_csv(mask_fname)

    if apply_to is not None:
        data = data.rename(
                    columns = {maskname : '_' + maskname}, copy = False
                ).rename(
                    columns = {apply_to : rawname}, copy = False
                )

    masked_data = data.merge(masked_id, on = rawname, how = 'left')
    if masked_data[maskname].isnull().any():
        raise StandardError("Expected all ids to match but they did not")

    masked_data = masked_data.drop(rawname, axis = 'columns')
    if apply_to is not None:
        masked_data = masked_data.rename(
                          columns = {maskname : 'mask_' + apply_to}, copy = False
                      ).rename(
                          columns = {'_' + maskname : maskname}, copy = False
                      )
    return masked_data

def build_numeric_key(data, name, saving = None, newname = None, **kwargs):
    string_var = np.sort(data.loc[:,name].unique())
    
    if newname is None: newname = name + '_key'
    lookup = pd.DataFrame({
                 name    : string_var, 
                 newname : range(string_var.size)
             })
    
    if saving is not None:
        save_data(
                      lookup, saving,
                      ftype = 'hdf5',
                      return_object = False,
                      data_key = newname,
                      key = name,
                      **kwargs
                  )

    data = data.merge(
               right = lookup,
               on    = name,
               how   = 'left'
           ).drop(
               labels = name, 
               axis   = 'columns'
           )
    assert not data[newname].isnull().any()
    return data

def drop_duplicates(data, **kwargs):
    len_before = len(data.index)
    data = data.drop_duplicates(**kwargs)
    len_after = len(data.index)

    obs_dropped = len_before - len_after
    print '%d observations deleted' %obs_dropped
    return data

def drop_all_duplicates(data, on):
    if len(on[0]) == 1: on = [on]
    data.loc[:, 'num_in_group'] = 1
    num_in_group = data.loc[:, on + ['num_in_group']].groupby(on, as_index = False).sum()
    data = data.drop(
               'num_in_group', 
               axis = 'columns'
           ).merge(
                right = num_in_group, 
                on = on,
                how = 'outer'
           )
    assert not data[on].isnull().any().any()

    len_before = len(data.index)
    data = data.loc[data.loc[:,'num_in_group'] == 1,:].drop(
               'num_in_group', 
               axis = 'columns'
           )
    len_after = len(data.index)

    obs_change = len_before - len_after
    print '%d observations deleted' %obs_change
    return data