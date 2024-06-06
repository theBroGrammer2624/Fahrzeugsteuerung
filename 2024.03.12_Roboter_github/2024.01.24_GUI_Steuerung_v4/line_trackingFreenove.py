import RPi.GPIO as GPIO
import time
from Motor import *
PWM=Motor()
from servo import *



class Line_Tracking:
    def __init__(self):
        self.IR01 = 16
        self.IR02 = 20
        self.IR03 = 21
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.IR01,GPIO.IN)
        GPIO.setup(self.IR02,GPIO.IN)
        GPIO.setup(self.IR03,GPIO.IN)
        
        #"""
    def doing(self):
        self.LMR=0x00
        sensor_values = [False, False, False]  # Liste zur Speicherung der Sensorzustände
        
        if GPIO.input(self.IR01) == True:
            sensor_values[0] = True
            self.LMR = (self.LMR | 4)
        if GPIO.input(self.IR02) == True:
            sensor_values[1] = True
            self.LMR = (self.LMR | 2)
        if GPIO.input(self.IR03) == True:
            sensor_values[2] = True
            self.LMR = (self.LMR | 1)
        
        if self.LMR == 2:
            PWM.setMotorModel(1200, 1200)
        elif self.LMR == 4:
            PWM.setMotorModel(-1500, 2500)
        elif self.LMR == 6:
            PWM.setMotorModel(-2000, 4000)
        elif self.LMR == 1:
            PWM.setMotorModel(2500, -1500)
        elif self.LMR == 3:
            PWM.setMotorModel(4000, -2000)
        elif self.LMR == 7:
            return sensor_values  # Rückgabe der Sensorwerte als Liste
            pass
        
        return sensor_values  # Rückgabe der Sensorwerte als Liste

#"""

        """
    def doing(self):
        self.LMR=0x00
        if GPIO.input(self.IR01)==True:
            self.LMR=(self.LMR | 4)
        if GPIO.input(self.IR02)==True:
            self.LMR=(self.LMR | 2)
        if GPIO.input(self.IR03)==True:
            self.LMR=(self.LMR | 1)
        if self.LMR==2:
            PWM.setMotorModel(1200,1200)
        elif self.LMR==4:
            PWM.setMotorModel(-1500,2500)
        elif self.LMR==6:
            PWM.setMotorModel(-2000,4000)
        elif self.LMR==1:
            PWM.setMotorModel(2500,-1500)
        elif self.LMR==3:
            PWM.setMotorModel(4000,-2000)
        elif self.LMR==7:
            pass
        
        """
            #PWM.setMotorModel(0,0,0,0)
        #if is_running:
        #    fenster.after(100, Line_Tracking.doing)
        #else:
        #    PWM.setMotorModel(0,0)
        #    print("ENDE")
        #else:
        #    PWM.setMotorModel(0,0)
            

# Main program logic follows:
if __name__ == '__main__':
    print ('Program is starting ... ')
    servo=Servo()
    servo.setServoPwm('0',250)
    servo.setServoPwm('1',140)    
    try:
        infrared.doing()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program  will be  executed.
        PWM.setMotorModel(0,0)
        servo.setServoPwm('0',250)
        servo.setServoPwm('1',140)
        print ("\nEnd of program")