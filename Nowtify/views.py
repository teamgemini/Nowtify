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
from Nowtify.models import Wearable, WearableBattery, WearableUsage
from Nowtify.models import Detector, DetectorBattery, DetectorUsage
from Nowtify.models import Alert, Assignment
from operator import itemgetter
from datetime import datetime,timedelta


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

    current_user = request.user
    current_user_id = current_user.get_username()
    current_user_pw = request.POST['current_password']
    new_password = request.POST['new_password']
    confirm_password = request.POST['confirm_password']

    user = authenticate(username=current_user_id, password=current_user_pw)

    if user is not None and new_password == confirm_password:
        # change pw successfully, redirect back to dashboard
        u = User.objects.get(username=current_user_id)
        u.set_password(new_password)
        u.save()
        return render(request, 'dashboard.html', {})

    elif user is None:
        return render(request, 'settings.html', {'error': 'Incorrect current password. Please re-enter password.'})

    else:
        return render(request, 'settings.html', {'error': 'Passwords do not match. Please re-enter password.'})


@login_required(login_url='')
def index(request):
    return render(request, "index.html")


@login_required(login_url='')
def dashboard(request):
    #
    #
    # Detector.objects.all().delete()
    # DetectorUsage.objects.all().delete()
    # DetectorBattery.objects.all().delete()
    #
    # Wearable.objects.all().delete()
    # WearableUsage.objects.all().delete()
    # WearableBattery.objects.all().delete()
    #
    # Alert.objects.all().delete()
    #
    #
    # #insert fake data
    # wearable1 = Wearable.objects.create(name="wearable1",remarks="superrr1")
    # wearable1Use= WearableUsage.objects.create(wearable_name=wearable1,used=True)
    # wearable1Battery = WearableBattery.objects.create(wearable_name=wearable1,battery=10) #ON  LOW BATT
    #
    # wearable2 = Wearable.objects.create(name="wearable2",remarks="superrr2")
    # wearable2Use= WearableUsage.objects.create(wearable_name=wearable2,used=True)
    # wearable2Battery = WearableBattery.objects.create(wearable_name=wearable2,battery=50) #ON
    #
    # wearable3 = Wearable.objects.create(name="wearable3",remarks="superrr3")
    # wearable3Use= WearableUsage.objects.create(wearable_name=wearable3,used=False)
    # wearable3Battery = WearableBattery.objects.create(wearable_name=wearable3,battery=50) #OFF
    #
    # wearable4 = Wearable.objects.create(name="wearable4",remarks="superrr4")
    # wearable4Use= WearableUsage.objects.create(wearable_name=wearable4,used=False)
    # wearable4Battery = WearableBattery.objects.create(wearable_name=wearable4,battery=15) #OFF LOW BATT
    #
    # detector1 = Detector.objects.create(name="detector1",remarks="ultraaaa1")
    # detector1Use= DetectorUsage.objects.create(detector_name=detector1,used=True)
    # detector1Battery = DetectorBattery.objects.create(detector_name=detector1,battery=10)  #ON ,low batt
    #
    # detector2 = Detector.objects.create(name="detector2",remarks="ultraaaa2")
    # detector2Use= DetectorUsage.objects.create(detector_name=detector2,used=True)
    # detector2Battery = DetectorBattery.objects.create(detector_name=detector2,battery=50) #ON
    #
    # detector3 = Detector.objects.create(name="detector3",remarks="ultraaaa3")
    # detector3Use= DetectorUsage.objects.create(detector_name=detector3,used=False)
    # detector3Battery = DetectorBattery.objects.create(detector_name=detector3,battery=50) #OFF
    #
    # detector4 = Detector.objects.create(name="detector4",remarks="ultraaaa4")
    # detector4Use= DetectorUsage.objects.create(detector_name=detector4,used=False)
    # detector4Battery = DetectorBattery.objects.create(detector_name=detector4,battery=15) #OFF ,low batt
    #
    # alert1 = Alert.objects.create(detector=detector1,wearable=wearable1,seen=False) #activated
    # alert2 = Alert.objects.create(detector=detector2,wearable=wearable2,seen=True) #acknowledged


    masterList= []

    detectorUsageUnique = []
    detectorUsage = []


    detectorBatteryUnique = []
    detectorBattery = []

    wearableUsageUnique = []
    wearableUsage = []


    wearableBatteryUnique = []
    wearableBattery = []


    alertUnique= []
    alertList= []

    startOfYtd = (datetime.now()- timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0) #yesterday's 00:00:00

