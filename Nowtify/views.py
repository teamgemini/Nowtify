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
from django.http import HttpResponse


def custom_login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect("dashboard")
    else:
        return login(request)


def login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect("dashboard")

    return render(request, "login.html", {})


def logout(request): # direct to login. html upon clicking logout
    auth_logout(request)
    c = {}
    c.update(csrf(request)) #session token
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
    current_user_pw = request.POST['current_password'] #get input
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
def dashboard(request):

    masterList= []

    detectorUsage = []
    detectorBattery = []
    detectorCounter = 0

    alertList= []

    startOfYtd = (datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0) #yesterday's 00:00:00

    startOfWeekNum = 1
    daysAfterStartOfWeek = 0
    endOfWeekNum = 7 # not used, for reference

    if datetime.now().isoweekday == 1:
        daysAfterStartOfWeek = 0

    if datetime.now().isoweekday() > 1:
        daysAfterStartOfWeek = datetime.now().isoweekday() - 1 #if 4, 4-3 = 1 which is monday
    #get start of week (monday) 00:00:00:00

    startOfWeek = (datetime.now() - timedelta(days=daysAfterStartOfWeek)).replace(hour=0, minute=0, second=0, microsecond=0) #datetime for 00:00 startofweek

    if(datetime.now().isoweekday() < 7): #determine how many days till end of week
        daysToEndOfWeek = 7 - (datetime.now().isoweekday())

    if(datetime.now().isoweekday() == 7):
        daysToEndOfWeek = 0

    #get end of week (sunday) 23:59:59:59
    endOfWeek = (datetime.now() + timedelta(days=daysToEndOfWeek)).replace(hour=23, minute=59, second=59, microsecond=59)

    startOfMonth = 1 #getting datetime for start/end of day, week, month
    today = datetime.now()
    startOfToday = (datetime.now()).replace(hour=0, minute=0, second=0, microsecond=0)
    endOfToday = (datetime.now()).replace(hour=23, minute=59, second=59, microsecond=59)
    thisMonthNum = today.month
    thisYearNum = today.year
    thisMonthEndNum = str(calendar.monthrange(thisYearNum,thisMonthNum)[1])
    thisMonthStartNum = "1"
    thisMonthStart = datetime.strptime(thisMonthStartNum + "/" + str(thisMonthNum)+ "/" + str(thisYearNum) + " 00:00:00", "%d/%m/%Y %H:%M:%S")
    thisMonthEnd = datetime.strptime(thisMonthEndNum + "/" + str(thisMonthNum) + "/" + str(thisYearNum) + " 23:59:59", "%d/%m/%Y %H:%M:%S")


    for detectorObject in Detector.objects.all():
        try:
            detectorUsage.append(DetectorUsage.objects.filter(detector_name__exact=detectorObject,updated__range=(startOfToday,endOfToday)).order_by('-updated').first()) # order by time only for ON OFF
        except:
            pass
        try:
            detectorBattery.append(DetectorBattery.objects.filter(detector_name__exact=detectorObject,updated__gte=startOfYtd).order_by('-updated').first())
        except:
            pass

    # order by time only for ON OFF
    for instance in detectorUsage:
        try:
            if instance.used == True:
                detectorCounter += 1

            if instance.used:
                messageType = "Sensor"
                message=str(instance.detector_name.name) + " in Center 1 is in operation."

                if(str(instance.updated.date()) == str(datetime.today().date())):
                    timestamp = "Today " + str(instance.updated)[11:19]
                else:
                    timestamp=datetime.strptime(str(instance.updated)[:19],'%Y-%m-%d %H:%M:%S').strftime("%d-%m-%Y %H:%M:%S")

                masterList.append([messageType,message,timestamp])
            else:
                messageType = "Sensor"
                message = str(instance.detector_name.name) + " in Center 1 is not in operation."

                if(str(instance.updated.date()) == str(datetime.today().date())):
                    timestamp = "Today " + str(instance.updated)[11:19]
                else:
                    timestamp = datetime.strptime(str(instance.updated)[:19],'%Y-%m-%d %H:%M:%S').strftime("%d-%m-%Y %H:%M:%S")
                masterList.append([messageType,message,timestamp])
        except:
            pass


    for instance in detectorBattery: #prepare messageType, message and timestamp of each occurance, display newsfeed and counter in html

        try:
            if(instance.battery)<= 40:
                messageType="Sensor"
                message=str(instance.detector_name.name) + " in Center 1 is below 40% Battery, Recharge Required!"

                if(str(instance.updated.date()) == str(datetime.today().date())):
                    timestamp = "Today " + str(instance.updated)[11:19]
                else:
                    timestamp=datetime.strptime(str(instance.updated)[:19],'%Y-%m-%d %H:%M:%S').strftime("%d-%m-%Y %H:%M:%S")

                masterList.append([messageType,message,timestamp])
        except:
            pass


    alertCounter = Alert.objects.filter(datetime__range=(startOfToday,endOfToday),seen__exact=False).count()
    weeklyCounter = Alert.objects.filter(datetime__range=(startOfWeek, endOfWeek)).count()
    monthlyCounter = Alert.objects.filter(datetime__range=(thisMonthStart,thisMonthEnd)).count()

    for instance in Alert.objects.filter(datetime__range=(startOfToday,endOfToday)).order_by('-datetime')[:5]:  #prepare data to pass to newsfeed in html page
        try:
            messageType="Alert"
            message="Alert Activated in Center 1 for " + str(instance.detector.name) + "."
            if(str(instance.datetime.date()) == str(datetime.today().date())):
                timestamp = "Today " + str(instance.datetime)[11:19]
            else:
                timestamp=datetime.strptime(str(instance.datetime)[:19],'%Y-%m-%d %H:%M:%S').strftime("%d-%m-%Y %H:%M:%S")

            masterList.append([messageType,message,timestamp])
        except:
            pass

    # sort by time
    if len(masterList) > 0:
        newsFeedList = sorted(masterList, key=itemgetter(2))[::-1]
    else:
        newsFeedList = []

    return render(request, "dashboard.html",{'dataSet': newsFeedList, 'alertCounter': alertCounter,'weeklyCounter': weeklyCounter,'monthlyCounter': monthlyCounter, 'detectorCounter':detectorCounter})


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


