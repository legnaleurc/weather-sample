import asyncio
import os.path as op
import signal
import sys

from aiohttp import web as aw
import aiohttp_jinja2 as aj
import jinja2
from wcpan.logger import setup as setup_logger, EXCEPTION, INFO

from . import view, database, api, weather
from .conf import DATABASE_DSN, WEATHER_API_KEY


class Daemon(object):

    def __init__(self, args):
        setup_logger((
            'aiohttp',
            'weather',
        ))

        self._loop = asyncio.get_event_loop()
        self._finished = asyncio.Event()

    def __call__(self):
        self._loop.create_task(self._guard())
        self._loop.add_signal_handler(signal.SIGINT, self._close_from_signal)
        self._loop.run_forever()
        self._loop.close()
        return 0

    async def _guard(self):
        try:
            return await self._main()
        except Exception as e:
            EXCEPTION('weather', e)
        finally:
            self._loop.stop()
        return 1

    async def _main(self):
        app = aw.Application()

        setup_static(app)
        setup_template(app)
        setup_api(app)

        # use context managers to manage clean-up actions
        with database.Database(DATABASE_DSN) as db:
            async with weather.Weather(WEATHER_API_KEY) as w, \
                       ServerContext(app):
                app['db'] = db
                app['weather'] = w

                # block here until SIGINT
                await self._wait_for_finished()

        return 0

    def _close_from_signal(self):
        self._finished.set()

    async def _wait_for_finished(self):
        await self._finished.wait()


class ServerContext(object):

    def __init__(self, app):
        self._runner = aw.AppRunner(app)

    async def __aenter__(self):
        await self._runner.setup()
        site = aw.TCPSite(self._runner, host='127.0.0.1', port=8000)
        await site.start()

        INFO('weather') << 'listening on 127.0.0.1:8000'

        return self._runner

    async def __aexit__(self, exc_type, exc, tb):
        await self._runner.cleanup()


def setup_static(app):
    root = op.dirname(__file__)
    static_path = op.join(root, 'static')

    app.router.add_static('/static/', path=static_path, name='static')
    app['static_root_url'] = '/static'


def setup_template(app):
    root = op.dirname(__file__)
    template_path = op.join(root, 'template')

    aj.setup(app, loader=jinja2.FileSystemLoader(template_path))

    app.router.add_view(r'/', view.IndexHandler)


def setup_api(app):
    app.router.add_view(r'/api/v1/country/{country_id:\d+}/city', api.CityHandler)
    app.router.add_view(r'/api/v1/weather/{city_id:\d+}', api.WeatherHandler)
    app.router.add_view(r'/api/v1/other/{icon_id:\d+}', api.OtherHandler)


main = Daemon(sys.argv)
exit_code = main()
sys.exit(exit_code)
