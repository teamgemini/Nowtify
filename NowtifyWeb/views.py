from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect

# Create your views here.
def login(request):
    #return HttpResponse('Hello World!')
    return render(request, "web/login.html", {})

def index(request):
    return render_to_response('web/index.html', {})

def overview(request):
    return render_to_response('web/overview.html', {})