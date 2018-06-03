import os
import os.path as op


def get_db_dsn():
    tmp = op.dirname(__file__)
    tmp = op.join(tmp, '..')
    tmp = op.normpath(tmp)
    tmp = op.join(tmp, 'db.sqlite')
    return tmp


DATABASE_DSN = get_db_dsn()
WEATHER_API_KEY = os.environ['WEATHER_API_KEY']
