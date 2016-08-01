from django.shortcuts import render
from django.shortcuts import HttpResponseRedirect
from django.shortcuts import redirect
from django.core.context_processors import csrf
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.models import User
from django.db import transaction
from Nowtify.models import Wearable, Wearable_Battery, Wearable_Usage
from Nowtify.models import Sensor, Sensor_Battery, Sensor_Usage


def custom_login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect("dashboard")
    else:
        return login(request)


def login(request):

    if request.user.is_authenticated():
        return HttpResponseRedirect("dashboard")

    return render(request, "login.html", {})


def logout(request):
    auth_logout(request)
    c = {}
    c.update(csrf(request))
    return render(request, "login.html", {})


def authentication(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)

    def errorHandle(error):
        c = {}
        c.update(csrf(request))
        return render(request, 'login.html', {'error': error})


    if user is not None:

        if user.is_active:
            auth_login(request, user)
            c = {}
            c.update(csrf(request))
            return redirect('dashboard')
        else:
            c = {}
            c.update(csrf(request))
            return render(request, "login.html", {})
    elif user is None:
        c = {}
        c.update(csrf(request))
        error = 'Invalid username/password'
        return errorHandle(error)



@login_required(login_url='')
def change_password(request):

    c = {}
    c.update(csrf(request))

    new_password = request.POST['new_password']
    confirm_password = request.POST['confirm_password']

    current_user = request.user
    current_user_id = current_user.get_username()
    current_user_pw = 'admin'
    password = request.POST['current_password']
    #current_user.get_username()

    if confirm_password == new_password and current_user_pw == password:

        u = User.objects.get(username=current_user_id)
        u.set_password(new_password)
        u.save()

        return render(request, 'dashboard.html', {})
    elif current_user_pw != password:
        return render(request, 'settings.html', {'error': 'Current password is wrong'})
    

    else:
        #need Josie and Shawn to add error message instead of redirecting to dashboard page

        return render(request, 'settings.html', {'error': 'Passwords do not match. Please re-enter password' })


@login_required(login_url='')
def index(request):
    return render(request, "index.html")


@login_required(login_url='')
def dashboard(request):

    with transaction.atomic():
        pass

    #wearable1 = Wearable(name="ABC", remarks="Made in Thailand. Please take care of this well.")
    #wearable_battery1 = Wearable_Battery(wearable_name=wearable1, battery=60)
    #wearable_usage1 = Wearable_Usage(wearable_name=wearable1, used=True)
    #wearable1.save()
    #wearable_battery1.save()
    #wearable_usage1.save()


    return render(request, "dashboard.html")


@login_required(login_url='')
def sensor(request):

    # do refer to models.py to see how the data is structured
    sensorUnique = []
    sensorUsage = []
    sensorBattery = []
    sensorLocation = []
    sensorUpdated = []
    sensorData = []

    # get unique sensors
    for instance in Sensor.objects.all():
        sensorUnique.append(instance)

    # there are many rows of data, this code will filter by each unique sensor, arrange from newest to oldest data
    # and get the first one, aka the latest data
    for sensorObject in sensorUnique:
        sensorUsage.append(
            Sensor_Usage.objects.all().filter(sensor_name__exact=sensorObject).order_by('updated').first().used)

        sensorBattery.append(
            Sensor_Battery.objects.all().filter(sensor_name__exact=sensorObject).order_by('updated').first().battery)

        sensorUpdated.append(Sensor_Usage.objects.all().filter(wearable_name__exact=sensorObject).order_by(
            'updated').first().updated)

    # we have yet to put in location feature. This is for future use. For now, I just put Location 1
    for sensorObject in sensorUnique:
        sensorLocation.append(1)

    count = 0
    for sensorObject in sensorUnique:

        if sensorUsage[count]:
            usage = "In Operation"
        else:
            usage = "Not in operation"

        if sensorBattery[count] > 80:
            action = "No action required"
        elif sensorBattery[count] > 50:
            action = "Battery over 50"
        elif sensorBattery[count] > 30:
            action = "Battery over 30"
        else:
            action = "Batter under 30"

            sensorData.append([str(sensorObject.name), usage, "Center " + str(sensorLocation[count]), str(sensorBattery[count]) + "%",action, (str(sensorUpdated[count]))[:19]])
        count += 1

    return render(request, "detectors.html", {'dataSet': sensorData})


@login_required(login_url='')
def alert_band(request):

    wearableUnique = []
    wearableUsage = []
    wearableBattery = []
    wearableLocation = []
    wearableUpdated = []
    wearableData = []

    # get sensor uniquely
    for instance in Wearable.objects.all():
        wearableUnique.append(instance)

    for wearableObject in wearableUnique:
        wearableUsage.append(
            Wearable_Usage.objects.all().filter(wearable_name__exact=wearableObject).order_by('updated').first().used)

        wearableBattery.append(
            Wearable_Battery.objects.all().filter(wearable_name__exact=wearableObject).order_by(
                'updated').first().battery)

        wearableUpdated.append(Wearable_Usage.objects.all().filter(wearable_name__exact=wearableObject).order_by(
                'updated').first().updated)

    for wearableObject in wearableUnique:
        wearableLocation.append(1)

    count = 0
    for wearableObject in wearableUnique:

        if wearableUsage[count]:
            usage = "In Operation"
        else:
            usage = "Not in Operation"

        if wearableBattery[count] > 80:
            action = "No action required"
        elif wearableBattery[count] > 50:
            action = "Battery over 50"
        elif wearableBattery[count] > 30:
            action = "Battery over 30"
        else:
            action = "Battery under 30"

        wearableData.append(
            [str(wearableObject.name), usage, "Center " + str(wearableLocation[count]), str(wearableBattery[count]) + "%",
             action, (str(wearableUpdated[count]))[:19]])
        count += 1

    return render(request, "alert_bands.html", {'dataSet': wearableData})


@login_required(login_url='')
def incident_reporting(request):
    return render(request, "incident_reporting.html")


@login_required(login_url='')
def settings(request):
    return render(request, "settings.html")


@login_required(login_url='')
def alert(request):
    return render(request, "alert.html")


def handler404(request):
    response = render_to_response('404.html', {},
                              context_instance=RequestContext(request))
    response.status_code = 404
    return response
