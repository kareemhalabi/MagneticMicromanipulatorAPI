import time
import RPi.GPIO as GPIO
from getField import *
#The main functions are:
#print(getField())
#print(getFieldAvg(int))

from power_supply import *

ps = PowerSupply('/dev/ttyUSB0')




def calibrate():
    print("Calibrating no field condition...")
    return(getFieldAvg(20))
    print("Calibration complete.")

def signum(value):
    return int(value/abs(value))

def demagCurrent(noField):
    
    print('noField: %f' % noField)
    #GPIO setup
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(5, GPIO.OUT)
    GPIO.setup(6, GPIO.OUT)
    GPIO.output(6, GPIO.HIGH)
    GPIO.output(5, GPIO.LOW)
    print('Ensuring saturation please wait.')
    current = 1.5                                                  
    
    ps.set_current(current)
    ps.enable_output()
    time.sleep(10)
    ps.disable_output()
    
    
    
    current = 0.05
    GPIO.output(5, GPIO.HIGH)
    GPIO.output(6, GPIO.HIGH)
    #position sensor
    input('Position sensor and press Enter to begin demagnetization')
    presentField = getField()
    original_sign = signum(presentField - noField)
    print('presentField %f' % presentField)
    print('Original sign: %f' % original_sign)
    ps.set_current(current)
    
    
    
        
    for i in range(15):
        
        print("The 0-field value is:\n" + str(noField))
        GPIO.output(6, GPIO.LOW)
        time.sleep(0.1)
        ps.enable_output()
        time.sleep(0.03) #this allows for the delay of the ps to turn on before opening the cct
        GPIO.output(6, GPIO.HIGH)
        ps.disable_output()
        time.sleep(0.5)#delay for inductance before field reading
        presentField = getField()
            
        if (abs(presentField - noField) > 0.004*noField and signum(presentField - noField) == original_sign)== False:
            break
			  
        print("Present Field is: " + str(presentField))
    
    if (abs(presentField - noField) > 0.004*noField and signum(presentField - noField) != original_sign):
        print("Overshoot of " + str(abs(presentField-noField)))
        current = 0.05
        ps.set_current(current)
        for i in range(5):
            GPIO.output(6, GPIO.HIGH)
            GPIO.output(5, GPIO.LOW)
            ps.enable_output()
            ps.disable_output()
            #time.sleep(0.001)#current duration
            GPIO.output(5, GPIO.HIGH)
            time.sleep(0.5)
            presentField = getField()
            if  (abs(presentField - noField) > 0.004*noField and (signum(presentField - noField) != original_sign)) == False:
                break
        
    time.sleep(1)
    presentField = getField()
    print("Final Field is: " + str(presentField))
    print("Off by: " + str(presentField-noField))
    #cleanup
    GPIO.cleanup()
    ps.disable_output()
    
    
def relay_switch(n):
    #setup
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(5, GPIO.OUT)
    GPIO.setup(6, GPIO.OUT)
    GPIO.output(5, GPIO.HIGH)
    GPIO.output(6, GPIO.HIGH)
    
    current=1.1
    ps.set_current(current)
    ps.enable_output()
    
    for i in range(n):
        #Relays energized
        GPIO.output(5, GPIO.HIGH)
        GPIO.output(6, GPIO.HIGH)
        
        time.sleep(0.007)
        #Relays de-energized
        GPIO.output(5, GPIO.LOW)
        GPIO.output(6, GPIO.LOW)
        
        time.sleep(0.007)
        
        if i % 10 == 0:
            ps.set_current(current)
            current += -0.1
        
    #cleanup
    GPIO.cleanup()
    ps.disable_output()

    
