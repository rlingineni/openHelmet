import smbus
import time
import os
import math
from meter import MMA7660
import RPi.GPIO as GPIO ## Import GPIO library


GPIO.setmode(GPIO.BOARD) ## Use board pin numbering

GPIO.setup(11, GPIO.OUT) ## Setup GPIO Pin 11 to OUT
GPIO.setup(13, GPIO.OUT) ## Setup GPIO Pin 13 to OUT
GPIO.setup(15, GPIO.OUT) ## Setup GPIO Pin 15 to OUT

mma = MMA7660() # This class is derived from meter.py

def Blink(numTimes,speed,pin):
    for i in range(0,numTimes):## Run loop numTimes
        print "Iteration " + str(i+1)## Print current loop
        GPIO.output(pin,True)## Switch on pin 7
        time.sleep(speed)## Wait
        GPIO.output(pin,False)## Switch off pin 7
        time.sleep(speed)## Wait
    print "Done" ## When loop is complete, print "Done"
    


oldVals = [] # A list of of values that we will average to account for outliers

mma.init()
for a in range(1000): # repeat this for a thousand times
    y = mma.getY() # get the Y Value from our meter libary
    oldVals.append(y) #add to the list of values
    if(len(oldVals)==5): #Once the list of values has 5 items
        average = sum(oldVals) /5 #Average the values in the list, and determine light to blink
        print average #Print for debugging
        if(average > 50 and average < 60): 
           Blink(10,1,15) #Blink the Right
        elif(average > 5 and average <10):
           Blink(10,1,11) #Blink the Left
        oldVals=[]
    print y #print for debugging

