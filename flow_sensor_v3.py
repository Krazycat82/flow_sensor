#Reads ~ 6793 times per sec
# I learned how to count potatoes and I also learned how to make the code run faster
# Printing takes time 
#
import RPi.GPIO as GPIO
import time
import math

FlowPin = 8  # flow sensor pin
LastState = 0 #last state

def setup():
    GPIO.setmode(GPIO.BOARD)  #Numbers GPIOS by Physical Location
    GPIO.setup(FlowPin, GPIO.IN) #Set FlowPin's Mode to Input
    
def read():
    LastState = GPIO.input(FlowPin)
    count = 0
    spins = 0
    Lastspintime = 0
    ShowerTime = 0
    ShowerInactivityTime = 10
    ShowerStart = 0
    ShowerOn = 0
    SpinsInShower = 0
    while True:
        CurrentState = GPIO.input(FlowPin)
       
        if (CurrentState == LastState):
           # print('No Change')
           pass
        else:
            if (CurrentState == 1):
                #print('One Spin')
                spins = spins + 1
                SpinsInShower = SpinsInShower + 1
                if(ShowerOn == 0):
                    ShowerStart = time.time()
                    SpinsInShower = 0
                ShowerOn = 1
                Lastspintime = time.time()
            else:
               # print('No Spin')
               pass
            LastState = CurrentState

        if(time.time()-Lastspintime >= ShowerInactivityTime and ShowerOn == 1):
            ShowerOn = 0
            ShowerTime = time.time() - ShowerInactivityTime - ShowerStart

        count = count + 1
        if count % 10000 == 0:
            print(count // 10000, spins, ShowerOn, SpinsInShower, SpinsInShower * 2.25 * 0.000594389, time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime(ShowerStart)), int(math.ceil(ShowerTime)))
        
def destroy():
    # GPIO.output(LedPin, GPIO.LOW)
    GPIO.cleanup()   # release resources



if __name__ == '__main__':  # Main Program Starts Here
    setup()
    try:
        read()
    except KeyboardInterrupt:   # When 'Ctrl + C is pressed, the function destroy will be called
        destroy()
    
