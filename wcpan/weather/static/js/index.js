(function () {
    'use strict';

    const selectionCountry = document.querySelector('#selection-country');
    const selectionCity = document.querySelector('#selection-city');
    const displayIcon = document.querySelector('#display-icon');
    const displayTemp = document.querySelector('#display-temp');
    const displayOtherCity = document.querySelector('#display-other-city');
    const weatherWidget = document.querySelector('.weather-widget');
    const otherWidget = document.querySelector('.other-widget');
    let currentIcon = 0;


    async function main () {
        selectionCountry.addEventListener('change', async (event) => {
            await updateCities();
        });
        selectionCity.addEventListener('change', async (event) => {
            await updateWeather();
        });

        // trigger manually
        await updateCities();

        while (true) {
            await wait(5000);
            await findSameCity();
        }
    }


    async function updateCities () {
        let countryID = selectionCountry.value;
        let cities = await fetch(`/api/v1/country/${countryID}/city`);
        cities = await cities.json();

        while (selectionCity.firstChild) {
            selectionCity.removeChild(selectionCity.firstChild);
        }
        for (let {id, name} of cities) {
            let o = document.createElement('option');
            o.value = id;
            o.textContent = name;
            selectionCity.appendChild(o);
        }

        // need to trigger the update manually
        await updateWeather();
        // reveal the widget
        weatherWidget.classList.remove('hidden');
    }


    async function updateWeather () {
        let cityID = selectionCity.value;
        let weather = await fetch(`/api/v1/weather/${cityID}`);
        weather = await weather.json();

        currentIcon = weather.icon;

        displayIcon.className = getIconClassName(weather.icon);
        displayTemp.textContent = weather.temp;

        // the icon may changed
        otherWidget.classList.add('hidden');
    }


    function getIconClassName (iconID) {
        let icon = window.__WeatherIcon__[iconID].icon;

        // If we are not in the ranges mentioned above, add a day/night prefix.
        if (!(iconID > 699 && iconID < 800) && !(iconID > 899 && iconID < 1000)) {
            icon = 'day-' + icon;
        }

        return `wi wi-${icon}`;
    }


    async function findSameCity () {
        let data = await fetch(`/api/v1/other/${currentIcon}`);
        data = await data.json();

        // no data
        if (!data) {
            return;
        }

        // user changed again
        if (currentIcon !== data.icon) {
            return;
        }

        displayOtherCity.textContent = data.name;

        // reveal the widget
        otherWidget.classList.remove('hidden');
    }


    function wait (msDelay) {
        return new Promise((resolve) => {
            setTimeout(resolve, msDelay);
        });
    }


    main().catch((e) => {
        console.error(e);
    });

})();
