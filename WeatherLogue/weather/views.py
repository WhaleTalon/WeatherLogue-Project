from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages

from requests import get as APIGet
from datetime import datetime
import decimal

from weather.models import APIKeys, Location, WeatherLog

def get_default_location():
    """Provides a default address to ensure data is available to render in
    all views.
    """
    default_location = {
        'place_name': "Pretoria, Gauteng, South Africa",
        'place_type': "place",
        'latitude': 28.154,
        'longitude': -25.7484
    }
    return default_location

def get_direction(degrees):
    """Translates wind degrees into compass directions. 
    In case of failure to translate, defaults to the numerical degrees 
    in the format 'xxx Deg'.
    """

    try:
        deg = int(degrees)

        if deg < 0 or deg > 360:
            return degrees + " Deg"
        elif deg < 33.75:
            return "NNE"
        elif deg < 56.25:
            return "NE"
        elif deg < 78.75:
            return "ENE"
        elif deg < 101.25:
            return "E"
        elif deg < 123.75:
            return "ESE"
        elif deg < 146.25:
            return "SE"
        elif deg < 168.75:
            return "SSE"
        elif deg < 191.25:
            return "S"
        elif deg < 213.75:
            return "SSW"
        elif deg < 236.25:
            return "SW"
        elif deg < 258.75:
            return "WSW"
        elif deg < 281.25:
            return "W"
        elif deg < 303.75:
            return "WNW"
        elif deg < 326.25:
            return "NW"
        elif deg < 348.75:
            return "NNW"
        else:
            return "N"
    
    except:
        return degrees + " Deg"

def extract_location(request):
    """Extract location parameters from the request object. 
    Raise an exception if parameters are incomplete.
    """

    if request.method == "GET":
        place_name = request.GET.get("place_name", "")
        place_type = request.GET.get("place_type", "")
        latitude = request.GET.get("latitude", "")
        longitude = request.GET.get("longitude", "")

    elif request.method == "POST":
        place_name = request.POST.get("place_name", "")
        place_type = request.POST.get("place_type", "")
        latitude = request.POST.get("latitude", "")
        longitude = request.POST.get("longitude", "")

    if place_name and place_type and latitude and longitude:
        return {
            'place_name': place_name,
            'place_type': place_type,
            'latitude': latitude,
            'longitude': longitude
        }

    else:
        raise Exception(f"Location data supplied is incomplete.")

def get_API_key(service_name):
    """Return the key for the desired API service (if available)"""

    try:
        key = APIKeys.objects.get(service_name=service_name)
        return key.key
    except:
        return ""

def find_location(request):
    """Lookup places and GPS coordinates for search criteria embedded in the request
    object. Return the result as a list object embedded in a json response."""

    try:
        place_name = request.GET.get("place_name", "")
        place_type = request.GET.get("place_type", "")
        if (not place_name or not place_type):
            raise Exception("Location search parameters were not supplied.")

        key = get_API_key("mapbox")
        if not key:
            raise Exception("API Key could not be found.")

        APIUrl = "https://api.mapbox.com/geocoding/v5/mapbox.places/{}.json?{}&types={}&access_token={}"
        APIUrl = APIUrl.format(place_name, "autocomplete=False", place_type, key)

        response = APIGet(APIUrl)
        data = response.json()
        places = data["features"] 
        locations = []
        for place in places:
            locations.append({
                'place_name': place["place_name"],
                'place_type': place["place_type"][0],
                'latitude': place["center"][0],
                'longitude': place["center"][1]
            })
            
        json = {"locations": locations}
        return JsonResponse(json)

    except Exception as err:
        print(f"Location search error:\n{str(err)}")

