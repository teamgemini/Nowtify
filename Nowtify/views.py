import calendar

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
from Nowtify.models import Alert, Assignment, IncidentReport
from operator import itemgetter
from datetime import datetime,timedelta,date
import csv


def custom_login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect("detectors") #CHANGED FOR DEPLOYMENT
    else:
        return login(request)


def login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect("detectors") #CHANGED FOR DEPLOYMENT

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
            return redirect('detectors') #CHANGED FOR DEPLOYMENT
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
        # change pw successfully, redirect back to Login
        u = User.objects.get(username=current_user_id)
        u.set_password(new_password)
        u.save()
        auth_logout(request)
        c = {}
        c.update(csrf(request))
        return render(request, 'login.html', {'error': 'Please re-login.'})

    elif user is None:
        return render(request, 'settings.html', {'error': 'Incorrect current password. Please re-enter password.'})

    else:
        return render(request, 'settings.html', {'error': 'Passwords do not match. Please re-enter password.'})


@login_required(login_url='')
def index(request):
    return render(request, "index.html")


@login_required(login_url='')
def dashboard(request):
    # Detector.objects.all().delete()
    # DetectorUsage.objects.all().delete()
    # DetectorBattery.objects.all().delete()
    #
    # Wearable.objects.all().delete()
    # WearableUsage.objects.all().delete()
    # WearableBattery.objects.all().delete()
    # #
    # Alert.objects.all().delete()
    # IncidentReport.objects.all().delete()
    # # # DO NOT DELETE YET, Gathering Data over time
    # #
    # # #insert fake data
    # datestr = "2016-10-14 14:45:00"
    # dateobj = datetime.strptime(datestr, '%Y-%m-%d %H:%M:%S')

    # wearable1 = Wearable.objects.create(name="Wearable 1",remarks="superrr1")
    # wearable1Use= WearableUsage.objects.create(wearable_name=wearable1,used=True,updated = dateobj)
    # wearable1Battery = WearableBattery.objects.create(wearable_name=wearable1,battery=40,updated = dateobj) #ON  LOW BATT
    #
    # assignment1 = Assignment.objects.create(name="Shawn", wearable_name=wearable1,update = dateobj)
    #
    # wearable2 = Wearable.objects.create(name="Wearable 2",remarks="superrr2")
    # wearable2Use= WearableUsage.objects.create(wearable_name=wearable2,used=True,updated = dateobj)
    # wearable2Battery = WearableBattery.objects.create(wearable_name=wearable2,battery=70,updated = dateobj) #ON
    #
    # assignment2 = Assignment.objects.create(name="Susan", wearable_name=wearable2,update = dateobj)
    #
    # datestr2 = "2016-10-10 14:45:20"
    # dateobj2 = datetime.strptime(datestr2, '%Y-%m-%d %H:%M:%S')
    # #
    # wearable3 = Wearable.objects.create(name="Wearable 3",remarks="superrr3")
    # wearable3Use= WearableUsage.objects.create(wearable_name=wearable3,used=True,updated = dateobj2)
    # wearable3Battery = WearableBattery.objects.create(wearable_name=wearable3,battery=50,updated = dateobj2) #OFF
    #
    # assignment3 = Assignment.objects.create(name="Dennis", wearable_name=wearable3,update = dateobj2)
    #
    # wearable4 = Wearable.objects.create(name="Wearable 4",remarks="superrr4")
    # wearable4Use= WearableUsage.objects.create(wearable_name=wearable4,used=True,updated = dateobj2)
    # wearable4Battery = WearableBattery.objects.create(wearable_name=wearable4,battery=55,updated = dateobj2) #OFF LOW BATT
    #
    # assignment4 = Assignment.objects.create(name="Momo", wearable_name=wearable4,update = dateobj2)
    #
    # wearable5 = Wearable.objects.create(name="Wearable 5",remarks="i want the name")
    # wearable5Use= WearableUsage.objects.create(wearable_name=wearable5,used=True,updated = dateobj)
    # wearable5Battery = WearableBattery.objects.create(wearable_name=wearable5,battery=70,updated = dateobj) #ON  LOW BATT
    # #
    # assignment5 = Assignment.objects.create(name="Donald Duck",wearable_name=wearable5,update = dateobj2)
    # #
    # #
    # wearable6 = Wearable.objects.create(name="Wearable 6",remarks="More names")
    # wearable6Use= WearableUsage.objects.create(wearable_name=wearable6,used=True,updated = dateobj2)
    # wearable6Battery = WearableBattery.objects.create(wearable_name=wearable6,battery=50,updated = dateobj2) #OFF
    # #
    # assignment6 = Assignment.objects.create(name="Mickey",wearable_name=wearable6,update = dateobj2)
    #
    #
    #
    # detector1 = Detector.objects.create(name="Sensor 1",remarks="ultraaaa1")
    # detector1Use= DetectorUsage.objects.create(detector_name=detector1,used=True,updated = dateobj)
    # detector1Battery = DetectorBattery.objects.create(detector_name=detector1,battery=70,updated = dateobj)  #ON ,low batt
    #
    # detector2 = Detector.objects.create(name="Sensor 2",remarks="ultraaaa2")
    # detector2Use= DetectorUsage.objects.create(detector_name=detector2,used=True,updated = dateobj)
    # detector2Battery = DetectorBattery.objects.create(detector_name=detector2,battery=50,updated = dateobj) #ON

    # detector3 = Detector.objects.create(name="Sensor 3",remarks="ultraaaa3")
    # detector3Use= DetectorUsage.objects.create(detector_name=detector3,used=True,updated = dateobj2)
    # detector3Battery = DetectorBattery.objects.create(detector_name=detector3,battery=40,updated = dateobj2) #OFF
    #
    # detector4 = Detector.objects.create(name="Sensor 4",remarks="ultraaaa4")
    # detector4Use= DetectorUsage.objects.create(detector_name=detector4,used=True,updated = dateobj2)
    # detector4Battery = DetectorBattery.objects.create(detector_name=detector4,battery=60,updated = dateobj2) #OFF ,low batt
    #
    # detector5 = Detector.objects.create(name="Sensor 5",remarks="ultraaaa5")
    # detector5Use= DetectorUsage.objects.create(detector_name=detector5,used=True,updated = dateobj)
    # detector5Battery = DetectorBattery.objects.create(detector_name=detector5,battery=66,updated = dateobj) #OFF ,low batt
    #
    # detector6 = Detector.objects.create(name="Sensor 6",remarks="ultraaaa6")
    # detector6Use= DetectorUsage.objects.create(detector_name=detector6,used=True,updated = dateobj2)
    # detector6Battery = DetectorBattery.objects.create(detector_name=detector6,battery=45,updated = dateobj2) #OFF ,low batt
    #
    #Generate for August
    # alert1 = Alert.objects.create(detector=detector1,wearable=wearable1,seen=False,datetime=datetime.strptime('2016-10-10 14:30:30', '%Y-%m-%d %H:%M:%S'))#1
    # alert1a = Alert.objects.create(detector=detector1,wearable=wearable1,seen=False,datetime=datetime.strptime('2016-10-10 15:30:30', '%Y-%m-%d %H:%M:%S'))
    # alert1b = Alert.objects.create(detector=detector1,wearable=wearable1,seen=False,datetime=datetime.strptime('2016-10-10 16:30:30', '%Y-%m-%d %H:%M:%S'))
    # alert1c = Alert.objects.create(detector=detector1,wearable=wearable1,seen=False,datetime=datetime.strptime('2016-10-10 17:30:30', '%Y-%m-%d %H:%M:%S'))
    # report1= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-08-01 14:30:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')
    #
    # alert2 = Alert.objects.create(detector=detector2,wearable=wearable2,seen=False,datetime=datetime.strptime('2016-10-10 14:30:30', '%Y-%m-%d %H:%M:%S'))#2
    # report2= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-10-10 14:30:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')

    # alert3 = Alert.objects.create(detector=detector3,wearable=wearable3,seen=False,datetime=datetime.strptime('2016-08-03 14:30:30', '%Y-%m-%d %H:%M:%S'))#3
    # alert3a = Alert.objects.create(detector=detector3,wearable=wearable3,seen=False,datetime=datetime.strptime('2016-08-03 15:30:30', '%Y-%m-%d %H:%M:%S'))
    # alert3b= Alert.objects.create(detector=detector3,wearable=wearable3,seen=False,datetime=datetime.strptime('2016-08-03 16:30:30', '%Y-%m-%d %H:%M:%S'))
    # alert3c = Alert.objects.create(detector=detector3,wearable=wearable3,seen=False,datetime=datetime.strptime('2016-08-03 17:30:30', '%Y-%m-%d %H:%M:%S'))
    # report3= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-08-03 14:30:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')
    #
    # alert4 = Alert.objects.create(detector=detector4,wearable=wearable4,seen=False,datetime=datetime.strptime('2016-08-04 14:30:30', '%Y-%m-%d %H:%M:%S'))#4
    # report4= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-08-04 14:30:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')
    #
    # alert5 = Alert.objects.create(detector=detector5,wearable=wearable5,seen=False,datetime=datetime.strptime('2016-08-05 14:30:30', '%Y-%m-%d %H:%M:%S'))#5
    # report5= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-08-05 14:30:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')
    #
    # alert6 = Alert.objects.create(detector=detector6,wearable=wearable6,seen=False,datetime=datetime.strptime('2016-08-08 14:30:30', '%Y-%m-%d %H:%M:%S'))#8
    # alert6a = Alert.objects.create(detector=detector6,wearable=wearable6,seen=False,datetime=datetime.strptime('2016-08-08 15:30:30', '%Y-%m-%d %H:%M:%S'))
    # alert6b = Alert.objects.create(detector=detector6,wearable=wearable6,seen=False,datetime=datetime.strptime('2016-08-08 16:30:30', '%Y-%m-%d %H:%M:%S'))
    # alert6c = Alert.objects.create(detector=detector6,wearable=wearable6,seen=False,datetime=datetime.strptime('2016-08-08 17:30:30', '%Y-%m-%d %H:%M:%S'))
    # alert6d = Alert.objects.create(detector=detector6,wearable=wearable6,seen=False,datetime=datetime.strptime('2016-08-08 18:30:30', '%Y-%m-%d %H:%M:%S'))
    # report6= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-08-08 14:30:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')
    #
    # alert7 = Alert.objects.create(detector=detector1,wearable=wearable1,seen=False,datetime=datetime.strptime('2016-08-09 14:30:30', '%Y-%m-%d %H:%M:%S'))#9
    # alert7a = Alert.objects.create(detector=detector1,wearable=wearable1,seen=False,datetime=datetime.strptime('2016-08-09 15:30:30', '%Y-%m-%d %H:%M:%S'))
    # report7= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-08-09 14:30:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')

    # alert8 = Alert.objects.create(detector=detector2,wearable=wearable2,seen=False,datetime=datetime.strptime('2016-08-10 14:30:30', '%Y-%m-%d %H:%M:%S'))#10
    # alert8a = Alert.objects.create(detector=detector2,wearable=wearable2,seen=False,datetime=datetime.strptime('2016-08-10 15:30:30', '%Y-%m-%d %H:%M:%S'))
    # alert8b = Alert.objects.create(detector=detector2,wearable=wearable2,seen=False,datetime=datetime.strptime('2016-08-10 16:30:30', '%Y-%m-%d %H:%M:%S'))
    # alert8c = Alert.objects.create(detector=detector2,wearable=wearable2,seen=False,datetime=datetime.strptime('2016-08-10 17:30:30', '%Y-%m-%d %H:%M:%S'))
    # alert8d = Alert.objects.create(detector=detector2,wearable=wearable2,seen=False,datetime=datetime.strptime('2016-08-10 18:30:30', '%Y-%m-%d %H:%M:%S'))
    # alert8e = Alert.objects.create(detector=detector2,wearable=wearable2,seen=False,datetime=datetime.strptime('2016-08-10 19:30:30', '%Y-%m-%d %H:%M:%S'))
    # report8= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-08-10 14:30:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')
    #
    # alert9 = Alert.objects.create(detector=detector3,wearable=wearable3,seen=False,datetime=datetime.strptime('2016-08-11 14:30:30', '%Y-%m-%d %H:%M:%S'))#11
    # report9= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-08-11 14:30:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')
    #
    # alert10 = Alert.objects.create(detector=detector4,wearable=wearable4,seen=False,datetime=datetime.strptime('2016-08-12 14:30:30', '%Y-%m-%d %H:%M:%S'))#12
    # report10= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-08-12 14:30:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')
    #
    #
    # alert11 = Alert.objects.create(detector=detector5,wearable=wearable5,seen=False,datetime=datetime.strptime('2016-10-14 14:30:30', '%Y-%m-%d %H:%M:%S'))#15
    # alert11a = Alert.objects.create(detector=detector5,wearable=wearable5,seen=False,datetime=datetime.strptime('2016-08-15 15:00:30', '%Y-%m-%d %H:%M:%S'))
    # alert11b = Alert.objects.create(detector=detector5,wearable=wearable5,seen=False,datetime=datetime.strptime('2016-08-15 15:30:30', '%Y-%m-%d %H:%M:%S'))
    # alert11c = Alert.objects.create(detector=detector5,wearable=wearable5,seen=False,datetime=datetime.strptime('2016-08-15 16:00:30', '%Y-%m-%d %H:%M:%S'))
    # alert11d = Alert.objects.create(detector=detector5,wearable=wearable5,seen=False,datetime=datetime.strptime('2016-08-15 16:20:30', '%Y-%m-%d %H:%M:%S'))
    # alert11e = Alert.objects.create(detector=detector5,wearable=wearable5,seen=False,datetime=datetime.strptime('2016-08-15 17:10:30', '%Y-%m-%d %H:%M:%S'))
    # alert11f = Alert.objects.create(detector=detector5,wearable=wearable5,seen=False,datetime=datetime.strptime('2016-08-15 17:15:30', '%Y-%m-%d %H:%M:%S'))
    # report11= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-08-15 14:30:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')
    #
    # alert12 = Alert.objects.create(detector=detector6,wearable=wearable6,seen=False,datetime=datetime.strptime('2016-08-16 14:30:30', '%Y-%m-%d %H:%M:%S'))#16
    # report12= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-08-16 14:30:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')
    #
    # alert13 = Alert.objects.create(detector=detector1,wearable=wearable1,seen=False,datetime=datetime.strptime('2016-08-17 14:30:30', '%Y-%m-%d %H:%M:%S'))#17
    # alert13a = Alert.objects.create(detector=detector1,wearable=wearable1,seen=False,datetime=datetime.strptime('2016-08-17 15:30:30', '%Y-%m-%d %H:%M:%S'))
    # alert13b = Alert.objects.create(detector=detector1,wearable=wearable1,seen=False,datetime=datetime.strptime('2016-08-17 16:30:30', '%Y-%m-%d %H:%M:%S'))
    # alert13c = Alert.objects.create(detector=detector1,wearable=wearable1,seen=False,datetime=datetime.strptime('2016-08-17 17:30:30', '%Y-%m-%d %H:%M:%S'))
    # alert13d = Alert.objects.create(detector=detector1,wearable=wearable1,seen=False,datetime=datetime.strptime('2016-08-17 18:30:30', '%Y-%m-%d %H:%M:%S'))
    # report13= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-08-17 14:30:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')

    #
    # alert14 = Alert.objects.create(detector=detector2,wearable=wearable2,seen=False,datetime=datetime.strptime('2016-08-18 14:30:30', '%Y-%m-%d %H:%M:%S'))#18
    # report18= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-08-18 14:30:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')
    #
    # alert15 = Alert.objects.create(detector=detector3,wearable=wearable3,seen=False,datetime=datetime.strptime('2016-08-19 14:30:30', '%Y-%m-%d %H:%M:%S'))#19
    # report15= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-08-19 14:30:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')
    #
    # alert16 = Alert.objects.create(detector=detector4,wearable=wearable4,seen=False,datetime=datetime.strptime('2016-08-22 14:30:30', '%Y-%m-%d %H:%M:%S'))#22
    # alert16a = Alert.objects.create(detector=detector4,wearable=wearable4,seen=False,datetime=datetime.strptime('2016-08-22 14:30:35', '%Y-%m-%d %H:%M:%S'))
    # alert16b = Alert.objects.create(detector=detector4,wearable=wearable4,seen=False,datetime=datetime.strptime('2016-08-22 16:30:30', '%Y-%m-%d %H:%M:%S'))
    # alert16c = Alert.objects.create(detector=detector4,wearable=wearable4,seen=False,datetime=datetime.strptime('2016-08-22 17:30:30', '%Y-%m-%d %H:%M:%S'))
    # report16= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-08-22 16:30:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')
    #
    #
    # alert17 = Alert.objects.create(detector=detector5,wearable=wearable5,seen=False,datetime=datetime.strptime('2016-08-23 14:30:30', '%Y-%m-%d %H:%M:%S'))#23
    # report17= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-08-23 15:30:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')
    #
    #
    # alert18 = Alert.objects.create(detector=detector6,wearable=wearable6,seen=False,datetime=datetime.strptime('2016-08-24 14:30:30', '%Y-%m-%d %H:%M:%S'))#24
    # alert18a = Alert.objects.create(detector=detector6,wearable=wearable6,seen=False,datetime=datetime.strptime('2016-08-24 14:35:30', '%Y-%m-%d %H:%M:%S'))
    # alert18b = Alert.objects.create(detector=detector6,wearable=wearable6,seen=False,datetime=datetime.strptime('2016-08-24 14:36:30', '%Y-%m-%d %H:%M:%S'))
    # alert18c = Alert.objects.create(detector=detector6,wearable=wearable6,seen=False,datetime=datetime.strptime('2016-08-24 14:37:30', '%Y-%m-%d %H:%M:%S'))
    # alert18d = Alert.objects.create(detector=detector6,wearable=wearable6,seen=False,datetime=datetime.strptime('2016-08-24 14:38:30', '%Y-%m-%d %H:%M:%S'))
    # report18= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-08-24 15:30:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')
    #
    #
    # alert19 = Alert.objects.create(detector=detector1,wearable=wearable1,seen=False,datetime=datetime.strptime('2016-08-25 14:30:30', '%Y-%m-%d %H:%M:%S'))#25
    # report19= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-08-25 14:30:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')

    # alert20 = Alert.objects.create(detector=detector2,wearable=wearable2,seen=False,datetime=datetime.strptime('2016-08-26 14:30:30', '%Y-%m-%d %H:%M:%S'))#26
    # alert20a = Alert.objects.create(detector=detector2,wearable=wearable2,seen=False,datetime=datetime.strptime('2016-08-26 15:30:30', '%Y-%m-%d %H:%M:%S'))
    # report20= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-08-26 15:30:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')
    #
    #
    # alert21 = Alert.objects.create(detector=detector3,wearable=wearable3,seen=False,datetime=datetime.strptime('2016-08-29 14:30:30', '%Y-%m-%d %H:%M:%S'))#29
    # alert21a = Alert.objects.create(detector=detector3,wearable=wearable3,seen=False,datetime=datetime.strptime('2016-08-29 14:31:30', '%Y-%m-%d %H:%M:%S'))
    # alert21b = Alert.objects.create(detector=detector3,wearable=wearable3,seen=False,datetime=datetime.strptime('2016-08-29 14:32:30', '%Y-%m-%d %H:%M:%S'))
    # alert21c = Alert.objects.create(detector=detector3,wearable=wearable3,seen=False,datetime=datetime.strptime('2016-08-29 14:33:30', '%Y-%m-%d %H:%M:%S'))
    # report21= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-08-29 14:31:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')
    #
    # alert22 = Alert.objects.create(detector=detector4,wearable=wearable4,seen=False,datetime=datetime.strptime('2016-08-30 14:30:30', '%Y-%m-%d %H:%M:%S'))#30
    # report22= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-08-30 14:30:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')
    #
    # alert23 = Alert.objects.create(detector=detector5,wearable=wearable5,seen=False,datetime=datetime.strptime('2016-08-31 14:33:30', '%Y-%m-%d %H:%M:%S'))#31
    # alert23a = Alert.objects.create(detector=detector5,wearable=wearable5,seen=False,datetime=datetime.strptime('2016-08-31 14:34:30', '%Y-%m-%d %H:%M:%S'))
    # alert23b = Alert.objects.create(detector=detector5,wearable=wearable5,seen=False,datetime=datetime.strptime('2016-08-31 14:35:30', '%Y-%m-%d %H:%M:%S'))
    # alert23c = Alert.objects.create(detector=detector5,wearable=wearable5,seen=False,datetime=datetime.strptime('2016-08-31 14:36:30', '%Y-%m-%d %H:%M:%S'))
    # report23= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-08-31 14:35:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')
    #
    #
    # #Generate for September
    # salert1 = Alert.objects.create(detector=detector1,wearable=wearable1,seen=False,datetime=datetime.strptime('2016-09-01 14:30:30', '%Y-%m-%d %H:%M:%S'))#1
    # sreport1= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-09-01 14:30:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')
    #
    # # salert2 = Alert.objects.create(detector=detector2,wearable=wearable2,seen=False,datetime=datetime.strptime('2016-09-02 14:30:30', '%Y-%m-%d %H:%M:%S'))#2
    # salert2a = Alert.objects.create(detector=detector1,wearable=wearable1,seen=False,datetime=datetime.strptime('2016-09-02 15:30:30', '%Y-%m-%d %H:%M:%S'))
    # sreport2= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-09-02 14:30:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')

    # salert3 = Alert.objects.create(detector=detector3,wearable=wearable3,seen=False,datetime=datetime.strptime('2016-09-05 14:30:30', '%Y-%m-%d %H:%M:%S'))#5
    # salert3a = Alert.objects.create(detector=detector3,wearable=wearable3,seen=False,datetime=datetime.strptime('2016-09-05 15:30:30', '%Y-%m-%d %H:%M:%S'))
    # salert3b= Alert.objects.create(detector=detector3,wearable=wearable3,seen=False,datetime=datetime.strptime('2016-09-05 16:30:30', '%Y-%m-%d %H:%M:%S'))
    # salert3c = Alert.objects.create(detector=detector3,wearable=wearable3,seen=False,datetime=datetime.strptime('2016-09-05 17:30:30', '%Y-%m-%d %H:%M:%S'))
    # sreport3= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-09-05 16:30:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')
    #
    # salert4 = Alert.objects.create(detector=detector4,wearable=wearable4,seen=False,datetime=datetime.strptime('2016-09-06 14:30:30', '%Y-%m-%d %H:%M:%S'))#6
    # salert5 = Alert.objects.create(detector=detector5,wearable=wearable5,seen=False,datetime=datetime.strptime('2016-09-06 14:30:30', '%Y-%m-%d %H:%M:%S'))
    # sreport5= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-09-06 14:30:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')
    #
    # salert6 = Alert.objects.create(detector=detector6,wearable=wearable6,seen=False,datetime=datetime.strptime('2016-09-07 14:30:30', '%Y-%m-%d %H:%M:%S'))#7
    # salert6a = Alert.objects.create(detector=detector6,wearable=wearable6,seen=False,datetime=datetime.strptime('2016-09-07 15:30:30', '%Y-%m-%d %H:%M:%S'))
    # salert6b = Alert.objects.create(detector=detector6,wearable=wearable6,seen=False,datetime=datetime.strptime('2016-09-07 16:30:30', '%Y-%m-%d %H:%M:%S'))
    # salert6c = Alert.objects.create(detector=detector6,wearable=wearable6,seen=False,datetime=datetime.strptime('2016-09-07 17:30:30', '%Y-%m-%d %H:%M:%S'))
    # salert6d = Alert.objects.create(detector=detector6,wearable=wearable6,seen=False,datetime=datetime.strptime('2016-09-07 18:30:30', '%Y-%m-%d %H:%M:%S'))
    # sreport6= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-09-07 17:30:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')
    #
    # salert7 = Alert.objects.create(detector=detector1,wearable=wearable1,seen=False,datetime=datetime.strptime('2016-09-08 14:30:30', '%Y-%m-%d %H:%M:%S'))#8
    # sreport7= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-09-08 14:30:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')
    #
    # salert7a = Alert.objects.create(detector=detector1,wearable=wearable1,seen=False,datetime=datetime.strptime('2016-09-09 15:30:30', '%Y-%m-%d %H:%M:%S'))#9
    # sreport7a= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-09-09 14:30:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')

    # salert8 = Alert.objects.create(detector=detector2,wearable=wearable2,seen=False,datetime=datetime.strptime('2016-09-12 14:30:30', '%Y-%m-%d %H:%M:%S'))#12
    # salert8a = Alert.objects.create(detector=detector2,wearable=wearable2,seen=False,datetime=datetime.strptime('2016-09-12 15:30:30', '%Y-%m-%d %H:%M:%S'))
    # salert8b = Alert.objects.create(detector=detector2,wearable=wearable2,seen=False,datetime=datetime.strptime('2016-09-12 16:30:30', '%Y-%m-%d %H:%M:%S'))
    # salert8c = Alert.objects.create(detector=detector2,wearable=wearable2,seen=False,datetime=datetime.strptime('2016-09-12 17:30:30', '%Y-%m-%d %H:%M:%S'))
    # salert8d = Alert.objects.create(detector=detector2,wearable=wearable2,seen=False,datetime=datetime.strptime('2016-09-12 18:30:30', '%Y-%m-%d %H:%M:%S'))
    # salert8e = Alert.objects.create(detector=detector2,wearable=wearable2,seen=False,datetime=datetime.strptime('2016-09-12 19:30:30', '%Y-%m-%d %H:%M:%S'))
    # sreport8= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-09-12 18:30:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')
    #
    # salert9 = Alert.objects.create(detector=detector3,wearable=wearable3,seen=False,datetime=datetime.strptime('2016-09-13 14:30:30', '%Y-%m-%d %H:%M:%S'))#13
    # salert10 = Alert.objects.create(detector=detector4,wearable=wearable4,seen=False,datetime=datetime.strptime('2016-09-13 14:31:30', '%Y-%m-%d %H:%M:%S'))
    # sreport10= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-09-13 14:31:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')
    #
    #
    #
    # salert11 = Alert.objects.create(detector=detector5,wearable=wearable5,seen=False,datetime=datetime.strptime('2016-09-14 14:30:30', '%Y-%m-%d %H:%M:%S'))#14
    # salert11a = Alert.objects.create(detector=detector5,wearable=wearable5,seen=False,datetime=datetime.strptime('2016-09-14 15:00:30', '%Y-%m-%d %H:%M:%S'))
    # salert11b = Alert.objects.create(detector=detector5,wearable=wearable5,seen=False,datetime=datetime.strptime('2016-09-14 15:30:30', '%Y-%m-%d %H:%M:%S'))
    # salert11c = Alert.objects.create(detector=detector5,wearable=wearable5,seen=False,datetime=datetime.strptime('2016-09-14 16:00:30', '%Y-%m-%d %H:%M:%S'))
    # salert11d = Alert.objects.create(detector=detector5,wearable=wearable5,seen=False,datetime=datetime.strptime('2016-09-14 16:20:30', '%Y-%m-%d %H:%M:%S'))
    # salert11e = Alert.objects.create(detector=detector5,wearable=wearable5,seen=False,datetime=datetime.strptime('2016-09-14 17:10:30', '%Y-%m-%d %H:%M:%S'))
    # salert11f = Alert.objects.create(detector=detector5,wearable=wearable5,seen=False,datetime=datetime.strptime('2016-09-14 17:15:30', '%Y-%m-%d %H:%M:%S'))
    # sreport11= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-09-14 16:30:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')
    #
    # salert12 = Alert.objects.create(detector=detector6,wearable=wearable6,seen=False,datetime=datetime.strptime('2016-09-15 14:30:30', '%Y-%m-%d %H:%M:%S'))#15
    # sreport12= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-09-15 14:30:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')
    #
    # salert13 = Alert.objects.create(detector=detector1,wearable=wearable1,seen=False,datetime=datetime.strptime('2016-09-16 14:30:30', '%Y-%m-%d %H:%M:%S'))#16
    # sreport13= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-09-16 14:30:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')
    #
    # salert13a = Alert.objects.create(detector=detector1,wearable=wearable1,seen=False,datetime=datetime.strptime('2016-09-19 15:30:30', '%Y-%m-%d %H:%M:%S'))#19
    # salert13b = Alert.objects.create(detector=detector1,wearable=wearable1,seen=False,datetime=datetime.strptime('2016-09-19 16:30:30', '%Y-%m-%d %H:%M:%S'))
    # salert13c = Alert.objects.create(detector=detector1,wearable=wearable1,seen=False,datetime=datetime.strptime('2016-09-19 17:30:30', '%Y-%m-%d %H:%M:%S'))
    # salert13d = Alert.objects.create(detector=detector1,wearable=wearable1,seen=False,datetime=datetime.strptime('2016-09-19 18:30:30', '%Y-%m-%d %H:%M:%S'))
    # sreport13= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-09-19 14:30:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')


    # salert14 = Alert.objects.create(detector=detector2,wearable=wearable2,seen=False,datetime=datetime.strptime('2016-09-20 14:30:30', '%Y-%m-%d %H:%M:%S'))#20
    # salert15 = Alert.objects.create(detector=detector3,wearable=wearable3,seen=False,datetime=datetime.strptime('2016-09-20 14:30:30', '%Y-%m-%d %H:%M:%S'))
    # sreport15= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-09-20 14:30:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')
    #
    # salert16 = Alert.objects.create(detector=detector4,wearable=wearable4,seen=False,datetime=datetime.strptime('2016-09-21 14:30:30', '%Y-%m-%d %H:%M:%S'))#21
    # salert16a = Alert.objects.create(detector=detector4,wearable=wearable4,seen=False,datetime=datetime.strptime('2016-09-21 14:30:35', '%Y-%m-%d %H:%M:%S'))
    # salert16b = Alert.objects.create(detector=detector4,wearable=wearable4,seen=False,datetime=datetime.strptime('2016-09-21 16:30:30', '%Y-%m-%d %H:%M:%S'))
    # salert16c = Alert.objects.create(detector=detector4,wearable=wearable4,seen=False,datetime=datetime.strptime('2016-09-21 17:30:30', '%Y-%m-%d %H:%M:%S'))
    # sreport16= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-09-21 14:30:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')
    #
    # salert17 = Alert.objects.create(detector=detector5,wearable=wearable5,seen=False,datetime=datetime.strptime('2016-09-22 14:30:30', '%Y-%m-%d %H:%M:%S'))#22
    # sreport17= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-09-22 14:30:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')
    #
    # salert17a = Alert.objects.create(detector=detector5,wearable=wearable5,seen=False,datetime=datetime.strptime('2016-09-23 14:30:30', '%Y-%m-%d %H:%M:%S'))#23
    # sreport17a= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-09-23 14:30:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')
    #
    #
    # salert18 = Alert.objects.create(detector=detector6,wearable=wearable6,seen=False,datetime=datetime.strptime('2016-09-26 14:30:30', '%Y-%m-%d %H:%M:%S'))#26
    # salert18a = Alert.objects.create(detector=detector6,wearable=wearable6,seen=False,datetime=datetime.strptime('2016-09-26 14:35:30', '%Y-%m-%d %H:%M:%S'))
    # salert18b = Alert.objects.create(detector=detector6,wearable=wearable6,seen=False,datetime=datetime.strptime('2016-09-26 14:36:30', '%Y-%m-%d %H:%M:%S'))
    # salert18c = Alert.objects.create(detector=detector6,wearable=wearable6,seen=False,datetime=datetime.strptime('2016-09-26 14:37:30', '%Y-%m-%d %H:%M:%S'))
    # salert18d = Alert.objects.create(detector=detector6,wearable=wearable6,seen=False,datetime=datetime.strptime('2016-09-26 14:38:30', '%Y-%m-%d %H:%M:%S'))
    # sreport18= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-09-26 14:37:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')
    #
    #
    # salert19 = Alert.objects.create(detector=detector1,wearable=wearable1,seen=False,datetime=datetime.strptime('2016-09-27 14:30:30', '%Y-%m-%d %H:%M:%S'))#27
    # sreport19= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-09-27 14:30:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')

    # salert20 = Alert.objects.create(detector=detector2,wearable=wearable2,seen=False,datetime=datetime.strptime('2016-09-28 14:30:30', '%Y-%m-%d %H:%M:%S'))#28
    # salert20a = Alert.objects.create(detector=detector2,wearable=wearable2,seen=False,datetime=datetime.strptime('2016-09-28 15:20:30', '%Y-%m-%d %H:%M:%S'))
    # salert20b = Alert.objects.create(detector=detector2,wearable=wearable2,seen=False,datetime=datetime.strptime('2016-09-28 15:30:30', '%Y-%m-%d %H:%M:%S'))
    # sreport20= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-09-28 15:30:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')
    #
    #
    # salert21 = Alert.objects.create(detector=detector3,wearable=wearable3,seen=False,datetime=datetime.strptime('2016-09-29 14:30:30', '%Y-%m-%d %H:%M:%S'))#29
    # sreport21= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-09-29 14:30:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')
    #
    #
    # salert22 = Alert.objects.create(detector=detector4,wearable=wearable4,seen=False,datetime=datetime.strptime('2016-09-30 14:30:30', '%Y-%m-%d %H:%M:%S'))#30
    # sreport22= IncidentReport.objects.create(client_name='Tan',caregiver_name='Shawn',author_name='Shawn',datetime=datetime.strptime('2016-09-30 14:30:30', '%Y-%m-%d %H:%M:%S'),comments='TESTING')
    #




    # alert1 = Alert.objects.create(detector=detector1,wearable=wearable1,seen=False) #activated
    # alert2 = Alert.objects.create(detector=detector2,wearable=wearable2,seen=True) #acknowledged
    #
    # wearableJJ = Wearable.objects.create(name="wearableJJ",remarks="wearableJJ")
    # wearableJJUse= WearableUsage.objects.create(wearable_name=wearableJJ,used=True)
    # wearableJJBattery = WearableBattery.objects.create(wearable_name=wearableJJ,battery=50) #ON
    #
    # detectorJJ = Detector.objects.create(name="detectorJJ",remarks="detectorJJ")
    # detectorJJUse= DetectorUsage.objects.create(detector_name=detectorJJ,used=True)
    # detectorJJBattery = DetectorBattery.objects.create(detector_name=detectorJJ,battery=50) #OFF
    #
    # testingTime= (datetime.now() - timedelta(days=1)).replace(hour=2, minute=2, second=2, microsecond=2)
    # alertJJ = Alert.objects.create(detector=detectorJJ,wearable=wearableJJ,seen=False,datetime=testingTime) #activated

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

    alertWeekList= []
    alertMonthList= []

    startOfYtd = (datetime.now()- timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0) #yesterday's 00:00:00


    startOfWeekNum = 1
    daysAfterStartOfWeek = 0
    endOfWeekNum = 7 #not used. for reference

    if (datetime.now().isoweekday == 1):
        daysAfterStartOfWeek = 0

    if(datetime.now().isoweekday() > 1):
        daysAfterStartOfWeek = datetime.now().isoweekday()-1 #if 4, 4-3 = 1 which is monday
    #get start of week (monday) 00:00:00:00

    startOfWeek = (datetime.now() - timedelta(days=daysAfterStartOfWeek)).replace(hour=0, minute=0, second=0, microsecond=0)


    if(datetime.now().isoweekday() < 7):
        daysToEndOfWeek = 7 - (datetime.now().isoweekday())

    if(datetime.now().isoweekday() == 7):
        daysToEndOfWeek = 0

    #get end of week (sunday) 23:59:59:59
    endOfWeek = (datetime.now() + timedelta(days=daysToEndOfWeek)).replace(hour=23, minute=59, second=59, microsecond=59)


    startOfMonth = 1
    today = datetime.now()
    startOfToday = (datetime.now()).replace(hour=0, minute=0, second=0, microsecond=0)
    endOfToday = (datetime.now()).replace(hour=23, minute=59, second=59, microsecond=59)
    thisMonthNum = today.month
    thisYearNum = today.year
    thisMonthEndNum = str(calendar.monthrange(thisYearNum,thisMonthNum)[1])
    thisMonthStartNum = "1"
    thisMonthStart = datetime.strptime(thisMonthStartNum + "/" + str(thisMonthNum)+ "/" + str(thisYearNum) + " 00:00:00", "%d/%m/%Y %H:%M:%S")
    thisMonthEnd = datetime.strptime(thisMonthEndNum + "/" + str(thisMonthNum) + "/" + str(thisYearNum) + " 23:59:59", "%d/%m/%Y %H:%M:%S")

    detectorList = Detector.objects.all()
    detectorUsageList = DetectorUsage.objects.all()
    detectorBatteryList = DetectorBattery.objects.all()

