#Reads ~ 6793 times per sec
# I learned how to count potatoes and I also learned how to make the code run faster
# Printing takes time
#
import RPi.GPIO as GPIO
import math
import requests

FlowPin = 8  # flow sensor pin
LastState = 0 #last state
#logf = open("/home/pi/flow_sensor/flow_sensor.log", "w+", 1)

import pyrebase
import datetime, time
import json

dripdropURL = "https://dots-dripdrop-api.herokuapp.com/flow_sensor/api/v1.0/amounts"
# dripdropURL = "http://0.0.0.0:5000/flow_sensor/api/v1.0/amounts"


# https://thedots-19a0e.firebaseio.com/flow_sensor

# my account
config = {
  "apiKey": "AIzaSyBREEXP3HTMN5PLfVlbJ7qIqakbzSql3KE",
  "authDomain": "thedots-19a0e.firebaseapp.com",
  "databaseURL": "https://thedots-19a0e.firebaseio.com",
  "storageBucket": "thedots-19a0e.appspot.com"
}


# Coach account
# config = {
#   "apiKey": "AIzaSyCz7orSLS09q3kcndmZ3iegqn3oXIgwRe0",
#   "authDomain": "the-dots-drip-drop.firebaseapp.com",
#   "databaseURL": "https://the-dots-drip-drop.firebaseio.com",
#   "storageBucket": "the-dots-drip-drop.appspot.com"
# }

class WaterUsage:
    def __init__(self, amount, duration_in_seconds, timestamp, user):
        self.timestamp = timestamp.strftime("%D %T")
        self.date = timestamp.strftime("%Y%m%d")
        self.week = timestamp.strftime("%Y%V")
        self.month = timestamp.strftime("%Y%m")
        self.year = timestamp.strftime("%Y")
        self.amount = amount
        self.duration_in_seconds = duration_in_seconds
        self.user = user

#flow_sensor/raw_amounts
def save_raw_amounts(amount, duration_in_seconds, timestamp, user):
    water_usage = WaterUsage(amount, duration_in_seconds, timestamp, user)
    db.child("flow_sensor").child("raw_amounts").push(water_usage.__dict__)

def update_today_amount(amount, duration_in_seconds, timestamp, user):
    key = timestamp.strftime("%Y%m%d")
    # check if need to reset/remove today's amount
    amounts = db.child("flow_sensor").child("today").order_by_child("date").equal_to(key).get()
    if len(amounts.each()) <= 0:
        print "Start new day, delete yesterday's data"
        db.child("flow_sensor").child("today").remove()
    aggregate_usage("today", "date", key, amount, duration_in_seconds, timestamp, user)

def update_daily_amount(amount, duration_in_seconds, timestamp, user):
    key = timestamp.strftime("%Y%m%d")
    aggregate_usage("daily_amounts", "date", key, amount, duration_in_seconds, timestamp, user)

def update_weekly_amount(amount, duration_in_seconds, timestamp, user):
    key = timestamp.strftime("%Y%V")
    aggregate_usage("weekly_amounts", "week", key, amount, duration_in_seconds, timestamp, user)

def update_monthly_amount(amount, duration_in_seconds, timestamp, user):
    key = timestamp.strftime("%Y%m")
    aggregate_usage("monthly_amounts", "month", key, amount, duration_in_seconds, timestamp, user)

def update_yearly_amount(amount, duration_in_seconds, timestamp, user):
    key = timestamp.strftime("%Y")
    aggregate_usage("yearly_amounts", "year", key, amount, duration_in_seconds, timestamp, user)

def aggregate_usage(aggregate_type, aggregate_by, aggregate_key, amount, duration_in_seconds, timestamp, user):
    print "aggregate_key = " + aggregate_key
    amounts = db.child("flow_sensor").child(aggregate_type).order_by_child(aggregate_by).equal_to(aggregate_key).get()
    new_amount = amount
    new_duration = duration_in_seconds
    # only loops thru if daily amounts isn't empty
    if len(amounts.each()) > 0:
        for amount in amounts.each():
            json_data = json.dumps(amount.val())
            python_obj = json.loads(json_data)
            print json_data
            prev_amount = python_obj["amount"]
            prev_duration = python_obj["duration_in_seconds"]
            new_amount = new_amount + prev_amount
            new_duration = new_duration + prev_duration
            print "new_amount = " + str(new_amount)
            print "new_duration = " + str(new_duration)
    water_usage = WaterUsage(new_amount, new_duration, timestamp, user)
    db.child("flow_sensor").child(aggregate_type).child(aggregate_key).set(water_usage.__dict__)

def get_amounts(amounts_type):
    print "+++++++++++++++++++++++ " + amounts_type + " ++++++++++++++++++++++++++++++++++"
    amounts = db.child("flow_sensor").child(amounts_type).get()
    count = 0
    if len(amounts.each()) > 0:
        for amount in amounts.each():
            json_data = json.dumps(amount.val())
            python_obj = json.loads(json_data)
            count = count + 1
            print str(count) + " - " + json_data

def process(amount, duration_in_seconds, timestamp, user):
    save_raw_amounts(amount, duration_in_seconds, timestamp, user)
    update_today_amount(amount, duration_in_seconds, timestamp, user)
    update_daily_amount(amount, duration_in_seconds, timestamp, user)
    update_weekly_amount(amount, duration_in_seconds, timestamp, user)
    update_monthly_amount(amount, duration_in_seconds, timestamp, user)
    update_yearly_amount(amount, duration_in_seconds, timestamp, user)

def setup():
    GPIO.setmode(GPIO.BOARD)  #Numbers GPIOS by Physical Location
    GPIO.setup(FlowPin, GPIO.IN) #Set FlowPin's Mode to Input

    firebase = pyrebase.initialize_app(config)
    db = firebase.database()

    print("Starting....")
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
#            logf.write("{0} {1} {2} {3} {4}\n".format(SpinsInShower, SpinsInShower * 2.25 * 0.000594389, time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime(ShowerStartTime)), int(math.ceil(ShowerTime))))
            post_amount2(SpinsInShower * 2.25 * 0.000594389, time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime(ShowerStartTime)), int(math.ceil(ShowerTime)))

        count = count + 1
        if(time.time() >= StartTime + 10):
            print(count, spins)#, flush=True)
#            logf.write("{0} {1}\n".format(count, spins))
            StartTime = time.time()
            count = 0


def post_amount2(amt, timestamp, duration_in_seconds):
    process(amt, duration_in_seconds, timestamp, "Coco")

def post_amount(amt, timestamp, duration_in_seconds):
    amount = {"amount":amt,"timestamp":timestamp, "duration_in_seconds":duration_in_seconds}
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
