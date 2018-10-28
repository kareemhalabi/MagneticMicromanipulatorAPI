import time
import statistics
# Import the ADS1x15 module.
import Adafruit_ADS1x15
#Ensure that the Adafruit_ADS1x15 folder is in the same directory as this file
# Create an ADS1115 ADC (16-bit) instance.
adc = Adafruit_ADS1x15.ADS1115()

# Choose a gain of 1 for reading voltages from 0 to 4.09V.
# Or pick a different gain to change the range of voltages that are read:
#  - 2/3 = +/-6.144V
#  -   1 = +/-4.096V
#  -   2 = +/-2.048V
#  -   4 = +/-1.024V
#  -   8 = +/-0.512V
#  -  16 = +/-0.256V
# See table 3 in the ADS1015/ADS1115 datasheet for more info on gain.



def getField():
    inpin = 0 #sets the input pin 0 for A0 - A1
    GAIN = 2 #this is for the 120k R1 and 36K R2 voltage divider protection


    #Debugging Lines
    
    #print("A0 is: " + str(adc.read_adc(inpin, gain=GAIN)))
    #print("A1 is: " + str(adc.read_adc(1, gain=GAIN)))
    #print("A0-A1 is: " + str(adc.read_adc_difference(inpin, gain=GAIN)))

    #End Testing Line

    
    trials = 10
    reading=[0]*trials
    avg=0
    avgcntr=0
    for i in range(trials):
        #uncomment below for pin difference reading
        #reading[i] = adc.read_adc_difference(inpin, gain=GAIN)
        #comment out below line if using difference reading
        reading[i] = adc.read_adc(1, gain=GAIN)
    deviation = statistics.stdev(reading)
    #here we want to remove outliers in the readings to account for bouncing or interference
    UB = statistics.mean(reading) + deviation
    LB = statistics.mean(reading) - deviation
    for i in range(trials):
        if (reading[i] < UB) and (reading[i]>LB):
            avg += reading[i]
            avgcntr += 1
    if avgcntr==0:
        return(-1)
    return(int(avg/avgcntr))



#take an average of the outlier-omit field readings over a specified number of trials
def getFieldAvg(trials):
    value = 0
    for i in range(trials):
        try:
            value += getField()
        except:
            return(-1)
    return(int(value/trials))
        

