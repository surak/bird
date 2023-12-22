from ServoKit import *


class Servo:
    # def __init__(self, servoKit):
    def __init__(self):
        # self.servoKit = servoKit
        self.servoKit = ServoKit(4)
        self.motor_step = 2

    def up(self):
        self.servoKit.setAngle(0, self.servoKit.getAngle(0) + self.motor_step)

    def down(self):
        self.servoKit.setAngle(0, self.servoKit.getAngle(0) - self.motor_step)

    def left(self):
        self.servoKit.setAngle(1, self.servoKit.getAngle(1) - self.motor_step)

    def right(self):
        self.servoKit.setAngle(1, self.servoKit.getAngle(1) + self.motor_step)

    def reset(self):
        self.servoKit.resetAll()
