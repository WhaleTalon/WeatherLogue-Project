# WeatherLogue Project

## Introduction

This project is a website that allows users to view current weather and hourly forecasted weather for any location. It also allows timestamped weather information to be logged for a given location.

The backend is created with Python and the Django framework, using a MySQL database to store weather data.

The frontend employs JavaScript to facilitate the retrieval of GPS Coordinates for place names.

GPS Coordinates are obtained via the MapBox API (www.mapbox.com), and weather data is obtained via the Openweathermap API (www.openweathermap.org).

## Web Pages / Views

The web site provides 3 web pages as follows:

### Location Page

This web page will initially display a default location. The user is presented with a "Change" button that displays a modal "Find location" dialog.

This dialog allows the user to search for a location based on some or all of Address, City/Town and Country options. The "Find" button will search for locations based on the criteria entered, and display up to 5 matches. The user should select the most appropriate place name, and click "Accept".

Once a location is accepted, it becomes the current location that all actions are based upon. Specifically, the user may navigate to the Forecast page or History Page (provided there is historical data available for the current location).

### Forecast Page

This web page will display the current weather data for the current location, as well as a hourly forecast.

Clicking the "Save" button will record the timestamped current weather data for the current location. If the operation is successful, the user is navigated to the History Page where the newly saved weather data will reflect.

Clicking the "Change" button will navigate the user to the Location Page where a new location may be specified.

### History Page

The history page will display records saved for the current location. If no records exist for the current location, the user is automatically redirected to the Location Page.

## TO DO

The following are the most critical next steps in the development of the WeatherLogue web site.

1. There are currently no UnitTests/TestCases written for the site, nor has structured testing been done.
2. It was intended for the user's IP Address to serve as a guide to select a good default location. This functionality should be added to the get_default_location() function in the weather/views.py module.
3. Type hinting should be added to the views.py module.
4. The location.html template file should add a geographical map of the current location. A place holder (DIV element) is currently displayed.
5. Support for messages is currently limited to rudimentary error messages. This can me made much more insightful and reactive.
6. The hourly forecast is not visually appealing or user friendly as a vertically scrolling table.
7. The overall site aesthetics needs a lot of work.
8. The site leverages bootstrap for responsive design, but the layout can be much improved.  

