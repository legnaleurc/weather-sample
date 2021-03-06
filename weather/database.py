import datetime as dt
import json
import math
import sqlite3
from typing import Any, Dict, List, Text, Union

from .conf import DATABASE_DSN


SQL_CREATE_TABLES = [
    '''
    CREATE TABLE country (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
    );
    ''',
    '''
    CREATE TABLE city (
        id INTEGER NOT NULL,
        name TEXT NOT NULL,
        country INTEGER NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY (country) REFERENCES country (id)
    );
    ''',
    '''
    CREATE TABLE weather (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city INTEGER NOT NULL,
        mtime INTEGER NOT NULL,
        temp REAL NOT NULL,
        temp_min REAL NOT NULL,
        temp_max REAL NOT NULL,
        icon INTEGER NOT NULL,
        FOREIGN KEY (city) REFERENCES city (id)
    );
    ''',
    'CREATE INDEX ix_city_country ON city(country);',
]


class Database(object):

    def __init__(self, dsn) -> None:
        self._dsn = dsn

    def __enter__(self) -> 'Database':
        try:
            self._try_create()
        except sqlite3.OperationalError as e:
            pass
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        self._db.close()
        self._db = None

    def update_city(self, city_data: Dict[Text, Any]) -> None:
        '''
        This function only used for import city data.
        '''
        # some cities do not have name, ignore them
        if not city_data['name']:
            return
        # some data represent continent, ignore them
        if not city_data['country']:
            return

        country_id = self.get_country_id_by_name(city_data['country'])
        if not country_id:
            country_id = self.create_country(city_data['country'])

        with ReadWrite(self._db) as query:
            query.execute('''
                INSERT INTO city
                (id, name, country)
                VALUES
                (?, ?, ?)
            ;''', (city_data['id'], city_data['name'], country_id))

    def get_country_id_by_name(self, name: Text) -> Union[Text, None]:
        with ReadOnly(self._db) as query:
            query.execute('SELECT id FROM country WHERE name=?;', (name,))
            rv = query.fetchone()
        if not rv:
            return None
        return rv['id']

    def create_country(self, name: Text) -> Text:
        with ReadWrite(self._db) as query:
            query.execute('INSERT INTO country (name) VALUES (?);', (name,))
            return query.lastrowid

    def get_country_list(self) -> List[Dict[Text, Any]]:
        with ReadOnly(self._db) as query:
            query.execute('SELECT id, name FROM country;')
            rv = query.fetchall()
        return [{
            'id': _['id'],
            'name': _['name'],
        } for _ in rv]

    def get_city_list_by_country_id(self, id_: int) -> List[Dict[Text, Any]]:
        with ReadOnly(self._db) as query:
            query.execute('SELECT id, name FROM city WHERE country=?;', (id_,))
            rv = query.fetchall()
        return [{
            'id': _['id'],
            'name': _['name'],
        } for _ in rv]

    def get_weather_by_city_id(self, id_: int) -> Union[Dict[Text, Any], None]:
        with ReadOnly(self._db) as query:
            query.execute('''
                SELECT mtime, temp, temp_min, temp_max, icon
                FROM weather
                WHERE city=?
            ;''', (id_,))
            rv = query.fetchone()

        # no cached value
        if not rv:
            return None

        # cached one day ago, need new one
        now = dt.datetime.now()
        mtime = dt.datetime.fromtimestamp(rv['mtime'])
        if (now - mtime) > dt.timedelta(days=1):
            return None

        return {
            'temp': rv['temp'],
            'temp_min':  rv['temp_min'],
            'temp_max':  rv['temp_max'],
            'icon':  rv['icon'],
        }

    def update_weather(self,
                       city_id: int,
                       weather_data: Dict[Text, Any]) -> None:
        with ReadWrite(self._db) as query:
            # just drop cache, we are going to update almost all fields anyway
            query.execute('DELETE FROM weather WHERE city=?;', (city_id,))

            now = dt.datetime.now()
            now = math.floor(now.timestamp())
            query.execute('''
                INSERT INTO weather
                (city, mtime, temp, temp_min, temp_max, icon)
                VALUES
                (?, ?, ?, ?, ?, ?)
            ;''', (city_id, now,
                   weather_data['temp'],
                   weather_data['temp_min'],
                   weather_data['temp_max'],
                   weather_data['icon']))

    def get_city_list_by_icon_id(self, id_):
        with ReadOnly(self._db) as query:
            query.execute('''
                SELECT city.name AS city, country.name AS country
                FROM weather
                    INNER JOIN city ON city.id=weather.city
                    INNER JOIN country ON country.id=city.country
                WHERE icon=?;
            ''', (id_,))
            rv = query.fetchall()

        if not rv:
            return []

        # TODO check mtime
        return ['{0}, {1}'.format(_['city'], _['country']) for _ in rv]

    def _open(self) -> sqlite3.Connection:
        db = sqlite3.connect(self._dsn)
        db.row_factory = sqlite3.Row
        return db

    def _try_create(self) -> None:
        self._db = self._open()
        with ReadWrite(self._db) as query:
            for sql in SQL_CREATE_TABLES:
                query.execute(sql)


class ReadOnly(object):

    def __init__(self, db: sqlite3.Connection) -> None:
        self._db = db

    def __enter__(self) -> sqlite3.Cursor:
        self._cursor = self._db.cursor()
        return self._cursor

    def __exit__(self, exc_type, exc_value, exc_tb) -> bool:
        self._cursor.close()


class ReadWrite(object):

    def __init__(self, db: sqlite3.Connection) -> None:
        self._db = db

    def __enter__(self) -> sqlite3.Cursor:
        self._cursor = self._db.cursor()
        return self._cursor

    def __exit__(self, exc_type, exc_value, exc_tb) -> bool:
        if exc_type is None:
            self._db.commit()
        else:
            self._db.rollback()
        self._cursor.close()


def initialize() -> None:
    # this function should not be used in concurrent way
    # so just use blocking functions here
    import gzip
    import urllib.request as ur

    # download city data from openweathermap
    url = 'http://bulk.openweathermap.org/sample/city.list.json.gz'
    with ur.urlopen(url) as link, \
         gzip.GzipFile(fileobj=link) as gz:
         cities = json.load(gz)

    # save to database
    with Database(DATABASE_DSN) as db:
        for city in cities:
            db.update_city(city)


if __name__ == '__main__':
    initialize()
