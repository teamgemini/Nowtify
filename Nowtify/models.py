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


class WearableUsage(models.Model):
    wearable_name = models.ForeignKey(Wearable, on_delete=models.CASCADE)
    used = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now_add=True, auto_now=False)

    class Meta:
        db_table = "NowtifyWeb_wearable_usage"


class WearableBattery(models.Model):
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


class SensorUsage(models.Model):
    sensor_name = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    used = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now_add=True, auto_now=False)

    class Meta:
        db_table = "NowtifyWeb_sensor_usage"


class SensorBattery(models.Model):
    sensor_name = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    battery = models.IntegerField(default=0)
    updated = models.DateTimeField(auto_now_add=True, auto_now=False)

    class Meta:
        db_table = "NowtifyWeb_sensor_battery"


class Detector(models.Model):
    name = models.CharField(max_length=30, primary_key=True)
    remarks = models.CharField(max_length=300)

    class Meta:
        db_table = "NowtifyWeb_detector"


class DetectorUsage(models.Model):
    detector_name = models.ForeignKey(Detector, on_delete=models.CASCADE)
    used = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now_add=True, auto_now=False)

    class Meta:
        db_table = "NowtifyWeb_detector_usage"


class DetectorBattery(models.Model):
    detector_name = models.ForeignKey(Detector, on_delete=models.CASCADE)
    battery = models.IntegerField(default=0)
    updated = models.DateTimeField(auto_now_add=True, auto_now=False)

    class Meta:
        db_table = "NowtifyWeb_detector_battery"


class Alert(models.Model):
    datetime = models.DateTimeField()
    detector = models.OneToOneField(Detector)
    seen = models.BooleanField(default=False)
    wearable = models.ForeignKey(Wearable, null=True, blank=True, default=None)

    class Meta:
        db_table = "NowtifyWeb_alert"


class Assignment(models.Model):
    wearable_name = models.ForeignKey(Wearable, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    update = models.DateTimeField(auto_now_add=True, auto_now=False)

    class Meta:
        db_table = "NowtifyWeb_assignment"