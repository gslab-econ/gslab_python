import datetime as dt
from R2_connection import R2_connection

def get_chunks(size, time_units):
    with R2_connection() as cxn:
        res = cxn.execute(
                  """ SELECT MIN(transaction_date)
                        FROM dim.date_lookup
                       GROUP BY %time_units%
              """).fetchall()
        last_day, = cxn.execute("SELECT MAX(transaction_date) FROM dim.date_lookup").fetchall()[0]
    
    res.sort()
    res.append((last_day+dt.timedelta(days=1),))
    timesteps = map(lambda x: str(x[0])[:10].replace('-',''), res)
    return [{'start_date' : timesteps[ix],
             'end_date'   : timesteps[(ix+size) if (ix+size) < len(timesteps) else -1]}
            for ix in range(0,len(timesteps)-1,size)]

def append(queue, base_name):
    table_idx = queue.get()     
    while (table_idx != 'END'):
        chunk_name = '{0}{1}'.format(base_name, table_idx)
        with R2_connection() as cxn:

            if (table_exists(base_name) is False):
                cxn.execute(
                    "CREATE TABLE %base_name% AS (SELECT * FROM %chunk_name%)",
                    verbose=False)
            else:
                cxn.execute(
                    """ INSERT INTO %base_name%
                        SELECT /*+ APPEND */ * FROM %chunk_name%
                    """, verbose=False)
            cxn.execute("DROP TABLE %chunk_name% PURGE", verbose=False)
        table_idx = queue.get()

def table_exists(table_name):
    with R2_connection() as cxn:
        existant_tables = cxn.execute(
                              "SELECT table_name FROM user_tables",verbose=False
                          ).fetchall()

    return table_name.upper() in map(lambda x: x[0], existant_tables) 
