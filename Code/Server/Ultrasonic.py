import time
from Motor import *
import RPi.GPIO as GPIO
from servo import *
from PCA9685 import PCA9685
GPIO.setwarnings(False)
trigger_pin = 27
echo_pin = 22
GPIO.setmode(GPIO.BCM)
GPIO.setup(trigger_pin,GPIO.OUT)
GPIO.setup(echo_pin,GPIO.IN)

LEFT_ANGLE = 130
FWD_ANGLE = 80
RIGHT_ANGLE = 30
SPEED = 0.05

class Ultrasonic:
    
    def __init__(self):
        self.PWM=Motor()
        self.pwm_S=Servo()

    def send_trigger_pulse(self):
        GPIO.output(trigger_pin,True)
        time.sleep(0.00015)
        GPIO.output(trigger_pin,False)

    def wait_for_echo(self,value,timeout):
        count = timeout
        while GPIO.input(echo_pin) != value and count>0:
            count = count-1
    
    def look_right(self):
        for a in range(FWD_ANGLE,LEFT_ANGLE,5):
            self.pwm_S.setServoPwm('0',a)
            time.sleep(SPEED)

    def look_left(self):
        for a in range(FWD_ANGLE,RIGHT_ANGLE,-5):
            self.pwm_S.setServoPwm('0',a)
            time.sleep(SPEED)
    
    def look_forward(self):
        self.pwm_S.setServoPwm('0',FWD_ANGLE)
                 
    def get_distance(self):
        distance_cm=[0,0,0,0,0]
        for i in range(3):
            self.send_trigger_pulse()
            self.wait_for_echo(True,10000)
            start = time.time()
            self.wait_for_echo(False,10000)
            finish = time.time()
            pulse_len = finish-start
            distance_cm[i] = pulse_len/0.000058
        distance_cm=sorted(distance_cm)
        return int(distance_cm[2])
    
    def run_motor(self,L,M,R):
        if (L < 30 and M < 30 and R <30) or M < 30 :
            self.PWM.setMotorModel(-1450,-1450,-1450,-1450) 
            time.sleep(0.1)   
            if L < R:
                self.PWM.setMotorModel(1450,1450,-1450,-1450)
            else :
                self.PWM.setMotorModel(-1450,-1450,1450,1450)
        elif L < 30 and M < 30:
            self.PWM.setMotorModel(1500,1500,-1500,-1500)
        elif R < 30 and M < 30:
            self.PWM.setMotorModel(-1500,-1500,1500,1500)
        elif L < 20 :
            self.PWM.setMotorModel(2000,2000,-500,-500)
            if L < 10 :
                self.PWM.setMotorModel(1500,1500,-1000,-1000)
        elif R < 20 :
            self.PWM.setMotorModel(-500,-500,2000,2000)
            if R < 10 :
                self.PWM.setMotorModel(-1500,-1500,1500,1500)
        else :
            self.PWM.setMotorModel(600,600,600,600)
                
    def run(self):
        for i in range(30,151,60):
                self.pwm_S.setServoPwm('0',i)
                time.sleep(0.2)
                if i==30:
                    L = self.get_distance()
                elif i==90:
                    M = self.get_distance()
                else:
                    R = self.get_distance()
        while True:
            for i in range(90,30,-60):
                self.pwm_S.setServoPwm('0',i)
                time.sleep(0.2)
                if i==30:
                    L = self.get_distance()
                elif i==90:
                    M = self.get_distance()
                else:
                    R = self.get_distance()
                self.run_motor(L,M,R)
            for i in range(30,151,60):
                self.pwm_S.setServoPwm('0',i)
                time.sleep(0.2)
                if i==30:
                    L = self.get_distance()
                elif i==90:
                    M = self.get_distance()
                else:
                    R = self.get_distance()
                self.run_motor(L,M,R)
        
            
        
ultrasonic=Ultrasonic()              
# Main program logic follows:
if __name__ == '__main__':
    print ('Program is starting ... ')
    try:
        ultrasonic.run()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        PWM.setMotorModel(0,0,0,0)
        ultrasonic.pwm_S.setServoPwm('0',90)