#DetectorOnOff
    detectorCounter = 0
    for instanceDetector in Detector.objects.all():
        detectorUsageUnique.append(instanceDetector)
    # there are many rows of data, this code will filter by each unique sensor, arrange from newest to oldest data
    # and get the first one, aka the latest data


    for detectorObject in detectorUsageUnique:
        detectorUsage.append(DetectorUsage.objects.all().filter(detector_name__exact=detectorObject,updated__gte=startOfYtd).order_by('updated').first()) # order by time only for ON OFF

    for instance in detectorUsage:
        messageType=""
        message=""
        time=None


        if instance.used == True:
            messageType="Detector"
            message=str(instance.detector_name.name) + " in Center 1 has been Switched ON"

            if(str(instance.updated.date()) == str(datetime.today().date())):
                time = "Today " + str(instance.updated)[11:19]
            else:
                time=datetime.strptime(str(instance.updated)[:19],'%Y-%m-%d %H:%M:%S').strftime("%d-%m-%Y %H:%M:%S")
            detectorCounter += 1

            masterList.append([messageType,message,time])

        if instance.used == False:
            messageType="Detector"
            message=str(instance.detector_name.name) + " in Center 1 has been Switched OFF"

            if(str(instance.updated.date()) == str(datetime.today().date())):
                time = "Today " + str(instance.updated)[11:19]
            else:
                time=datetime.strptime(str(instance.updated)[:19],'%Y-%m-%d %H:%M:%S').strftime("%d-%m-%Y %H:%M:%S")
            masterList.append([messageType,message,time])





#DetectorBattery
    for instanceDetector in Detector.objects.all():
        detectorBatteryUnique.append(instanceDetector)
    # there are many rows of data, this code will filter by each unique sensor, arrange from newest to oldest data
    # and get the first one, aka the latest data


    for detectorObject in detectorBatteryUnique: #take all sensors
        detectorBattery.append(DetectorBattery.objects.all().filter(detector_name__exact=detectorObject,updated__gte=startOfYtd).order_by('updated').first())
    #take only sensorBattery objects, filter by sensor name to prevent repeats, filer by condition, order by datetime,take latest
    for instance in detectorBattery:

        messageType=""
        message=""
        time=None

        if(instance.battery)<= 30:
            messageType="Detector"
            message=str(instance.detector_name.name) + " in Center 1 is below 30% Battery, Recharge Required!"

            if(str(instance.updated.date()) == str(datetime.today().date())):
                time = "Today " + str(instance.updated)[11:19]
            else:
                time=datetime.strptime(str(instance.updated)[:19],'%Y-%m-%d %H:%M:%S').strftime("%d-%m-%Y %H:%M:%S")

            masterList.append([messageType,message,time])




#WearableOnOff
    wearableCounter = 0

    for instanceWearable in Wearable.objects.all():
        wearableUsageUnique.append(instanceWearable)
    # there are many rows of data, this code will filter by each unique wearable, arrange from newest to oldest data
    # and get the first one, aka the latest data


    for wearableObject in wearableUsageUnique:
        wearableUsage.append(WearableUsage.objects.all().filter(wearable_name__exact=wearableObject,updated__gte=startOfYtd).order_by('updated').first()) # order by time only for ON OFF

    for instance in wearableUsage:
        messageType=""
        message=""
        time=None

        if instance.used == True:
            messageType="Wearable"
            message=str(instance.wearable_name.name) + " in Center 1 has been Switched ON"
            if(str(instance.updated.date()) == str(datetime.today().date())):
                time = "Today " + str(instance.updated)[11:19]
            else:
                time=datetime.strptime(str(instance.updated)[:19],'%Y-%m-%d %H:%M:%S').strftime("%d-%m-%Y %H:%M:%S")
            wearableCounter += 1

            masterList.append([messageType,message,time])

        if instance.used == False:
            messageType="Wearable"
            message=str(instance.wearable_name.name) + " in Center 1 has been Switched OFF"

            if(str(instance.updated.date()) == str(datetime.today().date())):
                time = "Today " + str(instance.updated)[11:19]
            else:
                time=datetime.strptime(str(instance.updated)[:19],'%Y-%m-%d %H:%M:%S').strftime("%d-%m-%Y %H:%M:%S")

            masterList.append([messageType,message,time])



