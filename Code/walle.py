#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  walle.py
#  
#  Copyright 2022 Arijit Sengupta <asengupt@fiu-mac.ad.fiu.edu>
#  
#
import time
from robot import *

def main(args):
	myrobot = Robot()
	myrobot.display("Hello")
	myrobot.turnLeft(speed=2000,duration=5)
	myrobot.moveArm(tail=50)
	# myrobot.moveArm(turn=118, arm=73, reach=142, claw=55)
	# myrobot.moveArm(turn=90, arm=100, reach=120)
	# myrobot.moveBackward()
	time.sleep(1)
	myrobot.moveArm(tail=120)
	#myrobot.moveArm(arm=140)
	#myrobot.moveArm(reach=110)
	#myrobot.moveArm(turn=135)
	#myrobot.moveArm(claw=100)
	
	
	myrobot.horn()
	return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
