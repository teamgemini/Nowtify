from django.db import models


class Meta:
    db_table = 'Nowtify'


class User(models.Model):
    pass


class Wearable(models.Model):
    name = models.CharField(max_length=30, primary_key=True)
    remarks = models.CharField(max_length=300)

    class Meta:
        db_table = "NowtifyWeb_wearable"

    pass


class Wearable_Usage(models.Model):
    wearable_name = models.ForeignKey(Wearable, on_delete=models.CASCADE)
    used = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now_add=True, auto_now=False)

    class Meta:
        db_table = "NowtifyWeb_wearable_usage"


class Wearable_Battery(models.Model):
    wearable_name = models.ForeignKey(Wearable, on_delete=models.CASCADE)
    battery = models.IntegerField(default=0)
    updated = models.DateTimeField(auto_now_add=True, auto_now=False)

    class Meta:
        db_table = "NowtifyWeb_wearable_battery"


class Sensor(models.Model):
    name = models.CharField(max_length=30, primary_key=True)
    remarks = models.CharField(max_length=300)

    class Meta:
        db_table = "NowtifyWeb_sensor"


class Sensor_Usage(models.Model):
    sensor_name = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    used = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now_add=True, auto_now=False)

    class Meta:
        db_table = "NowtifyWeb_sensor_usage"


class Sensor_Battery(models.Model):
    sensor_name = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    battery = models.IntegerField(default=0)
    updated = models.DateTimeField(auto_now_add=True, auto_now=False)

    class Meta:
        db_table = "NowtifyWeb_sensor_battery"