def obtain_location(request):
    """Extract the place parameters provided in the request object.
    Return the model class that matching the paramters, insert a new 
    entry in the DB if no match is found. 

    Raise an exception if unsuccessful.
    """
    context = extract_location(request)

    try:
        location_result = Location.objects.get(
            place_name=context["place_name"], 
            place_type=context["place_type"],
            latitude = context["latitude"],
            longitude = context["longitude"]
            )
        return location_result
    
    except Location.DoesNotExist:
        new_location = Location(
            place_name=context["place_name"], 
            place_type=context["place_type"],
            latitude = context["latitude"],
            longitude = context["longitude"]
            )
        new_location.save()
        return new_location

def log_weather(request, the_location):
    """Save the weather information embedded in the request
    for the location provided.

    Raise an exception if not successfull
    """

    dt = request.POST.get("log_date", "")
    if dt:
        log_date = datetime.fromtimestamp(int(dt))
    else:
        raise Exception("Log date not supplied.")

    temp = decimal.Decimal(request.POST.get("temp", ""))
    feels_like = decimal.Decimal(request.POST.get("feels_like", ""))
    temp_min = decimal.Decimal(request.POST.get("temp_min", ""))
    temp_max = decimal.Decimal(request.POST.get("temp_max", ""))

    main = request.POST.get("main", "")
    description = request.POST.get("description", "")
    icon = request.POST.get("icon", "")

    pressure = int(request.POST.get("pressure", ""))
    humidity = int(request.POST.get("humidity", ""))

    wind_speed = float(request.POST.get("wind_speed", ""))
    wind_degrees = float(request.POST.get("wind_deg", ""))

    weather_log = WeatherLog(
        location = the_location,
        log_date = log_date,
        main = main,
        description = description,
        icon = icon,
        temp = temp,
        feels_like = feels_like,
        temp_min = temp_min,
        temp_max = temp_max,
        pressure = pressure,
        humidity = humidity,
        wind_speed = wind_speed,
        wind_degrees = wind_degrees
    )
    weather_log.save()

def location(request):
    """Render the location page when requested."""

    try:
        context = extract_location(request)
    except Exception as err:
        context = get_default_location()

    context['active_page'] = "location"
    return render(request, "weather/location.html", context)   

def get_weather(latitude, longitude):
    """Query the openweathermap API for the current weather at the
    given GPS coordinates. 

    Return the result as a python dict, else raise an exception if 
    unsuccessful.
    """
    try:
        key = get_API_key("openweathermap")
        if not key:
            raise Exception("API Key could not be found.")

        APIUrl = "https://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&units=metric&appid={}"
        APIUrl =  APIUrl.format(latitude, longitude, key)

        response = APIGet(APIUrl)
        data = response.json()
        weather = {}
        weather["main"] = data["weather"][0]["main"]
        weather["description"] = data["weather"][0]["description"]
        weather["icon"] = data["weather"][0]["icon"]
        weather["temp"] = data["main"]["temp"]
        weather["feels_like"] = data["main"]["feels_like"]
        weather["temp_min"] = data["main"]["temp_min"]
        weather["temp_max"] = data["main"]["temp_max"]
        weather["pressure"] = data["main"]["pressure"]
        weather["humidity"] = data["main"]["humidity"]
        weather["wind_speed"] = data["wind"]["speed"]
        weather["wind_deg"] = data["wind"]["deg"]
        weather["wind_direction"] = get_direction(data["wind"]["deg"])
        weather["dt"] =  datetime.fromtimestamp(data["dt"])
        weather["log_date"] = data["dt"]

        return weather

    except Exception as err:
        print(f"Weather get error:\n{str(err)}")
        return {}

