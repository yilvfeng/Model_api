
from sqlalchemy import create_engine
from settings import kdtMysql
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy import exc
from sqlalchemy import event
from sqlalchemy.pool import Pool


def get_mysql_engine(**mysql_config):
    uri = 'mysql://%s:%s@%s:%s/%s?charset=utf8' % (mysql_config['user'],
                                                   mysql_config['passwd'],
                                                   mysql_config['host'],
                                                   mysql_config['port'],
                                                   mysql_config['db'])
    engine = create_engine(uri,
                           pool_size=mysql_config['pool_size'],
                           max_overflow=mysql_config['max_overflow'],
                           encoding='utf8')
    return engine

kdtUri = 'mysql://%s:%s@%s:%s/%s?charset=utf8' % (kdtMysql['user'], kdtMysql['passwd'],
                                                  kdtMysql['host'], kdtMysql['port'], kdtMysql['db'])
kdtEngine = create_engine(kdtUri,
                          pool_size=kdtMysql['pool_size'],
                          max_overflow=kdtMysql['max_overflow'],
                          encoding='utf8'
                          )

kdtMysql = get_mysql_engine(**kdtMysql)

@event.listens_for(Pool, "checkout")
def ping_connection(dbapi_connection, connection_record, connection_proxy):
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("SELECT 1")
    except:
        raise exc.DisconnectionError()
    cursor.close()