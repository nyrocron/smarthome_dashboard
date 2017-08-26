import pytz
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from bokeh.plotting import figure, curdoc
from bokeh.client import push_session
from bokeh.embed import autoload_server, file_html
from bokeh.resources import INLINE

from sensors.models import Sensor, Measurement


def index(request):
    sensor_list = '; '.join(str((s.pk, str(s)))for s in Sensor.objects.select_subclasses())
    return HttpResponse("Sensors: " + sensor_list)


def sensor(request, sensor_id):
    sensor = get_object_or_404(Sensor, pk=sensor_id)

    measurements = sensor.measurement_set

    # create bokeh plot
    data = [(m.time.astimezone(pytz.UTC).replace(tzinfo=None), m.value) for m in measurements.filter(type=Measurement.TEMPERATURE)]
    times, temps = zip(*data)
    plot = figure(title="Temperatur", x_axis_label="Zeit", x_axis_type="datetime",
                  y_axis_label="Temperatur / °C")
    plot.line(times, temps, legend=sensor.sensor_name, line_width=2, color="red")
    curdoc().add_root(plot)

    session = push_session(curdoc())
    script = autoload_server(plot, session_id=session.id)

    return HttpResponse("<html><head></head><body>" + script + "</body></html>")

    #html = file_html(plot, INLINE, "test plot")
    #return HttpResponse(html)

    #measurement_count = sensor.measurement_set.count()
    #return HttpResponse("You requested sensor #{0}. It has {1} measurements".format(sensor_id, measurement_count))
