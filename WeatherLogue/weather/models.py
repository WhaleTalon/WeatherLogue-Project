from django.db import models

class Location(models.Model):
    place_name = models.CharField(max_length=250)
    place_type = models.CharField(
        max_length=15,
        choices=(
            ("address", "Address"),
            ("place", "City/Town"),
            ("country", "Country")
        )
    )
    latitude = models.CharField(max_length=15)
    longitude = models.CharField(max_length=15)

    def __str__(self):
        return self.place_name

class WeatherLog(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    log_date = models.DateTimeField("date logged")
    main = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    icon = models.CharField(max_length=5)
    temp = models.DecimalField(max_digits=4, decimal_places=2)
    feels_like = models.DecimalField(max_digits=4, decimal_places=2)
    temp_min = models.DecimalField(max_digits=4, decimal_places=2)
    temp_max = models.DecimalField(max_digits=4, decimal_places=2)
    pressure  = models.PositiveIntegerField()
    humidity = models.PositiveSmallIntegerField()
    wind_speed = models.FloatField()
    wind_degrees = models.FloatField()

    def __str__(self):
        log_datetime = self.log_date.strftime("%m/%d/%Y, %H:%M:%S")
        return f"{log_datetime}: {self.location}" 

class APIKeys(models.Model):
    service_name = models.CharField(max_length=50)
    key = models.CharField(max_length=250)

    def __str__(self):
        return self.service_name