import sys,os
sys.path.append(os.path.join(sys.path[0],'Server'))
from Robotarm import Robotarm
import Servo

class Robot:
	def __init__(self):
		self.servo = Servo()
		self.robotarm = Robotarm(servo)
		
	def go(self, turn=0, arm=0, reach=0, claw=0, tail=0, tailclaw=0):
		self.robotarm.go(turn, arm, reach, claw, tail, tailclaw)
		