#DetectorOnOff
    detectorCounter = 0
    for instanceDetector in detectorList:
        detectorUsageUnique.append(instanceDetector)

    # there are many rows of data, this code will filter by each unique sensor, arrange from newest to oldest data
    # and get the first one, aka the latest data


    # for detectorObject in detectorUsageUnique: REMOVED FOR DEPLOYMENT
    #     if detectorUsageList.filter(detector_name__exact=detectorObject,updated__gte=startOfYtd).exists():
    #         detectorUsage.append(detectorUsageList.filter(detector_name__exact=detectorObject,updated__gte=startOfYtd).order_by('updated').first()) # order by time only for ON OFF

 #For DEPLOYMENT
    for detectorObject in detectorUsageUnique:
        if detectorUsageList.filter(detector_name__exact=detectorObject,updated__range=(startOfToday,endOfToday)).exists():
            detectorUsage.append(detectorUsageList.filter(detector_name__exact=detectorObject,updated__range=(startOfToday,endOfToday)).order_by('-updated').first()) # order by time only for ON OFF

    # order by time only for ON OFF
    for instance in detectorUsage:
        if instance.used == True:
            detectorCounter += 1

    # for instance in detectorUsage: REMOVED FOR DEPLOYMENT
    #     messageType=""
    #     message=""
    #     timestamp=None
    #
    #     if instance.used == True:
    #         messageType="Sensor"
    #         message=str(instance.detector_name.name) + " in Center 1 has been Switched ON"
    #
    #         if(str(instance.updated.date()) == str(datetime.today().date())):
    #             timestamp = "Today " + str(instance.updated)[11:19]
    #         else:
    #             timestamp=datetime.strptime(str(instance.updated)[:19],'%Y-%m-%d %H:%M:%S').strftime("%d-%m-%Y %H:%M:%S")
    #         detectorCounter += 1
    #
    #         masterList.append([messageType,message,timestamp])
    #
    #     if instance.used == False:
    #         messageType="Sensor"
    #         message=str(instance.detector_name.name) + " in Center 1 has been Switched OFF"
    #
    #         if(str(instance.updated.date()) == str(datetime.today().date())):
    #             timestamp = "Today " + str(instance.updated)[11:19]
    #         else:
    #             timestamp=datetime.strptime(str(instance.updated)[:19],'%Y-%m-%d %H:%M:%S').strftime("%d-%m-%Y %H:%M:%S")
    #         masterList.append([messageType,message,timestamp])





