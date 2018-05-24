#Reads ~ 6793 times per sec
# I learned how to count potatoes and I also learned how to make the code run faster
# Printing takes time
#
import RPi.GPIO as GPIO
import time
import math
import requests
import json

FlowPin = 8  # flow sensor pin
LastState = 0 #last state
#logf = open("/home/pi/flow_sensor/flow_sensor.log", "w+", 1)

def time2str(t):
    return time.strftime("%d %b %Y %H:%M:%S", time.localtime(t))

def log(message):
    logtime = time.strftime("%D %T", time.localtime(time.time()))
    print logtime + " " + message

def setup():
    GPIO.setmode(GPIO.BOARD)  #Numbers GPIOS by Physical Location
    GPIO.setup(FlowPin, GPIO.IN) #Set FlowPin's Mode to Input
    log("Starting....")
#    logf.write("Starting....\n")

def read():
    LastState = GPIO.input(FlowPin)
    count = 0 #times it has read the pin
    spins = 0 #total spins
    Lastspintime = 0  #time it last spun
    ShowerTime = 0 #how long the shower is in seconds
    ShowerInactivityTime = 3 #seconds
    ShowerStartTime = 0
    ShowerOn = 0
    SpinsInShower = 0
    StartTime = time.time()
    while True:
        CurrentState = GPIO.input(FlowPin)

        if (CurrentState == LastState):
            #print "CurrentState == LastState"
            pass
        else:
            if (CurrentState == 1):
                spins = spins + 1
                SpinsInShower = SpinsInShower + 1
                log("CurrentState == 1: spins=" + str(spins) + " SpinsInShower=" + str(SpinsInShower))
                if (ShowerOn == 0):
                    log("ShowerOn == 0")
                    ShowerStartTime = time.time()
                    SpinsInShower = 0
                ShowerOn = 1
                Lastspintime = time.time()
                log("ShowerStartTime=" + time2str(ShowerStartTime) + " Lastspintime=" + time2str(Lastspintime))

            LastState = CurrentState

        if(time.time()-Lastspintime >= ShowerInactivityTime and ShowerOn == 1):
            ShowerOn = 0
            ShowerTime = time.time() - ShowerInactivityTime - ShowerStartTime
            log("**** SpinsInShower=" + str(SpinsInShower) + " Amount=" + str(SpinsInShower * 2.25 * 0.000594389) + " ShowerStartTime=" + time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime(ShowerStartTime)) + " ShowerTime=" + str(int(math.ceil(ShowerTime))))
#            logf.write("{0} {1} {2} {3} {4}\n".format(SpinsInShower, SpinsInShower * 2.25 * 0.000594389, time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime(ShowerStartTime)), int(math.ceil(ShowerTime))))
            post_amount(SpinsInShower * 2.25 * 0.000594389, time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime(ShowerStartTime)), int(math.ceil(ShowerTime)))

        count = count + 1
        now = time.time()
        if(now >= StartTime + 10 and ShowerOn == 0):
            log("now=" + time2str(now) + " StartTime=" + time2str(StartTime) + " count=" + str(count) + " spins=" + str(spins))#, flush=True)
#            logf.write("{0} {1}\n".format(count, spins))
            StartTime = time.time()
            count = 0

def post_amount(amt, timestamp, duration_in_seconds):
    amount = {"amount":amt,"timestamp":timestamp, "duration_in_seconds":duration_in_seconds}
    log("**** post_amount: " + json.dumps(amount))
    resp = requests.post("https://dots-dripdrop-api.herokuapp.com/flow_sensor/api/v1.0/amounts", json=amount)
    if resp.status_code != 201:
        raise ApiError('POST /amounts/ {}'.format(resp.status_code))
#    print('Created amounts. ID: {}'.format(resp.json()))

def destroy():
    # GPIO.output(LedPin, GPIO.LOW)
    GPIO.cleanup()   # release resources



if __name__ == '__main__':  # Main Program Starts Here
    setup()
    try:
        read()
    except KeyboardInterrupt:   # When 'Ctrl + C is pressed, the function destroy will be called
        destroy()
