#Reads ~ 37 times per sec
import RPi.GPIO as GPIO
import time

FlowPin = 8  # flow sensor pin
LastState = 0 #last state

def setup():
    GPIO.setmode(GPIO.BOARD)  #Numbers GPIOS by Physical Location
    GPIO.setup(FlowPin, GPIO.IN) #Set FlowPin's Mode to Input
    
def read():
    LastState = GPIO.input(FlowPin)
    count = 0
    while True:
        CurrentState = GPIO.input(FlowPin)
        
        if GPIO.input(FlowPin):
            print('Input was high')
        else:
            print('Input was low')
            
        if (CurrentState == LastState):
            print('No Change')
        else:
            if (CurrentState == 1):
                print('One Spin')
            else:
                print('No Spin')
            LastState = CurrentState
            
        #time.sleep(1)
        #GPIO.output(LedPin, GPIO.LOW)
        #time.sleep(1)
        count = count + 1
        if count % 100 == 0:
            print('POTATO POTATO POTATO POTATO POTATO')
        
def destroy():
    # GPIO.output(LedPin, GPIO.LOW)
    GPIO.cleanup()   # release resources



if __name__ == '__main__':  # Main Program Starts Here
    setup()
    try:
        read()
    except KeyboardInterrupt:   # When 'Ctrl + C is pressed, the function destroy will be called
        destroy()
    
