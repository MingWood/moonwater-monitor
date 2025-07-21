from flask import Flask, request, jsonify
from prometheus_client import make_wsgi_app, Gauge
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import threading
import time
import yaml
import sys

import connectors.tds_meter as tds_meter
import connectors.tap_mixing_servo as tap_mixing_servo
import connectors.flow_meter as flow_meter
import algorithms.servo_angle_adjustments_from_tds as servo_angle_adjustments_from_tds

PORT = 5123

class WebServer(object):
    app = None

    def __init__(self, config_name):
        with open(config_name, 'r') as file:
            self.config = yaml.safe_load(file)
        self.app = Flask(__name__)
        self.app.wsgi_app = DispatcherMiddleware(self.app.wsgi_app, {
            '/metrics': make_wsgi_app()
        })  
        self.app.route('/test', methods=['GET'])(self.test_server)
        self.refresh_interval = self.config['REFRESH_INTERVAL']
        self.connectors = {}
        self.init_connectors()
        self.setup_prometheus()
        self.start_background_monitor()

    def init_connectors(self):
        self.connectors['tds_meter'] = tds_meter.TDSMeter(
                self.config['SENSORS_ATTACHED'],
                self.config['SENSOR_ID_TO_INDEX'],
                self.config['SENSOR_COMPENSATIONS']
        )

        flow_meter_details = self.config.get('FLOW_METER_ATTACHED_PIN')
        if flow_meter_details:
            meter_pin = list(flow_meter_details.values())[0]
            self.connectors['flow_meter'] = flow_meter.FlowMeter(meter_pin)

        if self.config['SERVO_ADJUSTMENTS']['USE_SERVO']:
            self.connectors['tap_mixing_servo'] = tap_mixing_servo.TapMixingServo(
                initial_angle=int(self.config['SERVO_ADJUSTMENTS']['INITIAL_ANGLE'])
            )

    def setup_prometheus(self):
        self.tds_sensor = Gauge(
            'tds_inline',
            'tds reading in ppm for inline water sensors',
            ["sensor_ID"]
        )
        self.servo_position = Gauge(
            'servo_degrees',
            'commanded set position of a servo',
            ["sensor_ID"]
        )
        self.flow_meter = Gauge(
            'flow_meter_liters_per_min',
            'recorded flow rate',
            ["sensor_ID"]
        )
    
    def test_server(self):
        return 'up'

    def start_background_monitor(self):
        thread = threading.Thread(target=self.monitor_correct_update, daemon=True)
        thread.start()

    def monitor_correct_update(self):
        while True:
            tds_values, tds_buffer = self.check_tds_levels()
            last_flow_rate, flow_buffer = self.check_flow_rates()
            new_angles = self.execute_angle_corrections(tds_buffer, flow_buffer)
            self.update_metrics(tds_values, new_angles, last_flow_rate)
            time.sleep(self.refresh_interval)

    def check_tds_levels(self):
        meter = self.connectors['tds_meter']
        current_vals = meter.read_tds_values()
        buffer = meter.get_buffered_tds_values()
        return current_vals, buffer

    def check_flow_rates(self):
        meter_details = self.config.get('FLOW_METER_ATTACHED_PIN')
        if not meter_details:
            return {}, []
        meter_name = list(meter_details.keys())[0]
        meter = self.connectors['flow_meter']
        return { meter_name: meter.get_last_flow_rate() },  meter.get_buffered_flow_rates()

    def execute_angle_corrections(self, tds_values, flow_buffer):
        if not self.config['SERVO_ADJUSTMENTS']['USE_SERVO']:
            return { self.config['SERVO_ADJUSTMENTS']['SERVO_ID_FOR_ANGLE_ADJUSTMENT']: 0 }

        tds_buffer = []
        for reading in tds_values:
            value = reading[self.config['SERVO_ADJUSTMENTS']['SENSOR_ID_FOR_ANGLE_ADJUSTMENT']]
            tds_buffer.append(value)
        serv = self.connectors['tap_mixing_servo']
        angle = servo_angle_adjustments_from_tds.proportial_only_servo_angle_from_tds(
            tds_buffer,
            flow_buffer,
            self.config['SERVO_ADJUSTMENTS']['TDS_TARGET'],
            serv.current_angle_position
        )
        serv.move_to_angle(angle)

        return {
            self.config['SERVO_ADJUSTMENTS']['SERVO_ID_FOR_ANGLE_ADJUSTMENT']: angle
        }
    
    def update_metrics(self, tds_values, new_angles, flow_values):
        for name, tds_value in tds_values.items():
            self.tds_sensor.labels(sensor_ID=name).set(tds_value)
        if new_angles:
            for name, angle in new_angles.items():
                self.servo_position.labels(sensor_ID=name).set(angle)
        if flow_values:
            for name, flow in flow_values.items():
                self.flow_meter.labels(sensor_ID=name).set(flow)

    def run(self, debug=False):
        self.app.run(host='0.0.0.0', port=PORT, debug=debug)


if __name__ == '__main__':
    config_name = sys.argv[1]
    server = WebServer(config_name)
    server.run()
