from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from bokeh.embed import autoload_server

from sensors.models import Sensor, Measurement


def index(request):
    sensor_list = '; '.join(str((s.pk, str(s)))for s in Sensor.objects.select_subclasses())
    return HttpResponse("Sensors: " + sensor_list)


def sensor(request, sensor_id):
    sensor = get_object_or_404(Sensor, pk=sensor_id)
    measurement_count = sensor.measurement_set.count()
    return HttpResponse("You requested sensor #{0}. It has {1} measurements".format(sensor_id, measurement_count))
