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
	myrobot.go(turn=90, arm=90, reach=90)
    # return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
