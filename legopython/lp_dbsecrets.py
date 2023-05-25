"""Securely retrieve connection information for connecting to databases"""
from legopython import lp_secretsmanager

def get_db_conn(dblookupname: str) -> dict:
    """Return a dictionary of connection information for Databases as pulled from secrets manager.
    Designed to be called via psycopg2_db_connection(<databasename>) to return a connection

    A secretsmanager secret must have the following key value pairs:
        host: {host}
        port: {port}
        database: {database}
        user: {user}
        password: {password}
    
    Currently only supports Secrets manager.
    """
    database_conns = {
            'production_ro' : {'secret_name': 'production_key_name'},
            }
    if dblookupname not in database_conns:
        raise ValueError(f'Database not found, available databases are: {list(database_conns.keys())}')
    return lp_secretsmanager.get_secret(database_conns[dblookupname]['secret_name'])

