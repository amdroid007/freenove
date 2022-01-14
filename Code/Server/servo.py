import time
from PCA9685 import PCA9685
class Servo:
    def __init__(self):
        self.PwmServo = PCA9685(0x40, debug=True)
        self.PwmServo.setPWMFreq(50)
        self.PwmServo.setServoPulse(8,1500)
        # self.PwmServo.setServoPulse(9,1500)
        # self.PwmServo.setServoPulse(10,1500)
        # self.PwmServo.setServoPulse(11,1500)
        # self.PwmServo.setServoPulse(12,1500)
        # self.PwmServo.setServoPulse(13,1500)
        # self.PwmServo.setServoPulse(14,1500)
        # self.PwmServo.setServoPulse(15,1500)
    def setServoPwm(self,channel,angle,error=0):
        angle=int(angle)
        if channel=='0':
            self.PwmServo.setServoPulse(8,2500-int((angle+error+20)/0.09))
        elif channel=='1':
            self.PwmServo.setServoPulse(9,500+int((angle+error)/0.09))
        elif channel=='2':
            self.PwmServo.setServoPulse(10,500+int((angle+error)/0.09))
        elif channel=='3':
            self.PwmServo.setServoPulse(11,500+int((angle+error)/0.09))
        elif channel=='4':
            self.PwmServo.setServoPulse(12,500+int((angle+error)/0.09))
        elif channel=='5':
            self.PwmServo.setServoPulse(13,500+int((angle+error)/0.09))
        elif channel=='6':
            self.PwmServo.setServoPulse(14,500+int((angle+error)/0.09))
        elif channel=='7':
            self.PwmServo.setServoPulse(15,500+int((angle+error)/0.09))

# Main program logic follows:
if __name__ == '__main__':
    pwm = Servo()
    for times in range(1,5):
        for a in range(45,90,2):
            pwm.setServoPwm('7',a)
            time.sleep(0.05)
        for b in range(90,45,-2):
            pwm.setServoPwm('7',b)
            time.sleep(0.05)
	time.sleep(1)
    pwm.setServoPwm('7',60) 
