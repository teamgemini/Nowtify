from django.shortcuts import render
from django.shortcuts import HttpResponseRedirect
from django.core.context_processors import csrf
from django.contrib.auth import authenticate, login

# Create your views here.
def login(request):
    c = {}
    c.update(csrf(request))
    return render(request, "web/login.html", {})

def authentication(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)

    if user is not None:
        return HttpResponseRedirect('web/index.html')
    else:
        return HttpResponseRedirect('web/login.html')

    # if username is "josie" and password is "123":
    #      return HttpResponseRedirect('web/index.html')
    # else:
    #      return HttpResponseRedirect('web/login.html')

def index(request):
    return render(request,"web/index.html")

def overview(request):
    return render(request, "web/overview.html")

def sensor(request):
    return render(request, "web/sensor.html")

def wearable(request):
    return render(request, "web/wearable.html")

def dashboard(request):
    return render(request, "web/dashboard.html")

def settings(request):
    return render(request, "web/settings.html")

def alert(request):
    return render(request, "web/alert.html")