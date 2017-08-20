from django.db import models
from sensors.utils import pressure_at_sealevel


class Sensor(models.Model):
    sensor_name = models.CharField(max_length=200)
    sensor_address = models.CharField(max_length=100, unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.sensor_name

    def parse_and_save(self, message, set_timestamp=None):
        for measurement in self.parse_measurements(message):
            # TODO: find more elegant solution for handling timestamps
            if set_timestamp is not None:
                measurement.time = set_timestamp
            measurement.save()

    def parse_measurements(self, message):
        raise NotImplementedError()


class BMP180(Sensor):
    altitude = models.FloatField()

    def parse_measurements(self, message_bytes):
        message = message_bytes.decode('ascii')
        data_dict = dict(part.strip().split('=')
                         for part in message.split(','))

        temperature = float(data_dict['T']) * 0.1
        pressure = pressure_at_sealevel(float(data_dict['P']) * 0.01, self.altitude)

        return [
            Measurement(sensor=self, type=Measurement.TEMPERATURE, value=temperature),
            Measurement(sensor=self, type=Measurement.PRESSURE, value=pressure),
        ]


class Measurement(models.Model):
    TEMPERATURE = 'T'
    PRESSURE = 'P'

    MEASUREMENT_TYPES = (
        (TEMPERATURE, 'Temperature'),
        (PRESSURE, 'Pressure'),
    )

    sensor = models.ForeignKey(Sensor)
    type = models.CharField(max_length=10, choices=MEASUREMENT_TYPES)
    value = models.FloatField()
    time = models.DateTimeField(auto_now=True)