# #DetectorBattery    REMOVED FOR DEPLOYMENT
#     for instanceDetector in detectorList:
#         detectorBatteryUnique.append(instanceDetector)
#     # there are many rows of data, this code will filter by each unique sensor, arrange from newest to oldest data
#     # and get the first one, aka the latest data
#
#
#     for detectorObject in detectorBatteryUnique: #take all sensors
#         if detectorBatteryList.filter(detector_name__exact=detectorObject,updated__gte=startOfYtd).exists():
#             detectorBattery.append(detectorBatteryList.filter(detector_name__exact=detectorObject,updated__gte=startOfYtd).order_by('updated').first())
#     #take only sensorBattery objects, filter by sensor name to prevent repeats, filer by condition, order by datetime,take latest
#
#
#     for instance in detectorBattery:
#
#         messageType=""
#         message=""
#         timestamp=None
#
#         if(instance.battery)<= 30:
#             messageType="Sensor"
#             message=str(instance.detector_name.name) + " in Center 1 is below 30% Battery, Recharge Required!"
#
#             if(str(instance.updated.date()) == str(datetime.today().date())):
#                 timestamp = "Today " + str(instance.updated)[11:19]
#             else:
#                 timestamp=datetime.strptime(str(instance.updated)[:19],'%Y-%m-%d %H:%M:%S').strftime("%d-%m-%Y %H:%M:%S")
#
#             masterList.append([messageType,message,timestamp])




