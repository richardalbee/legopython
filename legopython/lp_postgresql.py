"""Module for connecting to postgresql databases."""
import psycopg2
from legopython import lp_dbsecrets

def psycopg2_db_connection(database: str) -> tuple[psycopg2.extensions.connection, psycopg2.extensions.cursor]:
    '''Return a connection and cursor for the specified database.
    
    example)
    conn,cur = lp_postgresql.psycopg2_db_connection(db)
    '''
    db_conn = lp_dbsecrets.get_db_conn(database)
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
    '''Generator for iterating over return values from a SQL query.

    Example)
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
