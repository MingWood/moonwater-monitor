import RPi.GPIO as GPIO
import time, sys
from collections import deque
import threading
import logging

class FlowMeter(object):
    MAX_BUFFER_LENGTH = 2
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, gpio=26):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.counter_started = False
            self.FLOW_SENSOR_GPIO = gpio
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(gpio, GPIO.IN, pull_up_down = GPIO.PUD_UP)
            self.pulse_counter = 0
            self.flow = 0
            self.buffered_flow_values = deque([0])
            self.start_monitor()
            
    def _count_pulse(self, channel):
        self.pulse_counter += 1
    
    def start_monitor(self):
        if self.counter_started:
            return
        self.counter_started = True
        thread = threading.Thread(target=self._start_counter, daemon=True)
        thread.start()

    def _start_counter(self):
        GPIO.add_event_detect(self.FLOW_SENSOR_GPIO, GPIO.FALLING, callback=self._count_pulse)
        time_bucket = 5
        try:
            while True:
                time.sleep(time_bucket)
                self.flow = (self.pulse_counter * 60) / (38 * time_bucket) #GR-301 meter spec 38 * Q (L / Min)
                logging.info('Flow rate: {} L/min'.format(self.flow))

                self.buffered_flow_values.append(self.flow)
                if len(self.buffered_flow_values) > FlowMeter.MAX_BUFFER_LENGTH:
                    self.buffered_flow_values.popleft()
                self.pulse_counter = 0

        except Exception as emsg:
            logging.warning(emsg)
            GPIO.cleanup()
            sys.exit()
    
    def get_last_flow_rate(self):
        return self.flow

    def get_buffered_flow_rates(self):
        return self.buffered_flow_values


if __name__=='__main__':
    meter = FlowMeter()
    try:
        meter._start_counter()
    except:
        GPIO.cleanup()
        sys.exit()
        print("Exiting program.")        
