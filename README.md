## demo for weather app

This project at least need Python 3.6, and Chrome 64 or Firefox 59.

You need API key from https://openweathermap.org/.

Before start you need to initialize the database.

```sh
pip install -r requirements.txt
export WEATHER_API_KEY='your_api_key'
python3 -m weather.database
```

Then you can start the server.
```sh
python3 -m weather
```

By default it listen to localhost:8000.
For a live demo please see https://www.wcpan.me/weather/.
