import time
import sys
from threading import Thread
from Thread import *
from servo import Servo

TAILARMMIN = 35
TAILARMMAX = 150
TAILCLAWMIN = 25
TAILCLAWMAX = 120
CLAWMIN = 55
CLAWMAX = 100
TURNMIN = 30
TURNMAX = 170
REACHMIN = 30
REACHMAX = 150
ARMMIN = 40
ARMMAX = 130

TAILARMSERVO = '2'
TAILCLAWSERVO = '3'
TURNSERVO = '4'
ARMSERVO = '5'
REACHSERVO = '6'
CLAWSERVO = '7'

DEFTAILARMPOS = TAILARMMAX
DEFTAILCLAWPOS = TAILCLAWMIN
DEFCLAWPOS = 90 
DEFREACHPOS = 90
DEFARMPOS = 85
DEFTURNPOS = 100

defaultangles = {TAILARMSERVO:DEFTAILARMPOS, TAILCLAWSERVO:DEFTAILCLAWPOS, TURNSERVO:DEFTURNPOS, ARMSERVO:DEFARMPOS, REACHSERVO:DEFREACHPOS, CLAWSERVO:DEFCLAWPOS}
currentangles = {TAILARMSERVO:DEFTAILARMPOS, TAILCLAWSERVO:DEFTAILCLAWPOS, TURNSERVO:DEFTURNPOS, ARMSERVO:DEFARMPOS, REACHSERVO:DEFREACHPOS, CLAWSERVO:DEFCLAWPOS}
minangles = {TAILARMSERVO:TAILARMMIN, TAILCLAWSERVO:TAILCLAWMIN, TURNSERVO:TURNMIN, ARMSERVO:ARMMIN, REACHSERVO:REACHMIN, CLAWSERVO:CLAWMIN}
maxangles = {TAILARMSERVO:TAILARMMAX, TAILCLAWSERVO:TAILCLAWMAX, TURNSERVO:TURNMAX, ARMSERVO:ARMMAX, REACHSERVO:REACHMAX, CLAWSERVO:CLAWMAX}

class Robotarm:
    def __init__(self, servo):
        self.servo = servo
        for x in currentangles.keys():
            self.servo.setServoPwm(x, currentangles.get(x))
        self.moving = False
        self.servo_thread = None
        
    def up(self, to=0, by=2, delay=0.05):
        self.start_servo_thread(ARMSERVO, to, by, delay)
    
    def down(self, to=0, by=2, delay=0.05):
        self.start_servo_thread(ARMSERVO, to, by * -1, delay)
    
    def tailup(self, to=0, by=2, delay=0.05):
        self.start_servo_thread(TAILARMSERVO, to, by, delay)
    
    def taildown(self, to=0, by=2, delay=0.05):
        self.start_servo_thread(TAILARMSERVO, to, by * -1, delay)
    
    def left(self, to=0, by=3, delay=0.05):
        self.start_servo_thread(TURNSERVO, to, by, delay)
    
    def right(self, to=0, by=3, delay=0.05):
        self.start_servo_thread(TURNSERVO, to, by * -1, delay)
    
    def front(self, to=0, by=2, delay=0.05):
        self.start_servo_thread(REACHSERVO, to, by, delay)
    
    def back(self, to=0, by=2, delay=0.05):
        self.start_servo_thread(REACHSERVO, to, by * -1, delay)
    
    def open(self, to=0, by=5, delay=0.05):
        self.start_servo_thread(CLAWSERVO, to, by, delay)        
    
    def close(self, to=0, by=5, delay=0.05):
        self.start_servo_thread(CLAWSERVO, to, by * -1, delay)
        
    def tailopen(self, to=0, by=5, delay=0.05):
        self.start_servo_thread(TAILCLAWSERVO, to, by, delay)        
    
    def tailclose(self, to=0, by=5, delay=0.05):
        self.start_servo_thread(TAILCLAWSERVO, to, by * -1, delay)
        
    def stop(self):
        self.stop_servo_thread()
        
    def start_servo_thread(self, channel, to, inc, delay):
        if self.servo_thread or self.moving:
            self.stop_servo_thread()
        self.moving = True    
        self.servo_thread = Thread(target=self.run_servo_thread, args=(channel, to, inc, delay))
        self.servo_thread.start()   

    def stop_servo_thread(self):
        self.moving = False
        if self.servo_thread:
            stop_thread(self.servo_thread)
            self.servo_thread = None

    def go(self, turn=0, arm=0, reach=0, claw=0, tail=0, tailclaw=0):
        if turn > 0:
            self.moving = True
            self.run_servo_thread(TURNSERVO, turn, 2, .05)
        if arm > 0:
            self.moving = True
            self.run_servo_thread(ARMSERVO, arm, 2, .05)
        if reach > 0:
            self.moving = True
            self.run_servo_thread(REACHSERVO, reach, 2, .05)
        if claw > 0:
            self.moving = True
            self.run_servo_thread(CLAWSERVO, claw, 5, .05)
        if tail > 0:
            self.moving = True
            self.run_servo_thread(TAILARMSERVO, tail, 2, .05)
        if tailclaw > 0:
            self.moving = True
            self.run_servo_thread(TAILCLAWSERVO, tailclaw, 5, .05)
        
    def run_servo_thread(self, channel, to, inc, delay):
        curpos = currentangles.get(channel)
        inc = inc * -1 if to > 0 and (to - curpos) * inc < 0 else inc
        minpos = minangles.get(channel)
        maxpos = maxangles.get(channel) 
        if to > 0:
            to = to if to > minpos else minpos
            to = to if to < maxpos else maxpos
            minpos = to if inc < 0 else minpos
            maxpos = to if inc > 0 else maxpos
            
        while(self.moving and curpos >= minpos and curpos <= maxpos):

            curpos = curpos + inc
            curpos = curpos if curpos <= maxpos else maxpos
            curpos = curpos if curpos >= minpos else minpos
            print("Channel:" + channel + " curpos " + str(curpos)) 
                
            self.servo.setServoPwm(channel, curpos)
            currentangles[channel] = curpos               
            time.sleep(delay)
            if curpos == minpos or curpos == maxpos:
                break
        self.servo_thread = None
        self.moving = False
                
        
# Main program logic follows:
# For full robot this will open and close the claw 4 times
if __name__ == '__main__':
    servo = Servo()
    myarm=Robotarm(servo)
    
    myarm.taildown(to=30)
    time.sleep(2)
    myarm.stop()
    myarm.tailup(to=110)
    time.sleep(2)
    myarm.stop()
    myarm.tailup(to=100)
    time.sleep(2)
    myarm.stop()
    
    myarm.tailopen()
    time.sleep(1)
    myarm.tailclose()
    time.sleep(1)
    myarm.stop()
    myarm.go(turn=70, arm=80, reach=60, claw=45, tail=100, tailclaw=30)
    print("Done!")
    sys.exit(0)