#WearableOnOff
    wearableCounter = 0

    wearableList = Wearable.objects.all()
    wearableUsageList = WearableUsage.objects.all()
    wearableBatteryList = WearableBattery.objects.all()

    tstart = datetime.now()
    for instanceWearable in wearableList:
        wearableUsageUnique.append(instanceWearable)
    # there are many rows of data, this code will filter by each unique wearable, arrange from newest to oldest data
    # and get the first one, aka the latest data
    # tdiff0 = str(datetime.now() - tstart)  #REMOVED FOR DEPLOYMENT

    # tstart2 = datetime.now() #REMOVED FOR DEPLOYMENT
    # for wearableObject in wearableUsageUnique: REMOVED FOR DEPLOYMENT
    #     if wearableUsageList.filter(wearable_name__exact=wearableObject,updated__gte=startOfYtd).exists():
    #         wearableUsage.append(wearableUsageList.filter(wearable_name__exact=wearableObject,updated__gte=startOfYtd).order_by('updated').first()) # order by time only for ON OFF
    #
    for wearableObject in wearableUsageUnique:  #FOR DEPLOYMENT
        if wearableUsageList.filter(wearable_name__exact=wearableObject,updated__range=(startOfToday,endOfToday)).exists():
            wearableUsage.append(wearableUsageList.filter(wearable_name__exact=wearableObject, updated__range=(startOfToday,endOfToday)).order_by('-updated').first())  # order by time only for ON OFF

    for instance in wearableUsage:

        if instance.used==True:
            wearableCounter +=1

    # tdiff2 = str( datetime.now() - tstart2)      REMOVED FOR DEPLOYMENT
    #
    # #call for all assignment objects
    # allAssignment = Assignment.objects.all()
    #
    # tdiff = ''

    # for instance in wearableUsage:
    #     t1 = datetime.now()
    #     messageType=""
    #     message=""
    #     time=None
    #     caregiver = "" #to store assigned caregiver name
    #
    #     if instance.used == True:
    #         messageType="Wearable"
    #
    #         #get assignment for the wearable instance
    #         if allAssignment.filter(wearable_name__exact=instance.wearable_name, update__gte=startOfYtd).exists():
    #             caregiver = allAssignment.filter(wearable_name__exact=instance.wearable_name, update__gte=startOfYtd).order_by('update').first().name
    #             message = str(instance.wearable_name.name) + " in Center 1 has been Switched ON by " + str(caregiver)
    #         else:
    #             message = str(
    #                 instance.wearable_name.name) + " in Center 1 has been Switched ON, no Caregiver assigned yet"
    #
    #         if(str(instance.updated.date()) == str(datetime.today().date())):
    #             timestamp = "Today " + str(instance.updated)[11:19]
    #         else:
    #             # timestamp=datetime.strptime(str(instance.updated)[:19],'%Y-%m-%d %H:%M:%S').strftime("%d-%m-%Y %H:%M:%S")
    #             timestamp = '01:00:00'
    #         wearableCounter += 1
    #
    #         t2 = datetime.now()
    #         tdiff = str(t2-t1)
    #
    #         masterList.append([messageType + tdiff0 ,message + tdiff ,timestamp + tdiff2])
    #
    #
    #     if instance.used == False:
    #         messageType="Wearable"
    #
    #         # compare lists to see if a Caregiver has been assigned to the wearable,change message accordingly
    #         if allAssignment.filter(wearable_name__exact=instance.wearable_name, update__gte=startOfYtd).exists():
    #             caregiver = allAssignment.filter(wearable_name__exact=instance.wearable_name, update__gte=startOfYtd).order_by('update').first().name
    #             message = str(instance.wearable_name.name) + " in Center 1 has been Switched OFF by " + str(caregiver)
    #         else:
    #             message = str(
    #                 instance.wearable_name.name) + " in Center 1 has been Switched OFF, no Caregiver assigned yet"
    #
    #         if(str(instance.updated.date()) == str(datetime.today().date())):
    #             timestamp = "Today " + str(instance.updated)[11:19]
    #         else:
    #             timestamp=datetime.strptime(str(instance.updated)[:19],'%Y-%m-%d %H:%M:%S').strftime("%d-%m-%Y %H:%M:%S")
    #
    #         masterList.append([messageType,message,timestamp])



