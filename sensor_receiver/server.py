# Set up django
import sys, os, django

sys.path.append(os.path.abspath('..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smarthome_dashboard.settings')
django.setup()

# Regular imports
from socketserver import UDPServer, BaseRequestHandler
from queue import Queue
from datetime import datetime
from functools import partial
from threading import Thread

from sensors.models import Sensor


class MessageProcessor:
    def __init__(self):
        self.message_queue = Queue()
        self.shutdown_requested = False
        self.processing_thread = None

    def process_messages(self):
        while True:
            queue_item = self.message_queue.get()
            if queue_item is None:
                break

            timestamp, address, data = queue_item
            ip_addr, port = address

            # save to django
            sensor = Sensor.objects.get(sensor_address=ip_addr)
            sensor.parse_and_save(data, set_timestamp=timestamp)

            self.message_queue.task_done()

    def start_thread(self):
        self.processing_thread = Thread(target=self.process_messages)
        self.processing_thread.start()

    def join(self):
        self.message_queue.join()
        self.message_queue.put(None)
        self.processing_thread.join()


class SensorRequestHandler(BaseRequestHandler):
    def handle(self):
        data, _ = self.request
        self.server.sensor_message_queue.put((datetime.utcnow(), self.client_address, data))


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('--port', type=int, default=1785)
    args = parser.parse_args()

    message_processor = MessageProcessor()
    message_processor.start_thread()

    server = UDPServer(('0.0.0.0', args.port), SensorRequestHandler)
    server.sensor_message_queue = message_processor.message_queue
    server_thread = Thread(target=server.serve_forever)

    for command in iter(partial(input, '> '), 'stop'):
        pass

    server.shutdown()
    server_thread.join()
    message_processor.join()

if __name__ == '__main__':
    main()
