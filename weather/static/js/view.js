(function () {
    'use strict';

    const Weather = window.Weather || {};


    class View extends EventTarget {

        constructor (selector) {
            super();
            this._el = document.querySelector(selector);
        }

        // a quick helper for dispatchEvent
        trigger (type, detail) {
            const ev = new CustomEvent(type, {
                detail,
            });
            this.dispatchEvent(ev);
        }

        get el () {
            return this._el;
        }

        show () {
            this.el.classList.remove('hidden');
        }

        hide () {
            this.el.classList.add('hidden');
        }

    }


    class CountrySelectionWidget extends View {

        constructor (selector) {
            super(selector);

            this.el.addEventListener('change', (event) => {
                this.trigger('countrychange', this.el.value);
            });
        }

    }


    class CitySelectionWidget extends View {

        constructor (selector) {
            super(selector);

            this.el.addEventListener('change', (event) => {
                this.trigger('citychange', this.el.value);
            });
        }

        async updateByCountryID (countryID) {
            let url = Weather.URL.cityListByCountryID(countryID);
            let cities = await fetch(url);
            cities = await cities.json();

            this._replaceCities(cities);
    
            // need to trigger the event manually
            this.trigger('citychange', this.el.value);
        }

        _replaceCities (cities) {
            // remove all children first
            while (this.el.firstChild) {
                this.el.removeChild(this.el.firstChild);
            }
            // create new children
            for (let {id, name} of cities) {
                let o = document.createElement('option');
                o.value = id;
                o.textContent = name;
                this.el.appendChild(o);
            }
        }

    }


    class WeatherWidget extends View {

        constructor (selector) {
            super(selector);

            this._icon = this.el.querySelector('.display-icon');
            this._temp = this.el.querySelector('.display-temp');
            this._iconID = 0;
        }

        async updateByCityID (cityID) {
            let url = Weather.URL.weatherByCityID(cityID);
            let weather = await fetch(url);
            weather = await weather.json();
    
            this._iconID = weather.icon;
    
            this._icon.className = this._getIconClassName(weather.icon);
            this._temp.textContent = weather.temp;

            // we are ready to show this widget
            this.show();
    
            this.trigger('weatherchange', this.iconID);
        }

        get iconID () {
            return this._iconID;
        }

        _getIconClassName (iconID) {
            let icon = Weather.Icon[iconID].icon;
    
            // If we are not in the ranges mentioned above, add a day/night prefix.
            if (!(iconID > 699 && iconID < 800) && !(iconID > 899 && iconID < 1000)) {
                icon = 'day-' + icon;
            }
    
            return `wi wi-${icon}`;
        }

    }


    class OtherWidget extends View {

        constructor (selector) {
            super(selector);

            this._city = this.el.querySelector('.display-other-city');
        }

        async findSameCity (iconID) {
            let url = Weather.URL.otherByIconID(iconID);
            let data = await fetch(url);
            data = await data.json();
    
            // no data
            if (!data) {
                return;
            }
    
            // user changed again
            if (iconID !== data.icon) {
                return;
            }
    
            this._city.textContent = data.name;
    
            // reveal the widget
            this.show();
        }

    }


    window.Weather = Object.assign(Weather, {
        CountrySelectionWidget,
        CitySelectionWidget,
        WeatherWidget,
        OtherWidget,
    });

})();
