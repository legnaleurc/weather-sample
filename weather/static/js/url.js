(function () {
    'use strict';

    const Weather = window.Weather || {};

    // in case we are behind nginx
    const prefix = '';


    const URL = {

        cityListByCountryID (countryID) {
            return `${prefix}/api/v1/country/${countryID}/city`;
        },

        weatherByCityID (cityID) {
            return `${prefix}/api/v1/weather/${cityID}`;
        },

        otherByIconID (iconID) {
            return `${prefix}/api/v1/other/${iconID}`;
        },

    };


    window.Weather = Object.assign(Weather, {
      URL,
    });

})();
