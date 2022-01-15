#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  walle.py
#  
#  Copyright 2022 Arijit Sengupta <asengupt@fiu-mac.ad.fiu.edu>
#  
#  
from robot import *

def main(args):
	myrobot = Robot()
	myrobot.display("Hello")
	myrobot.moveArm(turn=45, arm=70, reach=65)
	myrobot.moveArm(turn=90, arm=100, reach=120)
	# myrobot.moveBackward()
	myrobot.horn()
	return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
