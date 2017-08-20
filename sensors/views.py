from django.http import HttpResponse
from django.shortcuts import render

from bokeh.embed import autoload_server


def index(request):
    return HttpResponse("Sensor list here")


def sensor(request, sensor_id):
    return HttpResponse("You requested sensor #{0}".format(sensor_id))