#WearableBattery
    for instanceWearable in Wearable.objects.all():
        wearableBatteryUnique.append(instanceWearable)
    # there are many rows of data, this code will filter by each unique sensor, arrange from newest to oldest data
    # and get the first one, aka the latest data


    for wearableObject in wearableBatteryUnique: #take all sensors
        wearableBattery.append(WearableBattery.objects.all().filter(wearable_name__exact=wearableObject,updated__gte=startOfYtd).order_by('updated').first())
    #take only sensorBattery objects, filter by sensor name to prevent repeats, filer by condition, order by datetime, take latest
    for instance in wearableBattery:

        messageType=""
        message=""
        time=None

        if(instance.battery)<= 30:
            messageType="Wearable"
            message=(str(instance.wearable_name.name)) + " in Center 1 is below 30% Battery, Recharge Required!"

            if(str(instance.updated.date()) == str(datetime.today().date())):
                time = "Today " + str(instance.updated)[11:19]
            else:
                time=datetime.strptime(str(instance.updated)[:19],'%Y-%m-%d %H:%M:%S').strftime("%d-%m-%Y %H:%M:%S")

            masterList.append([messageType,message,time])


# AlertActivated and Deactivated  #Acknowledgement might be removed
    alertCounter = 0

    for instanceAlert in Alert.objects.all():
        alertUnique.append(instanceAlert)
    # there are many rows of data, this code will filter by each unique alert, arrange from newest to oldest data
    # and get the first one, aka the latest data


    for alertObject in alertUnique: #take all sensors

            alertList.append(Alert.objects.all().filter(detector__exact=alertObject.detector,datetime__gte=startOfYtd).order_by('datetime').first())
    # take only sensorBattery objects, filter by sensor name to prevent repeats, filer by condition, order by datetime,take latest
    for instance in alertList:

        messageType=""
        message=""
        time=None

        if(instance.seen==False):
            messageType="Alert"
            message="Alert Activated in Center 1! Detector "+ str(instance.detector.name)

            if(str(instance.datetime.date()) == str(datetime.today().date())):
                time = "Today " + str(instance.datetime)[11:19]

                alertCounter += 1

            else:
                time=datetime.strptime(str(instance.datetime)[:19],'%Y-%m-%d %H:%M:%S').strftime("%d-%m-%Y %H:%M:%S")

            masterList.append([messageType,message,time])

        if(instance.seen==True):
            messageType="Alert"
            message="Alert Acknowledged in Center 1! Alert Band "+ str(instance.wearable.name) #ack might not be implemented

            if(str(instance.datetime.date()) == str(datetime.today().date())):
                time = "Today " + str(instance.datetime)[11:19]
            else:
                time=datetime.strptime(str(instance.datetime)[:19],'%Y-%m-%d %H:%M:%S').strftime("%d-%m-%Y %H:%M:%S")

            masterList.append([messageType,message,time])


    #sort by time
    newsFeedList = sorted(masterList, key=itemgetter(2))

    print(alertCounter)
    print(detectorCounter)
    print(wearableCounter)
    return render(request, "dashboard.html",{'dataSet': newsFeedList, 'alertCounter': alertCounter, 'detectorCounter':detectorCounter,'wearableCounter': wearableCounter})



@login_required(login_url='')
def sensor(request):
    # do refer to models.py to see how the data is structured
    detectorUnique = []
    detectorUsage = []
    detectorBattery = []
    detectorLocation = []
    detectorUpdated = []
    detectorData = []

    # get unique sensors
    for instance in Detector.objects.all():
        detectorUnique.append(instance)

    # there are many rows of data, this code will filter by each unique sensor, arrange from newest to oldest data
    # and get the first one, aka the latest data
    for detectorObject in detectorUnique:
        detectorUsage.append(
            DetectorUsage.objects.all().filter(sensor_name__exact=detectorObject).order_by('updated').first().used)

        detectorBattery.append(
            DetectorBattery.objects.all().filter(sensor_name__exact=detectorObject).order_by('updated').first().battery)

        detectorUpdated.append(DetectorUsage.objects.all().filter(wearable_name__exact=detectorObject).order_by(
            'updated').first().updated)

    # we have yet to put in location feature. This is for future use. For now, I just put Location 1
    for detectorObject in detectorUnique:
        detectorLocation.append(1)

    # count is required to get the index of the sensors in the list
    count = 0
    for detectorObject in detectorUnique:

        if detectorUsage[count]:
            usage = "In Operation"
        else:
            usage = "Not in operation"

        if detectorBattery[count] > 80:
            action = "No action required"
        elif detectorBattery[count] > 50:
            action = "Battery over 50"
        elif detectorBattery[count] > 30:
            action = "Battery over 30"
        else:
            action = "Battery under 30"

            detectorData.append(
                [str(detectorObject.name), usage, "Center " + str(detectorLocation[count]), str(detectorBattery[count]) + "%",
                 action, (str(detectorUpdated[count]))[:19]])
        count += 1

    return render(request, "detectors.html", {'dataSet': detectorData})


