import time
from PCA9685 import PCA9685
from pymaybe import maybe


class Motor:

    def __init__(self, tail=None):
        self.pwm = PCA9685(0x40, debug=True)
        self.pwm.setPWMFreq(50)
        self.taillight = tail
        self.moving = False
        
    def duty_range(self, duty1, duty2, duty3, duty4):
        if duty1 > 4095:
            duty1 = 4095
        elif duty1 < -4095:
            duty1 = -4095        
        
        if duty2 > 4095:
            duty2 = 4095
        elif duty2 < -4095:
            duty2 = -4095
            
        if duty3 > 4095:
            duty3 = 4095
        elif duty3 < -4095:
            duty3 = -4095
            
        if duty4 > 4095:
            duty4 = 4095
        elif duty4 < -4095:
            duty4 = -4095
        return duty1, duty2, duty3, duty4
        
    def left_Upper_Wheel(self, duty):
        if duty > 0:
            self.pwm.setMotorPwm(0, 0)
            self.pwm.setMotorPwm(1, duty)
        elif duty < 0:
            self.pwm.setMotorPwm(1, 0)
            self.pwm.setMotorPwm(0, abs(duty))
        else:
            self.pwm.setMotorPwm(0, 4095)
            self.pwm.setMotorPwm(1, 4095)

    def left_Lower_Wheel(self, duty):
        if duty > 0:
            self.pwm.setMotorPwm(3, 0)
            self.pwm.setMotorPwm(2, duty)
        elif duty < 0:
            self.pwm.setMotorPwm(2, 0)
            self.pwm.setMotorPwm(3, abs(duty))
        else:
            self.pwm.setMotorPwm(2, 4095)
            self.pwm.setMotorPwm(3, 4095)

    def right_Upper_Wheel(self, duty):
        if duty > 0:
            self.pwm.setMotorPwm(6, 0)
            self.pwm.setMotorPwm(7, duty)
        elif duty < 0:
            self.pwm.setMotorPwm(7, 0)
            self.pwm.setMotorPwm(6, abs(duty))
        else:
            self.pwm.setMotorPwm(6, 4095)
            self.pwm.setMotorPwm(7, 4095)

    def right_Lower_Wheel(self, duty):
        if duty > 0:
            self.pwm.setMotorPwm(4, 0)
            self.pwm.setMotorPwm(5, duty)
        elif duty < 0:
            self.pwm.setMotorPwm(5, 0)
            self.pwm.setMotorPwm(4, abs(duty))
        else:
            self.pwm.setMotorPwm(4, 4095)
            self.pwm.setMotorPwm(5, 4095)
            
    def stopMotor(self):
        self.setMotorModel(0, 0, 0, 0)
        self.moving = False
        
    def fastForward(self):
        self.setMotorModel(1500, 1500, 1500, 1500)
        self.moving = True
    
    def slowforward(self):
        self.setMotorModel(750, 750, 750, 750)
        self.moving = True
    
    def forward(self):
        self.setMotorModel(1000, 1000, 1000, 1000)
        self.moving = True
    
    def turnLeft(self):
        self.setMotorModel(-2400, -2400, 2400, 2400)
        self.moving = True
    
    def turnRight(self):
        self.setMotorModel(2400, 2400, -2400, -2400)
        self.moving = True
        
    def spin(self):
        self.setMotorModel(-1200, -1200, 3000, 3000)
        self.moving = True        
    
    def backup(self):
        self.setMotorModel(-1000, -1000, -1000, -1000)
        self.moving = True
 
    def slowBackup(self):
        self.setMotorModel(-750, -750, -750, -750)
    	self.moving = True

    def setMotorModel(self, duty1, duty2, duty3, duty4):
        duty1, duty2, duty3, duty4 = self.duty_range(duty1, duty2, duty3, duty4)
        self.left_Upper_Wheel(-duty1)
        self.left_Lower_Wheel(-duty2)
        self.right_Upper_Wheel(-duty3)
        self.right_Lower_Wheel(-duty4)
        
        if duty1 > 0 and duty2 > 0 and duty3 < 0 and duty4 < 0:
            (maybe(self.taillight)).leftblink()
        elif duty1 < 0 and duty2 < 0 and duty3 > 0 and duty4 > 0:
            (maybe(self.taillight)).rightblink()
        elif duty1 < 0 and duty2 < 0 and duty3 < 0 and duty4 < 0:
            (maybe(self.taillight)).flash()
        else:
            (maybe(self.taillight)).bothred()

	if duty1 != 0 and duty2 != 0 and duty3 != 0 and duty4 != 0:
	    self.moving = True
	else:
	    self.moving = False
            
            
PWM = Motor()          


def loop(): 
    PWM.setMotorModel(2000, 2000, 2000, 2000)  # Forward
    time.sleep(3)
    PWM.setMotorModel(-2000, -2000, -2000, -2000)  # Back
    time.sleep(3)
    PWM.setMotorModel(-500, -500, 2000, 2000)  # Left 
    time.sleep(3)
    PWM.setMotorModel(2000, 2000, -500, -500)  # Right    
    time.sleep(3)
    PWM.setMotorModel(0, 0, 0, 0)  # Stop

    
def destroy():
    PWM.setMotorModel(0, 0, 0, 0)                   


if __name__ == '__main__':
    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()