# #WearableBattery    REMOVED FOR DEPLOYMENT
#     for instanceWearable in wearableList:
#         wearableBatteryUnique.append(instanceWearable)
#     # there are many rows of data, this code will filter by each unique sensor, arrange from newest to oldest data
#     # and get the first one, aka the latest data
#
#
#     for wearableObject in wearableBatteryUnique: #take all sensors
#         if wearableBatteryList.filter(wearable_name__exact=wearableObject,updated__gte=startOfYtd).exists():
#             wearableBattery.append(wearableBatteryList.filter(wearable_name__exact=wearableObject,updated__gte=startOfYtd).order_by('updated').first())
#     #take only sensorBattery objects, filter by sensor name to prevent repeats, filer by condition, order by datetime, take latest
#
#     # if all(None for item in wearableBattery) and len(detectorUsage)== 4:
#
#     for instance in wearableBattery:
#
#         messageType=""
#         message=""
#         timestamp=None
#         caregiver = ""
#
#         if(instance.battery)<= 30:
#             messageType="Wearable"
#
#             if allAssignment.filter(wearable_name__exact=instance.wearable_name, update__gte=startOfYtd).exists():
#                 caregiver = allAssignment.filter(wearable_name__exact=instance.wearable_name,update__gte=startOfYtd).order_by('update').first().name
#                 message = (str(instance.wearable_name.name)) + " in Center 1 is below 30% Battery, Recharge Required!, Assigned to " + caregiver
#             else:
#                 message= (str(instance.wearable_name.name)) + " in Center 1 is below 30% Battery, Recharge Required! No Caregiver Assigned yet"
#
#
#             if(str(instance.updated.date()) == str(datetime.today().date())):
#                 timestamp = "Today " + str(instance.updated)[11:19]
#             else:
#                 timestamp=datetime.strptime(str(instance.updated)[:19],'%Y-%m-%d %H:%M:%S').strftime("%d-%m-%Y %H:%M:%S")
#
#             masterList.append([messageType,message,timestamp])


# AlertActivated
    alertCounter = 0
    weeklyCounter = 0
    monthlyCounter = 0

    allAlertList = Alert.objects.all()

    for instanceAlert in allAlertList:
        alertUnique.append(instanceAlert)
    # there are many rows of data, this code will filter by each unique alert, arrange from newest to oldest data
    # and get the first one, aka the latest data


    # for alertObject in alertUnique: #take all sensors REMOVED FOR DEPLOYMENT
    #     if allAlertList.filter(detector__exact=alertObject.detector,datetime__gte=startOfYtd).exists():
    #         alertList.append(allAlertList.filter(detector__exact=alertObject.detector,datetime__gte=startOfYtd).order_by('datetime').first())
    # # take only sensorBattery objects, filter by sensor name to prevent repeats, filer by condition, order by datetime,take latest


    for alertObject in alertUnique: #take all sensors    FOR DEPLOYMENT
        if allAlertList.filter(detector__exact=alertObject.detector,datetime__range=(startOfToday,endOfToday),seen__exact=False).exists():
            alertCounter += 1


    # for instance in alertList:   REMOVED FOR DEPLOYMENT
    #
    #     messageType=""
    #     message=""
    #     timestamp = None
    #
    #     if(instance.seen==False):
    #         messageType="Alert"
    #         message="Alert Activated in Center 1 for "+ str(instance.detector.name)
    #
    #         if(str(instance.datetime.date()) == str(datetime.today().date())):
    #             timestamp = "Today " + str(instance.datetime)[11:19]
    #
    #             alertCounter += 1
    #
    #         else:
    #             timestamp=datetime.strptime(str(instance.datetime)[:19],'%Y-%m-%d %H:%M:%S').strftime("%d-%m-%Y %H:%M:%S")
    #
    #         masterList.append([messageType,message,timestamp])

        # if(instance.seen==True):
        #     messageType="Alert"
        #     message="Alert Acknowledged in Center 1! Alert Band "+ str(instance.wearable.name) #ack might not be implemented
        #
        #     if(str(instance.datetime.date()) == str(datetime.today().date())):
        #         timestamp = "Today " + str(instance.datetime)[11:19]
        #     else:
        #         timestamp=datetime.strptime(str(instance.datetime)[:19],'%Y-%m-%d %H:%M:%S').strftime("%d-%m-%Y %H:%M:%S")
        #
        #     masterList.append([messageType,message,timestamp])

            # get by alerts this week
    for alertObject in alertUnique:  # take all alerts for this week
        if (alertObject.datetime >= startOfWeek):
            if allAlertList.filter(detector__exact=alertObject.detector, datetime__range=(startOfWeek, endOfWeek)).exists():
                weeklyCounter +=1

    for alertObject in alertUnique:  # take all alerts for this Month
        if(alertObject.datetime >= thisMonthStart):
            if allAlertList.filter(detector__exact=alertObject.detector, datetime__range=(thisMonthStart,thisMonthEnd)).exists():
                monthlyCounter += 1

    #sort by time REMOVED FOR DEPLOYMENT, RETURN STATEMENT AS WELL
    # if len(masterList) > 0:
    #     newsFeedList = sorted(masterList, key=itemgetter(2))
    # else:
    #     newsFeedList = []

    return render(request, "dashboard.html",{'alertCounter': alertCounter,'weeklyCounter': weeklyCounter,'monthlyCounter': monthlyCounter, 'detectorCounter':detectorCounter,'wearableCounter': wearableCounter})


