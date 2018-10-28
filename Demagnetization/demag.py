import time
from getField import *
#The main functions are:
#print(getField())
#print(getFieldAvg(int))

def calibrate():
    print("Calibrating no field condition...")
    return(getFieldAvg(20))
    print("Calibration complete.")
    
def demagCurrent():
    noField = calibrate()
    while True:
        #This is for user information
        print("The 0-field value is:\n" + str(noField))
        input("Simulate the new state then: Press enter to continue...")
        #End user information
        presentField = getField()
        print("Present Field is: " + str(presentField))
        if (abs(noField - presentField)) < (0.01*noField):
            break
        
    
demagCurrent()
    
    
