import time
import sys
import random
from threading import Thread
from Thread import *
from servo import Servo

TAILARMMIN = 35
TAILARMMAX = 150
TAILCLAWMIN = 45
TAILCLAWMAX = 140
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

DEFTAILARMPOS = (TAILARMMAX+TAILARMMIN)/2
DEFTAILCLAWPOS = TAILCLAWMIN
DEFCLAWPOS = 55 
DEFREACHPOS = 30
DEFARMPOS = 96
DEFTURNPOS = 100

defaultangles = {TAILARMSERVO:DEFTAILARMPOS, TAILCLAWSERVO:DEFTAILCLAWPOS, TURNSERVO:DEFTURNPOS, ARMSERVO:DEFARMPOS, REACHSERVO:DEFREACHPOS, CLAWSERVO:DEFCLAWPOS}
currentangles = {TAILARMSERVO:DEFTAILARMPOS, TAILCLAWSERVO:DEFTAILCLAWPOS, TURNSERVO:DEFTURNPOS, ARMSERVO:DEFARMPOS, REACHSERVO:DEFREACHPOS, CLAWSERVO:DEFCLAWPOS}
minangles = {TAILARMSERVO:TAILARMMIN, TAILCLAWSERVO:TAILCLAWMIN, TURNSERVO:TURNMIN, ARMSERVO:ARMMIN, REACHSERVO:REACHMIN, CLAWSERVO:CLAWMIN}
maxangles = {TAILARMSERVO:TAILARMMAX, TAILCLAWSERVO:TAILCLAWMAX, TURNSERVO:TURNMAX, ARMSERVO:ARMMAX, REACHSERVO:REACHMAX, CLAWSERVO:CLAWMAX}

# Need to debug this thing
moving = False
runchannel = ''
rundest = -1
runinc = -1
rundelay = -1.0

class Job(threading.Thread):

    def __init__(self, servo):
        # super(Job, self).__init__(*args, **kwargs)
	threading.Thread.__init__(self)
	self.servo = servo
        self.__flag = threading.Event() # The flag used to pause the thread
        self.__flag.set() # Set to True
        self.__running = threading.Event() # Used to stop the thread identification
        self.__running.set() # Set running to True

    def run(self):
        # Do I need this? 
        global moving, runchannel, rundest, runinc, rundelay
        while self.__running.isSet():
            self.__flag.wait() # return immediately when it is True, block until the internal flag is True when it is False
            print("In thread - moving is: " + str(moving))
            if (moving):
                curpos = currentangles.get(runchannel)
                runinc = runinc * -1 if rundest > 0 and (rundest - curpos) * runinc < 0 else runinc
                minpos = minangles.get(runchannel)
                maxpos = maxangles.get(runchannel) 
                if rundest > 0:
                    rundest = rundest if rundest > minpos else minpos
                    rundest = rundest if rundest < maxpos else maxpos
                    minpos = rundest if runinc < 0 else minpos
                    maxpos = rundest if runinc > 0 else maxpos
        
                print("Start point Channel:" + runchannel + ", curpos: " + str(curpos) + ", target:" + str(rundest) + ", min: " + str(minpos) + ", max: " + str(maxpos))
            
                while(moving and curpos >= minpos and curpos <= maxpos):
        
                    curpos = curpos + runinc
                    curpos = curpos if curpos <= maxpos else maxpos
                    curpos = curpos if curpos >= minpos else minpos
                        
                    print("Channel:" + runchannel + " curpos " + str(curpos)) 
        
                    self.servo.setServoPwm(runchannel, curpos)
                    currentangles[runchannel] = curpos               
                    time.sleep(rundelay)
                    if curpos == minpos or curpos == maxpos:
                        break
                moving = False
                self.pause()
                

    def pause(self):
        self.__flag.clear() # Set to False to block the thread

    def resume(self):
        self.__flag.set() # Set to True, let the thread stop blocking

    def stop(self):
        self.__flag.set() # Resume the thread from the suspended state, if it is already suspended
        self.__running.clear() # Set to False

