import time
from threading import Thread
from Thread import *
from servo import Servo

TAILARMMIN = 35
TAILARMMAX = 150
TAILCLAWMIN = 25
TAILCLAWMAX = 120
CLAWMIN = 55
CLAWMAX = 90
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
        self.start_servo_thread(REACHSERVO, to=0, by, delay)
    
    def back(self, to=0, by=2, delay=0.05):
        self.start_servo_thread(REACHSERVO, to, by * -1, delay)
    
    def open(self, to=0, by=5, delay=0.05):
        self.start_servo_thread(CLAWSERVO, to, by, delay)        
    
    def close(self, to=0, by=5, delay=0.05):
        self.start_servo_thread(CLAWSERVO, to=0, by * -1, delay)
        
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
        
    def run_servo_thread(self, channel, to, inc, delay):
        curpos = currentangles.get(channel)
        if to == 0:
            minpos = minangles.get(channel)
            maxpos = maxangles.get(channel) 
        else:
            minpos = to if inc < 0 else minangles.get(channel)
            maxpos = to if inc > 0 else maxangles.get(channel)
            
        while(self.moving and curpos >= minpos and curpos <= maxpos):

		print("Channel:" + channel + " curpos " + str(curpos)) 
                curpos = curpos + inc
                curpos = curpos if curpos <= maxpos else maxpos
                curpos = curpos if curpos >= minpos else minpos
                
                self.servo.setServoPwm(channel, curpos)
                currentangles[channel] = curpos               
                time.sleep(delay)
	self.servo_thread = None
	self.moving = False
                
        
# Main program logic follows:
# For full robot this will open and close the claw 4 times
# Main program logic follows:
# For full robot this will open and close the claw 4 times
if __name__ == '__main__':
    servo = Servo()
    myarm=Robotarm(servo)
    
    myarm.tailup()
    time.sleep(2)
    myarm.stop()
    myarm.tailup()
    time.sleep(2)
    myarm.stop()
    
    myarm.tailopen()
    time.sleep(1)
    myarm.tailclose()