@login_required(login_url='')
def alert_band(request):
    wearableUnique = []
    wearableAssignment = []
    wearableUsage = []
    wearableBattery = []
    wearableLocation = []
    wearableUpdated = []
    wearableData = []


    # get sensor uniquely
    for instance in Wearable.objects.all():
        wearableUnique.append(instance)

    for wearableObject in wearableUnique:

        if Assignment.objects.all().filter(wearable_name__exact=wearableObject).exists():
            wearableAssignment.append(
                Assignment.objects.all().filter(wearable_name__exact=wearableObject).first().name
            )
        else:
            wearableAssignment.append("Not Assigned")

        wearableUsage.append(
            WearableUsage.objects.all().filter(wearable_name__exact=wearableObject).order_by('updated').first().used)

        wearableBattery.append(
            WearableBattery.objects.all().filter(wearable_name__exact=wearableObject).order_by(
                'updated').first().battery)

        wearableUpdated.append(WearableUsage.objects.all().filter(wearable_name__exact=wearableObject).order_by(
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
            [str(wearableObject.name), str(wearableAssignment[count]), usage, "Center " + str(wearableLocation[count]),
             str(wearableBattery[count]) + "%",
             action, (str(wearableUpdated[count]))[:19]])
        count += 1

# --------------------

    wearableAssignment = []

    for instance in wearableUnique:
        instanceName = str(instance.name)
        if Assignment.objects.all().filter(wearable_name__exact=instance).exists():
            instanceAssignee = str(Assignment.objects.all().filter(wearable_name__exact=instance).first().name)
        else:
            instanceAssignee = "Not Assigned"
        wearableAssignment.append([instanceName,instanceAssignee])

    return render(request, "alert_bands.html", {'dataSet': wearableData, 'wearableNames': wearableAssignment})


@login_required(login_url='')
def update_assignment(request):
    wearableName = request.POST['wearableName']
    assignee = request.POST['assignee']

    wearableObject = Wearable.objects.all().filter(name__exact=wearableName).first()

    if Assignment.objects.all().filter(wearable_name__exact=wearableObject).exists():
        assignment = Assignment.objects.all().filter(wearable_name__exact=wearableObject).first()
        assignment.name = assignee
        assignment.save(update_fields=['name'])
    else:
        assignment = Assignment(wearable_name=wearableObject, name=assignee)
        assignment.save()

#------------------------------

    wearableUnique = []
    wearableAssignment = []
    wearableUsage = []
    wearableBattery = []
    wearableLocation = []
    wearableUpdated = []
    wearableData = []

    # get sensor uniquely
    for instance in Wearable.objects.all():
        wearableUnique.append(instance)

    for wearableObject in wearableUnique:

        if Assignment.objects.all().filter(wearable_name__exact=wearableObject).exists():
            wearableAssignment.append(
                str(Assignment.objects.all().filter(wearable_name__exact=wearableObject).first().name)
            )
        else:
            wearableAssignment.append("Not Assigned")

        wearableUsage.append(
            WearableUsage.objects.all().filter(wearable_name__exact=wearableObject).order_by(
                'updated').first().used)

        wearableBattery.append(
            WearableBattery.objects.all().filter(wearable_name__exact=wearableObject).order_by(
                'updated').first().battery)

        wearableUpdated.append(WearableUsage.objects.all().filter(wearable_name__exact=wearableObject).order_by(
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
            [str(wearableObject.name), str(wearableAssignment[count]), usage, "Center " + str(wearableLocation[count]),
             str(wearableBattery[count]) + "%",
             action, (str(wearableUpdated[count]))[:19]])
        count += 1

        # --------------------

    wearableAssignment = []

    for instance in wearableUnique:
        instanceName = str(instance.name)
        if Assignment.objects.all().filter(wearable_name__exact=instance).exists():
            instanceAssignee = str(Assignment.objects.all().filter(wearable_name__exact=instance).first().name)
        else:
            instanceAssignee = "Not Assigned"
        wearableAssignment.append([instanceName, instanceAssignee])

    return render(request, "alert_bands.html", {'dataSet': wearableData, 'wearableNames': wearableAssignment, 'successMessage': assignee + ' has been assigned to ' + wearableName})

    #return render(request, "alert_bands.html", {'successMessage': assignee + ' has been assigned to ' + wearableName })

@login_required(login_url='')
def incident_reporting(request):
    return render(request, "incident_reporting.html")


@login_required(login_url='')
def settings(request):
    return render(request, "settings.html")


@login_required(login_url='')
def alert(request):
    i = Alert.objects.all().count()

    if i > 0:
        # if standing, return with message
        return render(request, "alert.html", {'message': 'ALERT from Sensor A1.'})
    else:
        return render(request, "alert.html")


def handler404(request):
    response = render_to_response('404.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 404
    return response
