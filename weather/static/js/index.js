(function () {
    'use strict';

    const Weather = window.Weather || {};


    async function main () {
        const selectionCountry = new Weather.CountrySelectionWidget('#selection-country');
        const selectionCity = new Weather.CitySelectionWidget('#selection-city');
        const weatherWidget = new Weather.WeatherWidget('.weather-widget');
        const otherWidget = new Weather.OtherWidget('.other-widget');

        selectionCountry.addEventListener('countrychange', async (event) => {
            await selectionCity.updateByCountryID(event.detail);
        });

        selectionCity.addEventListener('citychange', async (event) => {
            await weatherWidget.updateByCityID(event.detail);
        });

        weatherWidget.addEventListener('weatherchange', (event) => {
            otherWidget.hide();
        });

        // on page loaded we have to trigger manually
        selectionCountry.trigger('countrychange', selectionCountry.el.value);

        while (true) {
            await wait(5000);
            await otherWidget.findSameCity(weatherWidget.iconID);
        }
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
