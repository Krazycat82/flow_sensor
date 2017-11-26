#Reads ~ 6793 times per sec
# I learned how to count potatoes and I also learned how to make the code run faster
# Printing takes time 
#
import RPi.GPIO as GPIO
import time
import math
import requests

FlowPin = 8  # flow sensor pin
LastState = 0 #last state

def setup():
    GPIO.setmode(GPIO.BOARD)  #Numbers GPIOS by Physical Location
    GPIO.setup(FlowPin, GPIO.IN) #Set FlowPin's Mode to Input
    
def read():
    LastState = GPIO.input(FlowPin)
    count = 0 #times it has read the pin
    spins = 0 #total spins
    Lastspintime = 0  #time it last spun
    ShowerTime = 0 #how long the shower is in seconds
    ShowerInactivityTime = 10 #seconds
    ShowerStartTime = 0
    ShowerOn = 0
    SpinsInShower = 0
    StartTime = time.time()
    while True:
        CurrentState = GPIO.input(FlowPin)
       
        if (CurrentState == LastState):
           pass
        else:
            if (CurrentState == 1):
                spins = spins + 1
                SpinsInShower = SpinsInShower + 1
                if(ShowerOn == 0):
                    ShowerStartTime = time.time()
                    SpinsInShower = 0
                ShowerOn = 1
                Lastspintime = time.time()
    
            LastState = CurrentState

        if(time.time()-Lastspintime >= ShowerInactivityTime and ShowerOn == 1):
            ShowerOn = 0
            ShowerTime = time.time() - ShowerInactivityTime - ShowerStartTime
            print(SpinsInShower, SpinsInShower * 2.25 * 0.000594389, time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime(ShowerStartTime)), int(math.ceil(ShowerTime)))
            post_amount(SpinsInShower * 2.25 * 0.000594389, time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime(ShowerStartTime)), int(math.ceil(ShowerTime)))

        count = count + 1   
        if(time.time() >= StartTime + 10):
            print(count, spins)
            StartTime = time.time()
            count = 0

def post_amount(amt, timestamp, duration_in_seconds):
    amount = {"amount":amt,"timestamp":timestamp, "duration_in_seconds":duration_in_seconds}
    resp = requests.post("http://localhost:5000/flow_sensor/api/v1.0/amounts", json=amount)
    if resp.status_code != 201:
        raise ApiError('POST /amounts/ {}'.format(resp.status_code))
    print('Created amounts. ID: {}'.format(resp.json())) 
        
def destroy():
    # GPIO.output(LedPin, GPIO.LOW)
    GPIO.cleanup()   # release resources



if __name__ == '__main__':  # Main Program Starts Here
    setup()
    try:
        read()
    except KeyboardInterrupt:   # When 'Ctrl + C is pressed, the function destroy will be called
        destroy()
    
