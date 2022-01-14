import sys,os
sys.path.append(os.path.join(sys.path[0],'Server'))
import RPi.GPIO as GPIO
from Robotarm import Robotarm
from servo import Servo
from threading import Thread
from Thread import *
from Motor import *
from Buzzer import *
from ADC import *
from gpiozero import LED
from TailLight import TailLight
from SevenSegDisplay import SevenSegDisplay

class Robot:
	def __init__(self):
		self.servo = Servo()
		self.backlight = TailLight()
		self.robotarm = Robotarm(servo)
		self.buzzer = Buzzer()
		self.frontlight = LED(HEADLIGHTPIN)		
		self.backlight = TailLight()
		self.backlight.bothred()
		self.motor = Motor()
		self.dp = SevenSegDisplay()
		
	def moveArm(self, turn=0, arm=0, reach=0, claw=0, tail=0, tailclaw=0):
		self.robotarm.go(turn, arm, reach, claw, tail, tailclaw)
	
	def horn(self, duration=0.5):
		self.buzzer.run('1')
		time.sleep(duration)
		self.buzzer.run('0')
	
	def headLight(self, state=True):
		if state:
			self.frontlight.on()
		else:
			self.frontlight.off()
	
	def moveForward(self, speed=1500, duration=1.0):
		self.motor.setMotorModel(speed, speed, speed, speed)
		if duration > 0:
			time.sleep(duration)
			self.stop()
			
	
	def moveBackward(self, speed=1500, duration=1.0):
		self.motor.setMotorModel(-speed, -speed, -speed, -speed)
		if duration > 0:
			time.sleep(duration)
			self.stop()
	
	def turnLeft(self, speed=1500):
		self.motor.setMotorModel(-speed, -speed, speed, speed)
		if duration > 0:
			time.sleep(duration)
			self.stop()
	
	def turnRight(self, speed=1500):
		self.motor.setMotorModel(speed, speed, -speed, -speed)
		if duration > 0:
			time.sleep(duration)
			self.stop()
	
	def stop(self):
		self.motor.setMotorModel(0,0,0,0)
	
	def taillight(self, state=True):
		if state:
			self.taillight.bothred()
		else:
			self.taillight.off()
	
	def display(self, text):
		self.dp.show(1, text)