@login_required(login_url='')
def detector(request):
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
            DetectorUsage.objects.all().filter(detector_name__exact=detectorObject).order_by('-updated').first().used)


        detectorBattery.append(
            DetectorBattery.objects.all().filter(detector_name__exact=detectorObject).order_by('-updated').first().battery)

        detectorUpdated.append(DetectorUsage.objects.all().filter(detector_name__exact=detectorObject).order_by(
            '-updated').first().updated)

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
            action = "No action required"
        elif detectorBattery[count] > 30:
            action = "Recharge Required!"
        else:
            action = "Immediate Recharge Required!"

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
            WearableUsage.objects.all().filter(wearable_name__exact=wearableObject).order_by('-updated').first().used)

        wearableBattery.append(
            WearableBattery.objects.all().filter(wearable_name__exact=wearableObject).order_by(
                '-updated').first().battery)

        wearableUpdated.append(WearableUsage.objects.all().filter(wearable_name__exact=wearableObject).order_by(
            '-updated').first().updated)

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
            action = "No action required"
        elif wearableBattery[count] > 30:
            action = "Recharge Required!"
        else:
            action = "Immediate Recharge Required!"

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



@login_required(login_url='')
def data_analysis(request):
    return render(request, "data_analysis.html")

@login_required(login_url='')
def incident_reporting(request):
    return render(request, "incident_reporting.html")


@login_required(login_url='')
def incident_reporting_process(request):
    c = {}
    c.update(csrf(request))

    clientNameInput = request.POST['clientName']
    caregiverNameInput = request.POST['caregiverName']
    authorNameInput = request.POST['authorName']
    commentsInput = request.POST['comments']
    datetimeInput = datetime.strptime(request.POST['datetime'],'%d/%m/%Y %I:%M %p')

    incidentReport = IncidentReport(client_name=clientNameInput, caregiver_name=caregiverNameInput, author_name=authorNameInput, comments=commentsInput, datetime=datetimeInput)
    incidentReport.save()

    return render(request, 'incident_reporting.html', {'incidentReported': True})

@login_required(login_url='')
def data_analysis_query(request):
    c = {}
    c.update(csrf(request))

    dataTitle = request.POST.get('data_title',"EmptyTitle")
    dataType = request.POST.get('data_type',"EmptyType")

    startMonth = request.POST.get('datetimepicker1',1111) #month

    endMonth = request.POST.get('datetimepicker2',2222) #month
    #
    startWeek = request.POST.get('datetimepicker3',3333) #week
    endWeek = request.POST.get('datetimepicker4',4444) #week


    startDay = request.POST.get('datetimepicker5',5555) #day
    endDay = request.POST.get('datetimepicker6',6666) #day


    startTimeSlotDate = request.POST.get('datetimepicker7',7777) #timeslot date
    endTimeSlotDate = request.POST.get('datetimepicker8',8888)#timeslot date

    startTimeSlotTime = request.POST.get('start_time',9999) #timeslot time
    endTimeSlotTime = request.POST.get('end_time',1010) #timeslot time

    getType = None #0 = month  1 = week  2 = day  3 = timeslot
    getTitle = None
    # 0 =Highest Number of Alert   1 = Total Number of Alert   2= Highest Number of Incident Reported
    # 3 = Total Number of Incident Reported   #4 = Incident Reports

    alertQuery = Alert.objects.all()

    incidentQuery = IncidentReport.objects.all()

    labelList = [] #list of labels to be returned
    dataList = []  # FINAL LIST, sorted by criteria
    listOfMonths = []
    listOfDays = []
    listOfWeeks = []
    listOfTimeSlotDays = []


    # computing filter by WEEK
    if (dataType == "By Week"):
        dayS = startWeek[:2]
        monthS = startWeek[3:5]
        yearS = startWeek[6:]

        startDate =  yearS + "-" + monthS + "-" + dayS
        startDateTimeObject = datetime.strptime(startDate, '%Y-%m-%d')

        dayE = endWeek[:2]
        monthE = endWeek[3:5]
        yearE = endWeek[6:]

        endDate = yearE + "-" + monthE + "-" + dayE
        endDateTimeObject = datetime.strptime(endDate, '%Y-%m-%d')

        startWeekNumber = startDateTimeObject.isocalendar()[1] #Return a 3-tuple, (ISO year, ISO week number, ISO weekday)
        endWeekNumber = endDateTimeObject.isocalendar()[1]
        numberOfWeeks = endWeekNumber - startWeekNumber + 1 #inclusive

        counter = 0

        while (counter < numberOfWeeks):  # for each count, add 7 days to the startDate and add to the list of weeks,labels to be start date of every week (monday)
            # new = startDateTimeObject.replace(day=(startDateTimeObject.day + (counter * 7) ) )
            new = startDateTimeObject + timedelta(days=(counter * 7) )
            listOfWeeks.append(new)
            labelList.append(new.strftime("%d %b %Y"))
            counter += 1

        if (dataTitle == "Total Number of Alert" or dataTitle == "Highest Number of Alert"):  # if alerts
            selectedQuery = alertQuery
        else: # (dataTitle == "Highest Number of Incident Reported" or dataTitle == "Total Number of Incident Reported"):  # if incident reports
            selectedQuery = incidentQuery


        for eachStartOFWeek in listOfWeeks:  # each day, count the number of objects occur on that day
            # eachEndOfWeek = eachStartOFWeek.replace(day=(eachStartOFWeek.day + (4) ) )
            eachEndOfWeek = eachStartOFWeek + timedelta(days=4)
            countForWeek = (  selectedQuery.filter(datetime__range=(eachStartOFWeek,eachEndOfWeek)  )  ).count()
            dataList.append(countForWeek)

        if (dataTitle == "Highest Number of Alert" or dataTitle == "Highest Number of Incident Reported"):  # if need to sort by Highest Alert or Highest Incident Reports
            dataList, labelList = (list(t) for t in zip(*sorted(zip(dataList, labelList), reverse=True)))

        return render(request, 'data_analysis.html',{'dataList': dataList, 'labels': labelList, 'dataTitle': dataTitle + ',', 'dataType': dataType,'start': ' From: ' + startWeek, 'end': ' To: '+ endWeek})

    #computing filter by DAY
    if(dataType == "By Day"):
        dayS = startDay[:2]
        monthS = startDay[3:5]
        yearS = startDay[6:]

        startDate =  yearS + "-" + monthS + "-" + dayS
        startDateTimeObject = datetime.strptime(startDate, '%Y-%m-%d')

        dayE = endDay[:2]
        monthE = endDay[3:5]
        yearE = endDay[6:]

        endDate = yearE + "-" + monthE + "-" + dayE
        endDateTimeObject = datetime.strptime(endDate, '%Y-%m-%d')

        numberOfDays = abs( (endDateTimeObject - startDateTimeObject).days) + 1 #timedelta object.days, result should be int,inclusive

        counter = 0

        while(counter < numberOfDays): #for each count, add 1 to the month and add to the list of months
            new = startDateTimeObject + timedelta(days=counter)
            listOfDays.append(new)
            labelList.append(new.strftime("%d %b %Y"))
            counter += 1

        if (dataTitle == "Total Number of Alert" or dataTitle == "Highest Number of Alert"):  # if alerts
            selectedQuery = alertQuery
        else: # (dataTitle == "Highest Number of Incident Reported" or dataTitle == "Total Number of Incident Reported"):  # if incident reports
            selectedQuery = incidentQuery

        for eachDay in listOfDays:  # each day, count the number of objects occur on that day
            countForDay = (selectedQuery.filter(datetime__startswith=eachDay.date)).count()
            dataList.append(countForDay)

        if (dataTitle == "Highest Number of Alert" or dataTitle == "Highest Number of Incident Reported"):  # if need to sort by Highest Alert or Highest Incident Reports
            dataList, labelList = (list(t) for t in zip(*sorted(zip(dataList, labelList), reverse=True)))

        return render(request, 'data_analysis.html',{'dataList': dataList, 'labels': labelList, 'dataTitle': dataTitle + ',', 'dataType': dataType,'start': ' From: ' + startDay, 'end': ' To: ' + endDay})

    #computing filter by MONTH
    if (dataType == "By Month" ):
        #01/2016 is given by the input

        monthE = endMonth[:2]  # 01
        yearE = endMonth[3:] #2016

        temp = calendar.monthrange(int(yearE), int(monthE))  # (1,31) returns a tuple
        lastDayOfMonth = temp[1] #31

        endDate = yearE + "-" + monthE + "-" + str(lastDayOfMonth) + " 23:59" #2016-01-31 23:59

        endDateTimeObject = datetime.strptime(endDate, '%Y-%m-%d %H:%M')



        #01/2016
        monthS = startMonth[:2] #01
        yearS = startMonth[3:] #2016

        startDate = yearS + "-" + monthS + "-01" + " 00:00" #2016-01-01 00:00

        startDateTimeObject = datetime.strptime(startDate, '%Y-%m-%d %H:%M')



        numberOfMonths = int(monthE) - int(monthS) + 1 #inclusive
        numberOfYears = 0 #container
        if(numberOfMonths < 0):
            numberOfYears = int(yearE) - int(yearS) -1 #if 2016/01 to 2015/12? monthE - monthS = -11 months
            numberOfMonths = 12 + numberOfMonths #2 months
        else:
            numberOfYears = int(yearE) - int(yearS)
        totalNumberOfMonths = numberOfYears * 12 + numberOfMonths #get number of months to determine the list of months


        firstDayOfStartDateTime= startDateTimeObject.replace(day=1) #all become 1st of the month


        counter = 0

        while(counter < totalNumberOfMonths): #for each count, add 1 to the month and add to the list of months
            # new = firstDayOfStartDateTime.replace(month=(firstDayOfStartDateTime.month + counter))
            new = firstDayOfStartDateTime + timedelta(days=(counter * 31) ) #by pass limitation, timedelta only allows days, adding 31 ensures date is in the next month
            listOfMonths.append(new)
            labelList.append(new.strftime("%b %Y"))
            counter += 1


        if (dataTitle == "Total Number of Alert" or dataTitle == "Highest Number of Alert"):  # if alerts
            selectedQuery = alertQuery
        else: # (dataTitle == "Highest Number of Incident Reported" or dataTitle == "Total Number of Incident Reported"):  # if incident reports
            selectedQuery = incidentQuery

        for eachMonth in listOfMonths: #each month, count the number of objects that is the same as the month
            countForMonth = (selectedQuery.filter(datetime__month=eachMonth.month)).count()
            dataList.append(countForMonth)


        if(dataTitle == "Highest Number of Alert" or dataTitle == "Highest Number of Incident Reported"): #if need to sort by Highest Alert or Highest Incident Reports
            dataList, labelList = (list(t) for t in zip(*sorted(zip(dataList, labelList),reverse=True)))


        return render(request, 'data_analysis.html',{'dataList': dataList, 'labels': labelList, 'dataTitle': dataTitle + ',', 'dataType': dataType,'start': ' From: ' + startMonth, 'end': ' To: ' + endMonth})

    #filter by TimeSlot
    if (dataType == "By Timeslot"):
        dayS = startTimeSlotDate[:2]
        monthS = startTimeSlotDate[3:5]
        yearS = startTimeSlotDate[6:]


        startDate = yearS + "-" + monthS + "-" + dayS
        startDateTimeObject = datetime.strptime(startDate, '%Y-%m-%d')


        dayE = endTimeSlotDate[:2]
        monthE = endTimeSlotDate[3:5]
        yearE = endTimeSlotDate[6:]

        endDate = yearE + "-" + monthE + "-" + dayE
        endDateTimeObject = datetime.strptime(endDate, '%Y-%m-%d')

        numberOfDays = abs((endDateTimeObject - startDateTimeObject).days) + 1  # timedelta object.days, result should be int,inclusive

        counter = 0

        while (counter < numberOfDays):  # for each count, add 1 to the month and add to the list of months
            new = startDateTimeObject + timedelta(days=counter)
            listOfTimeSlotDays.append(new)
            labelList.append(new.strftime("%d %b %Y"))
            counter += 1

        if (dataTitle == "Total Number of Alert" or dataTitle == "Highest Number of Alert"):  # if alerts
            selectedQuery = alertQuery
        else: # (dataTitle == "Highest Number of Incident Reported" or dataTitle == "Total Number of Incident Reported"):  # if incident reports
            selectedQuery = incidentQuery

        #filter by timeslot

        for eachDay in listOfTimeSlotDays:  # each day, count the number of objects occur on that day
            currentDate = eachDay.strftime('%Y-%m-%d') #get string
            startRange = datetime.strptime(currentDate + " " + str(startTimeSlotTime),'%Y-%m-%d %I:%M %p') #for each date, add the start time
            endRange = datetime.strptime(currentDate + " " + str(endTimeSlotTime),'%Y-%m-%d %I:%M %p') #for each date, add the end time
            countForEachDayTimeSlot = (selectedQuery.filter(datetime__range=(startRange,endRange))).count()
            dataList.append(countForEachDayTimeSlot)

        if(dataTitle == "Highest Number of Alert" or dataTitle == "Highest Number of Incident Reported"):  # if need to sort by Highest Alert or Highest Incident Reports
            dataList, labelList = (list(t) for t in zip(*sorted(zip(dataList, labelList), reverse=True)))

        #strings for Title on return
        start = "From: " + dayS + "/" + monthS + "/" + yearS + " To: " + dayE + "/" + monthE + "/" + yearE + ","
        end = str(startTimeSlotTime) +" To "+ str(endTimeSlotTime)

        return render(request, 'data_analysis.html',{'dataList': dataList, 'labels': labelList, 'dataTitle': dataTitle + ',', 'dataType': dataType,'start':start,'end':end})

    else:
        return render (request,'data_analysis.html')


