import pigpio
from time import sleep


class TapMixingServo(object):
    PIN = 17
    ANGLE_RANGE = 270
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, initial_angle=0):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.current_angle_position = initial_angle
            self.servo_control = pigpio.pi()

    def move_to_angle(self, angle):
        angle = min(angle, TapMixingServo.ANGLE_RANGE)
        pulse_width = int(500 + (angle / (TapMixingServo.ANGLE_RANGE / 2000)))
        self.servo_control.set_servo_pulsewidth(TapMixingServo.PIN, pulse_width)
        self.current_angle_position = angle


if __name__=='__main__':
    serv = TapMixingServo()
    while True:
        #Ask user for angle and turn servo to it
        angle = float(input('Enter angle between 0 & 180: '))
        serv.move_to_angle(angle)