def get_forecast(latitude, longitude):
    """Query the openweathermap API for the hourly weather forecast
    at the given GPS coordinates. 
    
    Return the result as a python list, else raise an exception if 
    unsuccessful.
    """
    try:
        key = get_API_key("openweathermap")
        if not key:
            raise Exception("API Key could not be found.")

        APIUrl = "https://api.openweathermap.org/data/2.5/forecast?lat={}&lon={}&units=metric&appid={}"
        APIUrl = APIUrl.format(latitude, longitude, key)

        response = APIGet(APIUrl)
        data_list = response.json()["list"]
        forecast = []
        for data in data_list:
            weather = {}
            weather["main"] = data["weather"][0]["main"]
            weather["description"] = data["weather"][0]["description"]
            weather["icon"] = data["weather"][0]["icon"]
            weather["temp"] = data["main"]["temp"]
            weather["feels_like"] = data["main"]["feels_like"]
            weather["pressure"] = data["main"]["pressure"]
            weather["humidity"] = data["main"]["humidity"]
            weather["wind_speed"] = data["wind"]["speed"]
            weather["wind_deg"] = data["wind"]["deg"]
            weather["wind_direction"] = get_direction(data["wind"]["deg"])
            weather["dt"] =  datetime.fromtimestamp(data["dt"])
            forecast.append(weather)
        return forecast

    except Exception as err:
        print(f"Forecast get error:\n{str(err)}")
        return []

def forecast(request):
    """
    GET request = Render the forecast view with current and hourly
    weather information.

    POST request = Save the returned weather in the DB (the location
    as well if needed) and redirect to the history view to show all
    entries for the currently selected location. 
    """
    if request.method == "GET":
        try:
            context = extract_location(request)
        except Exception as err:
            context = get_default_location()
            messages.add_message(request, messages.ERROR, f"Location extraction error:\n{str(err)}")
            
    elif request.method == "POST":
        try:
            location_result = obtain_location(request)
        
        except Exception as err:
            context = get_default_location()
            messages.add_message(request, messages.ERROR, f"Location error:\n{str(err)}")

        else:
            try:
                log_weather(request, location_result)

            except Exception as err:
                context = get_default_location()
                messages.add_message(request, messages.ERROR, f"The weather could not be saved.\n{str(err)}")
                
            else:
                return HttpResponseRedirect(reverse("weather:location_history", args=(location_result.id,)))


    context["weather"] = get_weather(context['latitude'], context['longitude'])
    context["forecast"] = get_forecast(context['latitude'], context['longitude'])

    context['active_page'] = "forecast"
    return render(request, "weather/forecast.html", context)
        
def location_history(request, location_id):
    """Render the historical entries for the specified location.
    
    Fallback to the default location view if unsuccessfull.
    """

    try:
        location_result = Location.objects.get(id = location_id)
    
    except Exception as err:
        messages.add_message(request, messages.ERROR, f"The location could not be found.\n{str(err)}")
        return HttpResponseRedirect(reverse("weather:location"))

    else:
        try:
            weatherlog_results = WeatherLog.objects.filter(location__pk = location_id).values()
            
        except Exception as err:
            messages.add_message(request, messages.ERROR, f"Weather results could not be found.\n{str(err)}")
            return HttpResponseRedirect(reverse("weather:location"))

        else:
            context = {}
            context["weatherlog"] = weatherlog_results 
            context["place_name"] = location_result.place_name
            context["place_type"] = location_result.place_type
            context["latitude"] = location_result.latitude
            context["longitude"] = location_result.longitude
            context['active_page'] = "history"
            return render(request, "weather/history.html", context)

def history(request):
    """If the DB contains entries for the location embedded in the request object,
    then redirect to the proper location_history view to display them.
    
    If no entries are found, then redirect to the default location view."""

    try:
        context = extract_location(request)

    except Exception as err:
        messages.add_message(request, messages.ERROR, f"The location could not be extracted.\n{str(err)}")
        return HttpResponseRedirect(reverse("weather:location"))

    else:
        try:
            location_result = Location.objects.get(
                place_name=context["place_name"], 
                place_type=context["place_type"],
                latitude = context["latitude"],
                longitude = context["longitude"]
                )
            location_id = location_result.id

        except Location.DoesNotExist: 
            messages.add_message(request, messages.ERROR, "The location has no weather logs.")
            return HttpResponseRedirect(reverse("weather:location"))

        else:
            return HttpResponseRedirect(reverse("weather:location_history", args=(location_id,)))