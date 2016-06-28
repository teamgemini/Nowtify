from django.shortcuts import render
from django.shortcuts import HttpResponseRedirect
from django.shortcuts import redirect
from django.core.context_processors import csrf
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout


# Create your views here.
def login(request):
    c = {}
    c.update(csrf(request))
    return render(request, "web/login.html", {})


def logout(request):
    logout(request)
    return render(request, "web/login.html")


def authentication(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)

    if user is not None:

        if user.is_active:
            auth_login(request, user)
            return redirect('index')
        else:
            return redirect('login')


@login_required(login_url='web')
def index(request):
    return render(request, "web/index.html")


def overview(request):
    return render(request, "web/overview.html")


def sensor(request):
    return render(request, "web/sensor.html")


def wearable(request):
    return render(request, "web/wearable.html")


def dashboard(request):
    return render(request, "web/dashboard.html")

