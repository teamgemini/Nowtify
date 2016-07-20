from django.db import models

class User(models.Model):
    pass

class Wearable(models.Model):
    name = models.CharField(max_length=30, primary_key=True)
    remarks = models.CharField(max_length=300)
    pass

class Wearable_Usage(models.Model):
    wearable_name = models.ForeignKey(Wearable, on_delete=models.CASCADE)
    used = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now_add=True, auto_now=False)

class Wearable_Battery(models.Model):
    wearable_name = models.ForeignKey(Wearable, on_delete=models.CASCADE)
    battery = models.IntegerField(default=0)
    updated = models.DateTimeField(auto_now_add=True, auto_now=False)

class Sensor(models.Model):
    name = models.CharField(max_length=30, primary_key=True)
    remarks = models.CharField(max_length=300)
    pass

class Sensor_Usage(models.Model):
    sensor_name = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    used = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now_add=True, auto_now=False)

class Sensor_Battery(models.Model):
    sensor_name = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    battery = models.IntegerField(default=0)
    updated = models.DateTimeField(auto_now_add=True, auto_now=False)