#pylint: disable=line-too-long
"""
Module to assist with connections to  relational databases, currently configured to psycopg2 datbases.
"""
import psycopg2
from legopython import lp_awssession
from legopython.lp_logging import logger

def get_db_conn(dblookupname: str) -> dict:
    """
    Return a dictionary of connection information for  Databases.
    Designed to be called by DB.db_connection(<databasename>), but can also be called natively
    """

    _databases = {
            'prodro' : {'host':'ro.health.com','database':'prod','user':'prod_user','credstashkey':'pgsql.implementationpw.prod','environment':'prod', 'port': 5432},
            }

    if dblookupname not in _databases:
        logger.error(f'Database not found, available databases are: {list(_databases.keys())}')
        return None

    #Production databases TODO: Migrate credstash to secrets manager
    #_databases[dblookupname]['password'] = Credstash.get_password_from_credstash(secret_name=_databases[dblookupname]['credstashkey'],environment=_databases[dblookupname]['environment'])
    
    if 'port' not in _databases[dblookupname]: #Set default port here to save space above
        _databases[dblookupname]['port'] = '5432'
    
    return _databases[dblookupname]


def psycopg2_db_connection(database: str) -> tuple[psycopg2.extensions.connection, psycopg2.extensions.cursor]:
    '''Return a connection and cursor for the specified DB'''
    db_conn = get_db_conn(database)
    if db_conn is None :
        return None
    conn = psycopg2.connect(
        host=db_conn['host'],
        port=db_conn['port'],
        database=db_conn['database'],
        user=db_conn['user'],
        password=db_conn['password'],
        sslmode='require',
        sslrootcert='~/.postgresql/postgresql.crt'
        )
    return conn,conn.cursor()


def return_generator(cursor, arraysize=1500) :
    '''Internal function to create a generator for iterating over return values. EX)

    conn,cur = lp_sql.psycopg2_db_connection(db)
    sql = """SELECT tablecolumn
    FROM tablename
    WHERE tablecolumn in %s
    and tablecolumn2 not in (0)
    """
    cur.execute(sql, (tuple(tablecolumn),))
    tablecolumn_ids = list(sql.return_generator(cur))
    '''
    while True :
        results = cursor.fetchmany(arraysize)
        if not results :
            break
        yield from results


def main():
    '''Check AWS Session'''
    if lp_awssession.checkSession() is False :
        exit(1)


if __name__ == '__main__':
    main()