@login_required(login_url='')
def view_incident_reports(request):
    c = {}
    c.update(csrf(request))

    runAlready = False

    start = request.POST.get('datetimepicker1', 'nothing')  # startDate

    end = request.POST.get('datetimepicker2', 'nothing')  # endDate

    if start != 'nothing':
        runAlready = True

        incidentList = IncidentReport.objects.all()

        wantedReports = []
        listToReturn = []

        dayS = start[:2]
        monthS = start[3:5]
        yearS = start[6:]

        startDate = yearS + "-" + monthS + "-" + dayS + " 00:00:00"
        startDateTimeObject = datetime.strptime(startDate, '%Y-%m-%d %H:%M:%S')

        dayE = end[:2]
        monthE = end[3:5]
        yearE = end[6:]

        endDate = yearE + "-" + monthE + "-" + dayE + " 23:59:59"
        endDateTimeObject = datetime.strptime(endDate, '%Y-%m-%d %H:%M:%S')

        if incidentList.filter(datetime__range=(startDateTimeObject, endDateTimeObject)).exists():
            wantedReports.append(incidentList.filter(datetime__range=(startDateTimeObject, endDateTimeObject)).order_by('datetime'))


            title = 'Displaying Incident Reports from ' + dayS + "-" + monthS + "-" + yearS+ ' to ' + dayE + "-" + monthE + "-" + yearE

            for eachReport in wantedReports[0]:
                clientName = eachReport.client_name
                caregiverName = eachReport.caregiver_name
                authorName = eachReport.author_name
                dateTime = str(eachReport.datetime)
                comments = eachReport.comments
                listToReturn.append(
                    [str(clientName), str(caregiverName), str(authorName), dateTime, str(comments)])  # already sorted by datetime

            return render(request, "view_incident_reports.html", {'dataSet': listToReturn, 'title': title, 'runAlready': runAlready})


        else:
            title = 'No Data to Display'

            return render(request, "view_incident_reports.html", {'dataSet': listToReturn, 'title': title,'runAlready':runAlready})

    else:
        return render(request,"view_incident_reports.html",{'runAlready':runAlready})


@login_required(login_url='')
def incident_reports_table(request):
    return render(request, "incident_reports_table.html")

