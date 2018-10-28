#Event Functions#

from pagegui1 import *

def setCurrent(amp, time):
    #Label_status_amps.set("Amperes (mA): "+amp)
    print ('Set current to ', amp, 'For time ', time)
    return amp

def initPowerSupply():  #One time set up per launch
    #Set output current/voltage range
    #Enable output
    #Set step size?
    return 1

def getSetValue():      #Return the current the Power Supply is set to (
    #IE call APPLy? or CURRent?
    return 1;
def getActualCurrent():     #Measure the current flow using on board sense resistor
    # Call MEASure: CURRent?
    return 1
def shutOff():
    print('Turning off Power Supply')
    return 1

def turnOn():
    print('Turning on Power Supply')
    return 1