@login_required(login_url='') #nolonger used, use of Miband deprecated
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
        # take only Assignment objects, filter by name to prevent repeats, filer by condition, order by datetime,take latest
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
            # take only Assignment objects, filter by name to prevent repeats, filer by condition, order by datetime,take latest
        else:
            instanceAssignee = "Not Assigned"
        wearableAssignment.append([instanceName,instanceAssignee])

    return render(request, "alert_bands.html", {'dataSet': wearableData, 'wearableNames': wearableAssignment})


@login_required(login_url='')
def update_assignment(request): #allows assignment of caregiver name to wearable to be changed #no longer used, use of Miband deprecated
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

    # get wearable uniquely
    for instance in Wearable.objects.all():
        wearableUnique.append(instance)

    for wearableObject in wearableUnique:

        if Assignment.objects.all().filter(wearable_name__exact=wearableObject).exists():
            wearableAssignment.append(
                str(Assignment.objects.all().filter(wearable_name__exact=wearableObject).first().name)
                # take only Assignment objects, filter by name to prevent repeats, filer by condition, order by datetime,take latest
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
    for wearableObject in wearableUnique: #passdata to be printed to alert_band.html, based on on/off and battery levels

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
def data_analysis(request):
    return render(request, "data_analysis.html")

@login_required(login_url='')
def incident_reporting(request):
    return render(request, "incident_reporting.html")


@login_required(login_url='')
def incident_reporting_process(request):
    c = {}
    c.update(csrf(request))

    clientNameInput = request.POST['clientName'] #get all data from html
    caregiverNameInput = request.POST['caregiverName']
    authorNameInput = request.POST['authorName']
    commentsInput = request.POST['comments']
    datetimeInput = datetime.strptime(request.POST['datetime'],'%d/%m/%Y %I:%M %p')

    incidentReport = IncidentReport(client_name=clientNameInput, caregiver_name=caregiverNameInput, author_name=authorNameInput, comments=commentsInput, datetime=datetimeInput)
    incidentReport.save() #write to DB

    return render(request, 'incident_reporting.html', {'incidentReported': True})

@login_required(login_url='')
def data_analysis_query(request):
    c = {}
    c.update(csrf(request))

    dataTitle = request.POST.get('data_title',"EmptyTitle")
    dataType = request.POST.get('data_type',"EmptyType")

    startMonth = request.POST.get('datetimepicker1',1111) #month #1111 is value to be returned if null is found

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

    alertQuery = Alert.objects.all()

    incidentQuery = IncidentReport.objects.all()

    labelList = [] #list of labels to be returned
    dataList = []  # FINAL LIST, sorted by criteria
    listOfMonths = []
    listOfDays = []
    listOfWeeks = []
    listOfTimeSlotDays = []


    # computing filter by WEEK
    if (dataType == "By Week"): #dayS is chosen start day.
        dayS = startWeek[:2]
        monthS = startWeek[3:5]
        yearS = startWeek[6:]

        startDate =  yearS + "-" + monthS + "-" + dayS
        startDateTimeObject = datetime.strptime(startDate, '%Y-%m-%d')#get start datetime object

        dayE = endWeek[:2]
        monthE = endWeek[3:5]
        yearE = endWeek[6:]

        endDate = yearE + "-" + monthE + "-" + dayE
        endDateTimeObject = datetime.strptime(endDate, '%Y-%m-%d')#get end datetime object

        startWeekNumber = startDateTimeObject.isocalendar()[1] #Return a 3-tuple, (ISO year, ISO week number, ISO weekday)
        endWeekNumber = endDateTimeObject.isocalendar()[1]
        numberOfWeeks = endWeekNumber - startWeekNumber + 1 #inclusive

        counter = 0

        while (counter < numberOfWeeks):  # for each count, add 7 days to the startDate and add to the list of weeks,labels to be start date of every week (monday)
            new = startDateTimeObject + timedelta(days=(counter * 7) )
            listOfWeeks.append(new)
            labelList.append(new.strftime("%d %b %Y"))
            counter += 1

        if (dataTitle == "Total Number of Alert" or dataTitle == "Highest Number of Alert"):  # if alerts
            selectedQuery = alertQuery
        else: # if incident reports
            selectedQuery = incidentQuery


        for eachStartOFWeek in listOfWeeks:  # each day, count the number of objects occur on that day
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
        startDateTimeObject = datetime.strptime(startDate, '%Y-%m-%d') #get start datetime object

        dayE = endDay[:2]
        monthE = endDay[3:5]
        yearE = endDay[6:]

        endDate = yearE + "-" + monthE + "-" + dayE
        endDateTimeObject = datetime.strptime(endDate, '%Y-%m-%d') #get end datetime object

        numberOfDays = abs( (endDateTimeObject - startDateTimeObject).days) + 1 #timedelta object.days, result should be int,inclusive

        counter = 0

        while(counter < numberOfDays): #for each count, add 1 to the month and add to the list of months
            new = startDateTimeObject + timedelta(days=counter)
            listOfDays.append(new)
            labelList.append(new.strftime("%d %b %Y"))
            counter += 1

        if (dataTitle == "Total Number of Alert" or dataTitle == "Highest Number of Alert"):  # if alerts
            selectedQuery = alertQuery
        else:# if incident reports
            selectedQuery = incidentQuery

        for eachDay in listOfDays:  # each day, count the number of objects occur on that day
            countForDay = (selectedQuery.filter(datetime__startswith=eachDay.date)).count()
            dataList.append(countForDay)

        if (dataTitle == "Highest Number of Alert" or dataTitle == "Highest Number of Incident Reported"):  # if need to sort by Highest Alert or Highest Incident Reports
            dataList, labelList = (list(t) for t in zip(*sorted(zip(dataList, labelList), reverse=True)))

        return render(request, 'data_analysis.html',{'dataList': dataList, 'labels': labelList, 'dataTitle': dataTitle + ',', 'dataType': dataType,'start': ' From: ' + startDay, 'end': ' To: ' + endDay})

    #computing filter by MONTH
    if (dataType == "By Month" ):
        #for example, 01/2016 is given by the input

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
            new = firstDayOfStartDateTime + timedelta(days=(counter * 31) ) #by pass limitation, timedelta only allows days, adding 31 ensures date is in the next month
            listOfMonths.append(new)
            labelList.append(new.strftime("%b %Y"))
            counter += 1


        if (dataTitle == "Total Number of Alert" or dataTitle == "Highest Number of Alert"):  # if alerts
            selectedQuery = alertQuery
        else: # if incident reports
            selectedQuery = incidentQuery

        for eachMonth in listOfMonths: #each month, count the number of objects that is the same as the month
            countForMonth = (selectedQuery.filter(datetime__month=eachMonth.month)).count()
            dataList.append(countForMonth)


        if(dataTitle == "Highest Number of Alert" or dataTitle == "Highest Number of Incident Reported"): #if need to sort by Highest Alert or Highest Incident Reports
            dataList, labelList = (list(t) for t in zip(*sorted(zip(dataList, labelList),reverse=True)))


        return render(request, 'data_analysis.html',{'dataList': dataList, 'labels': labelList, 'dataTitle': dataTitle + ',', 'dataType': dataType,'start': ' From: ' + startMonth, 'end': ' To: ' + endMonth})

    #filter by TimeSlot
    if (dataType == "By Timeslot"):
        dayS = startTimeSlotDate[:2] #dayS is start day chosen, dayE is end day chosen
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
        else: # if incident reports
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

    runAlready = False #checker for if the query has been run at least once, needed as page tries to run once without input everytime navigated to page

    start = request.POST.get('datetimepicker1', 'nothing')  # startDate

    end = request.POST.get('datetimepicker2', 'nothing')  # endDate

    if start != 'nothing': #nothing is returned if input is left blank
        runAlready = True #change checker to true

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
            #filter reports by daterange

            title = 'Displaying Incident Reports from ' + dayS + "-" + monthS + "-" + yearS+ ' to ' + dayE + "-" + monthE + "-" + yearE

            for eachReport in wantedReports[0]: #get all fields initially input by the caregiver, return to table
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
    title = [allList[2]]

    fileName = (datetime.now()).strftime('%d-%b-%Y %I-%M%p')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="' + fileName + '.csv"'

    writerForTitle = csv.writer(response,dialect='excel')
    writerForTitle.writerow(title)
    #cos title has no need to be delimited, use a diff writer
    writer = csv.writer(response,delimiter=',',quoting=csv.QUOTE_NONE)
    writer.writerow(labels)
    writer.writerow(dataList)

    return response

# DUMMY EXPORT METHOD

@login_required(login_url='')
def export(request):
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

        return render(request, 'export.html',{'dataList': dataList, 'labels': labelList, 'dataTitle': dataTitle + ',', 'dataType': dataType,'start': ' From: ' + startWeek, 'end': ' To: '+ endWeek})

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

        return render(request, 'export.html',{'dataList': dataList, 'labels': labelList, 'dataTitle': dataTitle + ',', 'dataType': dataType,'start': ' From: ' + startDay, 'end': ' To: ' + endDay})

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


        return render(request, 'export.html',{'dataList': dataList, 'labels': labelList, 'dataTitle': dataTitle + ',', 'dataType': dataType,'start': ' From: ' + startMonth, 'end': ' To: ' + endMonth})

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

        return render(request, 'export.html',{'dataList': dataList, 'labels': labelList, 'dataTitle': dataTitle + ',', 'dataType': dataType,'start':start,'end':end})

    else:
        return render (request,'export.html')