# @login_required(login_url='') #Highest Number of Alert,By Month From: 01/2016 To: 10/2016
#                               #Total Number of Alert,By Timeslot From: 05/10/2016 To: 24/10/2016, 12:00 PM To 5:00 PM
# def download_csv(request):
#     title = str(request.POST['clientName'])
#     dataTitle = (title.split(","))[0] #Highest Number of Alert
#     remainder1 = ((title.split(","))[1])
#
#     if (title.split(","))[2] != None: # 12:00 PM To 5:00 PM
#         fromDate =
#         toDate =
#
#
#     tempList = remainder1.split(":")
#     dataType = (tempList[0])[:-5] #is By Month From
#
#     if dataType =="By Timeslot":
#
#
#     fromDate = (tempList[1])[1:-3] #is <space> 01/2016 to
#     toDate= (tempList[2])[1:] #is <space> 10/2016
#
#     alertQuery = Alert.objects.all()
#
#     incidentQuery = IncidentReport.objects.all()
#
#     labelList = []  # list of labels to be returned
#     dataList = []  # FINAL LIST, sorted by criteria
#     listOfMonths = []
#     listOfDays = []
#     listOfWeeks = []
#     listOfTimeSlotDays = []
#
#     # computing filter by WEEK
#     if (dataType == "By Week"):
#         dayS = fromDate[:2]
#         monthS = fromDate[3:5]
#         yearS = fromDate[6:]
#
#         startDate = yearS + "-" + monthS + "-" + dayS
#         startDateTimeObject = datetime.strptime(startDate, '%Y-%m-%d')
#
#         dayE = endDate[:2]
#         monthE = endDate[3:5]
#         yearE = endDate[6:]
#
#         endDate = yearE + "-" + monthE + "-" + dayE
#         endDateTimeObject = datetime.strptime(endDate, '%Y-%m-%d')
#
#         startWeekNumber = startDateTimeObject.isocalendar()[
#             1]  # Return a 3-tuple, (ISO year, ISO week number, ISO weekday)
#         endWeekNumber = endDateTimeObject.isocalendar()[1]
#         numberOfWeeks = endWeekNumber - startWeekNumber + 1  # inclusive
#
#         counter = 0
#
#         while (
#             counter < numberOfWeeks):  # for each count, add 7 days to the startDate and add to the list of weeks,labels to be start date of every week (monday)
#             # new = startDateTimeObject.replace(day=(startDateTimeObject.day + (counter * 7) ) )
#             new = startDateTimeObject + timedelta(days=(counter * 7))
#             listOfWeeks.append(new)
#             labelList.append(new.strftime("%d %b %Y"))
#             counter += 1
#
#         if (dataTitle == "Total Number of Alert" or dataTitle == "Highest Number of Alert"):  # if alerts
#             selectedQuery = alertQuery
#         else:  # (dataTitle == "Highest Number of Incident Reported" or dataTitle == "Total Number of Incident Reported"):  # if incident reports
#             selectedQuery = incidentQuery
#
#         for eachStartOFWeek in listOfWeeks:  # each day, count the number of objects occur on that day
#             # eachEndOfWeek = eachStartOFWeek.replace(day=(eachStartOFWeek.day + (4) ) )
#             eachEndOfWeek = eachStartOFWeek + timedelta(days=4)
#             countForWeek = (selectedQuery.filter(datetime__range=(eachStartOFWeek, eachEndOfWeek))).count()
#             dataList.append(countForWeek)
#
#         if (
#                 dataTitle == "Highest Number of Alert" or dataTitle == "Highest Number of Incident Reported"):  # if need to sort by Highest Alert or Highest Incident Reports
#             dataList, labelList = (list(t) for t in zip(*sorted(zip(dataList, labelList), reverse=True)))
#
#         return render(request, 'data_analysis.html',
#                       {'dataList': dataList, 'labels': labelList, 'dataTitle': dataTitle + ',', 'dataType': dataType,
#                        'start': ' From: ' + startWeek, 'end': ' To: ' + endWeek})
#
#     # computing filter by DAY
#     if (dataType == "By Day"):
#         dayS = startDay[:2]
#         monthS = startDay[3:5]
#         yearS = startDay[6:]
#
#         startDate = yearS + "-" + monthS + "-" + dayS
#         startDateTimeObject = datetime.strptime(startDate, '%Y-%m-%d')
#
#         dayE = endDay[:2]
#         monthE = endDay[3:5]
#         yearE = endDay[6:]
#
#         endDate = yearE + "-" + monthE + "-" + dayE
#         endDateTimeObject = datetime.strptime(endDate, '%Y-%m-%d')
#
#         numberOfDays = abs(
#             (endDateTimeObject - startDateTimeObject).days) + 1  # timedelta object.days, result should be int,inclusive
#
#         counter = 0
#
#         while (counter < numberOfDays):  # for each count, add 1 to the month and add to the list of months
#             new = startDateTimeObject + timedelta(days=counter)
#             listOfDays.append(new)
#             labelList.append(new.strftime("%d %b %Y"))
#             counter += 1
#
#         if (dataTitle == "Total Number of Alert" or dataTitle == "Highest Number of Alert"):  # if alerts
#             selectedQuery = alertQuery
#         else:  # (dataTitle == "Highest Number of Incident Reported" or dataTitle == "Total Number of Incident Reported"):  # if incident reports
#             selectedQuery = incidentQuery
#
#         for eachDay in listOfDays:  # each day, count the number of objects occur on that day
#             countForDay = (selectedQuery.filter(datetime__startswith=eachDay.date)).count()
#             dataList.append(countForDay)
#
#         if (
#                 dataTitle == "Highest Number of Alert" or dataTitle == "Highest Number of Incident Reported"):  # if need to sort by Highest Alert or Highest Incident Reports
#             dataList, labelList = (list(t) for t in zip(*sorted(zip(dataList, labelList), reverse=True)))
#
#         return render(request, 'data_analysis.html',
#                       {'dataList': dataList, 'labels': labelList, 'dataTitle': dataTitle + ',', 'dataType': dataType,
#                        'start': ' From: ' + startDay, 'end': ' To: ' + endDay})
#
#     # computing filter by MONTH
#     if (dataType == "By Month"):
#         # 01/2016 is given by the input
#
#         monthE = endMonth[:2]  # 01
#         yearE = endMonth[3:]  # 2016
#
#         temp = calendar.monthrange(int(yearE), int(monthE))  # (1,31) returns a tuple
#         lastDayOfMonth = temp[1]  # 31
#
#         endDate = yearE + "-" + monthE + "-" + str(lastDayOfMonth) + " 23:59"  # 2016-01-31 23:59
#
#         endDateTimeObject = datetime.strptime(endDate, '%Y-%m-%d %H:%M')
#
#         # 01/2016
#         monthS = startMonth[:2]  # 01
#         yearS = startMonth[3:]  # 2016
#
#         startDate = yearS + "-" + monthS + "-01" + " 00:00"  # 2016-01-01 00:00
#
#         startDateTimeObject = datetime.strptime(startDate, '%Y-%m-%d %H:%M')
#
#         numberOfMonths = int(monthE) - int(monthS) + 1  # inclusive
#         numberOfYears = 0  # container
#         if (numberOfMonths < 0):
#             numberOfYears = int(yearE) - int(yearS) - 1  # if 2016/01 to 2015/12? monthE - monthS = -11 months
#             numberOfMonths = 12 + numberOfMonths  # 2 months
#         else:
#             numberOfYears = int(yearE) - int(yearS)
#         totalNumberOfMonths = numberOfYears * 12 + numberOfMonths  # get number of months to determine the list of months
#
#         firstDayOfStartDateTime = startDateTimeObject.replace(day=1)  # all become 1st of the month
#
#         counter = 0
#
#         while (counter < totalNumberOfMonths):  # for each count, add 1 to the month and add to the list of months
#             # new = firstDayOfStartDateTime.replace(month=(firstDayOfStartDateTime.month + counter))
#             new = firstDayOfStartDateTime + timedelta(days=(
#             counter * 31))  # by pass limitation, timedelta only allows days, adding 31 ensures date is in the next month
#             listOfMonths.append(new)
#             labelList.append(new.strftime("%b %Y"))
#             counter += 1
#
#         if (dataTitle == "Total Number of Alert" or dataTitle == "Highest Number of Alert"):  # if alerts
#             selectedQuery = alertQuery
#         else:  # (dataTitle == "Highest Number of Incident Reported" or dataTitle == "Total Number of Incident Reported"):  # if incident reports
#             selectedQuery = incidentQuery
#
#         for eachMonth in listOfMonths:  # each month, count the number of objects that is the same as the month
#             countForMonth = (selectedQuery.filter(datetime__month=eachMonth.month)).count()
#             dataList.append(countForMonth)
#
#         if (
#                 dataTitle == "Highest Number of Alert" or dataTitle == "Highest Number of Incident Reported"):  # if need to sort by Highest Alert or Highest Incident Reports
#             dataList, labelList = (list(t) for t in zip(*sorted(zip(dataList, labelList), reverse=True)))
#
#         return render(request, 'data_analysis.html',
#                       {'dataList': dataList, 'labels': labelList, 'dataTitle': dataTitle + ',', 'dataType': dataType,
#                        'start': ' From: ' + startMonth, 'end': ' To: ' + endMonth})
#
#     # filter by TimeSlot
#     if (dataType == "By Timeslot"):
#         dayS = startTimeSlotDate[:2]
#         monthS = startTimeSlotDate[3:5]
#         yearS = startTimeSlotDate[6:]
#
#         startDate = yearS + "-" + monthS + "-" + dayS
#         startDateTimeObject = datetime.strptime(startDate, '%Y-%m-%d')
#
#         dayE = endTimeSlotDate[:2]
#         monthE = endTimeSlotDate[3:5]
#         yearE = endTimeSlotDate[6:]
#
#         endDate = yearE + "-" + monthE + "-" + dayE
#         endDateTimeObject = datetime.strptime(endDate, '%Y-%m-%d')
#
#         numberOfDays = abs(
#             (endDateTimeObject - startDateTimeObject).days) + 1  # timedelta object.days, result should be int,inclusive
#
#         counter = 0
#
#         while (counter < numberOfDays):  # for each count, add 1 to the month and add to the list of months
#             new = startDateTimeObject + timedelta(days=counter)
#             listOfTimeSlotDays.append(new)
#             labelList.append(new.strftime("%d %b %Y"))
#             counter += 1
#
#         if (dataTitle == "Total Number of Alert" or dataTitle == "Highest Number of Alert"):  # if alerts
#             selectedQuery = alertQuery
#         else:  # (dataTitle == "Highest Number of Incident Reported" or dataTitle == "Total Number of Incident Reported"):  # if incident reports
#             selectedQuery = incidentQuery
#
#         # filter by timeslot
#
#         for eachDay in listOfTimeSlotDays:  # each day, count the number of objects occur on that day
#             currentDate = eachDay.strftime('%Y-%m-%d')  # get string
#             startRange = datetime.strptime(currentDate + " " + str(startTimeSlotTime),
#                                            '%Y-%m-%d %I:%M %p')  # for each date, add the start time
#             endRange = datetime.strptime(currentDate + " " + str(endTimeSlotTime),
#                                          '%Y-%m-%d %I:%M %p')  # for each date, add the end time
#             countForEachDayTimeSlot = (selectedQuery.filter(datetime__range=(startRange, endRange))).count()
#             dataList.append(countForEachDayTimeSlot)
#
#         if (
#                 dataTitle == "Highest Number of Alert" or dataTitle == "Highest Number of Incident Reported"):  # if need to sort by Highest Alert or Highest Incident Reports
#             dataList, labelList = (list(t) for t in zip(*sorted(zip(dataList, labelList), reverse=True)))
#
#         # strings for Title on return
#         start = "From " + dayS + "/" + monthS + "/" + yearS + " To " + dayE + "/" + monthE + "/" + yearE + ","
#         end = str(startTimeSlotTime) + " To " + str(endTimeSlotTime)
#
#         return render(request, 'data_analysis.html',
#                       {'dataList': dataList, 'labels': labelList, 'dataTitle': dataTitle + ',', 'dataType': dataType,
#                        'start': start, 'end': end})
#
#     else:
#         return render(request, 'data_analysis.html')

@login_required(login_url='') #pass the entire DataSet over
def download_csv(request):
    allList = str(request.POST['download'])
    allList = (allList.replace("[","").replace("]","")).split('&')
    dataList = allList[0].split(',')
    labels = (allList[1].replace("'","")).split(',')

    fileName = (datetime.now()).strftime('%d-%b-%Y %I-%M%p')

    dataFile = open(fileName + '.csv', "w")
    writer = csv.writer(dataFile,delimiter=',',quoting=csv.QUOTE_NONE)

    combined = [labels,dataList]
    writer.writerows(combined)

    dataFile.close()


    return render(request, 'data_analysis.html',{'dataRecieved':labels})