class Robotarm:
    def __init__(self, servo):
        self.servo = servo
        self.runner = Job(self.servo)
        self.runner.setDaemon(True)
        self.runner.start()
        self.runner.pause()
        for x in currentangles.keys():
            self.servo.setServoPwm(x, currentangles.get(x))
            pass
        
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
        self.start_servo_thread(TAILCLAWSERVO, to, -by, delay)        
    
    def tailclose(self, to=0, by=5, delay=0.05):
        self.start_servo_thread(TAILCLAWSERVO, to, by, delay)
        
    def stop(self):
        self.stop_servo_thread()
        
    def start_servo_thread(self, channel, to, inc, delay):
        # Do I need this? 
        global moving, runchannel, rundest, runinc, rundelay
        if moving:
            moving = False
            self.runner.pause()
            time.sleep(0.2) # Pause a bit if we were already running to let things sync?

        moving = True    
        runchannel = channel
        rundest = to
        runinc = inc
        rundelay = delay
        self.runner.resume()

    def stop_servo_thread(self):
	global moving
        moving = False
        self.runner.pause()

    def go(self, turn=0, arm=0, reach=0, claw=0, tail=0, tailclaw=0):
        global moving
        if turn > 0:
            moving = True
            self.start_servo_thread(TURNSERVO, turn, 2, .05)
        if arm > 0:
            while moving:
                time.pause(0.25)
            self.moving = True
            self.start_servo_thread(ARMSERVO, arm, 2, .05)
        if reach > 0:
            while moving:
                time.pause(0.25)
            moving = True
            self.start_servo_thread(REACHSERVO, reach, 2, .05)
        if claw > 0:
            while moving:
                time.pause(0.25)
            moving = True
            self.start_servo_thread(CLAWSERVO, claw, 5, .05)
        if tail > 0:
            while moving:
                time.pause(0.25)
            moving = True
            self.start_servo_thread(TAILARMSERVO, tail, 2, .05)
        if tailclaw > 0:
            while moving:
                time.pause(0.25)
            moving = True
            self.start_servo_thread(TAILCLAWSERVO, tailclaw, 5, .05)
                        
    def run_tests(self, num_tests=1000, stop_probability = 0.8):
        """A test method to figure out what is happening
        
        System getting stuck after a number of operations - unfortunately
        not quite predictably - so lets try to get some kind of test that
        may be we can run without powering on the servos to see if I can
        reproduce the issue. Likely too many threads, but thread counting
        did not seem to help.
        
        There are 12 operations, and the stop. Technically we call stop only
        for the hand ops - claw ops do not call stop.
        
        So maybe we randomly find an op to run, a time period (0-2 sec) to run
        and then call stop (or not) randomly. 
        """
        curtest = 0
        random.seed(1111) # lets use a fixed seed so we can repeat this
        
        while curtest < num_tests:
            curtest = curtest + 1
            op = random.randint(1,12) # decide which op to run
            duration = 0.25 + random.random()*1.75 # Generate a float between 0 and 2
            stop = random.random() # Generate another float - use to decide if stop is called

            print("*** Test # " + str(curtest) + ": Op: " + str(op) + ", Duration: " + str(duration) + ", Stop prob: " + str(stop))
            
            if op == 1:
                self.up()
            elif op == 2:
                self.down()
            elif op == 3:
                self.left()
            elif op == 4:
                self.right()
            elif op == 5:
                self.front()
            elif op == 6:
                self.back()
            elif op == 7:
                self.open()
            elif op == 8:
                self.close()
            elif op == 9:
                self.tailup()
            elif op == 10:
                self.taildown()
            elif op == 11:
                self.tailopen()
            else:
                self.tailclose()
            
            time.sleep(duration)
            
            if (stop <= stop_probability):
                self.stop()
                
        
# Main program logic follows:
# For full robot this will open and close the claw 4 times
if __name__ == '__main__':
    servo = Servo()
    myarm=Robotarm(servo)
    
    myarm.run_tests()
    
   
    print("Done!")
    sys.exit(0)
