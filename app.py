'''
https://dots-dripdrop-api.herokuapp.com/flow_sensor/api/v1.0/amounts
TODO add discription of program
post example:
curl -i -H "Content-Type: application/json" -X POST -d  '{"amount":0.1201,"timestamp":"Thu, 24 May 2018 00:10:56 +0000", "duration_in_seconds":10.1, "household":"Family_C"}' http://localhost:5000/flow_sensor/api/v1.0/amounts
curl -i -H "Content-Type: application/json" -X POST -d  '{"amount":0.1201,"timestamp":"Thu, 24 May 2018 00:10:56 +0000", "duration_in_seconds":10.1, "household":"Family_C"}' https://dots-dripdrop-api.herokuapp.com/flow_sensor/api/v1.0/amounts
get example:
curl http://localhost:5000/flow_sensor/api/v1.0/amounts?household=Family_B
curl https://dots-dripdrop-api.herokuapp.com/flow_sensor/api/v1.0/amounts?household=Family_B

'''
from flask import Flask,jsonify, request
from json2html import *
import pyrebase
import datetime, time
import json
import random

demo_family = "Family_Demo"

# https://thedots-19a0e.firebaseio.com/flow_sensor

# my account
# config = {
#   "apiKey": "AIzaSyBREEXP3HTMN5PLfVlbJ7qIqakbzSql3KE",
#   "authDomain": "thedots-19a0e.firebaseapp.com",
#   "databaseURL": "https://thedots-19a0e.firebaseio.com",
#   "storageBucket": "thedots-19a0e.appspot.com"
# }

# Coach account
config = {
  "apiKey": "AIzaSyCz7orSLS09q3kcndmZ3iegqn3oXIgwRe0",
  "authDomain": "the-dots-drip-drop.firebaseapp.com",
  "databaseURL": "https://the-dots-drip-drop.firebaseio.com",
  "storageBucket": "the-dots-drip-drop.appspot.com"
}

print "databaseURL=" + config["databaseURL"]
firebase = pyrebase.initialize_app(config)
db = firebase.database()

class WaterUsage:
    def __init__(self, amount, duration_in_seconds, timestamp, household, number_of_sessions):
        self.timestamp = timestamp.strftime("%D %T")
        self.date = timestamp.strftime("%Y%m%d")
        self.week = timestamp.strftime("%Y%V")
        self.month = timestamp.strftime("%Y%m")
        self.year = timestamp.strftime("%Y")
        self.amount = amount
        self.duration_in_seconds = duration_in_seconds
        self.household = household
        self.number_of_sessions = number_of_sessions

class WaterUsageSummary:
    def __init__(self, amount, number_of_sessions):
        self.amount = amount
        self.number_of_sessions = number_of_sessions

def time2str(t):
    return t.strftime("%d %b %Y %H:%M:%S")

#flow_sensor/raw_amounts
def save_raw_amounts(amount, duration_in_seconds, timestamp, household):
    print "++++ save_raw_amounts: amount=" + str(amount) + " duration=" + str(duration_in_seconds) + " timestamp=" + time2str(timestamp)
    water_usage = WaterUsage(amount, duration_in_seconds, timestamp, household, 1)
    db.child(household).child("flow_sensor_1").child("raw_amounts").push(water_usage.__dict__)
    return water_usage

def update_today_amount(amount, duration_in_seconds, timestamp, household):
    print "++++ update_today_amount: amount=" + str(amount) + " duration=" + str(duration_in_seconds) + " timestamp=" + time2str(timestamp)
    key = timestamp.strftime("%Y%m%d")
    # check if need to reset/remove today's amount
    amounts = db.child(household).child("flow_sensor_1").child("today").order_by_child("date").equal_to(key).get()
    if len(amounts.each()) <= 0:
        print "Start new day, delete yesterday data"
        db.child(household).child("flow_sensor_1").child("today").remove()
    aggregate_usage("today", "date", key, amount, duration_in_seconds, timestamp, household)

def update_daily_amount(amount, duration_in_seconds, timestamp, household):
    print "++++ update_daily_amount: amount=" + str(amount) + " duration=" + str(duration_in_seconds) + " timestamp=" + time2str(timestamp)
    key = timestamp.strftime("%Y%m%d")
    aggregate_usage("daily_amounts", "date", key, amount, duration_in_seconds, timestamp, household)

def update_weekly_amount(amount, duration_in_seconds, timestamp, household):
    print "++++ update_weekly_amount: amount=" + str(amount) + " duration=" + str(duration_in_seconds) + " timestamp=" + time2str(timestamp)
    key = timestamp.strftime("%Y%V")
    aggregate_usage("weekly_amounts", "week", key, amount, duration_in_seconds, timestamp, household)

def update_monthly_amount(amount, duration_in_seconds, timestamp, household):
    print "++++ update_monthly_amount: amount=" + str(amount) + " duration=" + str(duration_in_seconds) + " timestamp=" + time2str(timestamp)
    key = timestamp.strftime("%Y%m")
    aggregate_usage("monthly_amounts", "month", key, amount, duration_in_seconds, timestamp, household)

def update_yearly_amount(amount, duration_in_seconds, timestamp, household):
    print "++++ update_yearly_amount: amount=" + str(amount) + " duration=" + str(duration_in_seconds) + " timestamp=" + time2str(timestamp)
    key = timestamp.strftime("%Y")
    aggregate_usage("yearly_amounts", "year", key, amount, duration_in_seconds, timestamp, household)

def aggregate_usage(aggregate_type, aggregate_by, aggregate_key, amt, duration_in_seconds, timestamp, household):
    print "++++ aggregate_usage: aggregate_type" + aggregate_type + " aggregate_by=" + aggregate_by + " aggregate_key=" + aggregate_key + " amount=" + str(amt) + " duration=" + str(duration_in_seconds) + " timestamp=" + time2str(timestamp)
    amounts = db.child(household).child("flow_sensor_1").child(aggregate_type).order_by_child(aggregate_by).equal_to(aggregate_key).get()
    new_amount = amt
    new_duration = duration_in_seconds
    prev_amount = 0
    prev_duration = 0
    prev_sessions = 0
    new_sessions = 1 # always default to 1
    # only loops thru if daily amounts isn't empty
    if len(amounts.each()) > 0:
        for amount in amounts.each():
            json_data = json.dumps(amount.val())
            python_obj = json.loads(json_data)
            print json_data
            prev_amount = python_obj["amount"]
            prev_duration = python_obj["duration_in_seconds"]
            if 'number_of_sessions' in python_obj:
                prev_sessions = python_obj["number_of_sessions"]
            else:
                prev_sessions = 1 # assume there is at least 1
            new_amount = new_amount + prev_amount
            new_duration = new_duration + prev_duration
            new_sessions = new_sessions + prev_sessions
            # print "new_amount = " + str(new_amount)
            # print "new_duration = " + str(new_duration)
            # print "new_sessions = " + str(new_sessions)
    water_usage = WaterUsage(new_amount, new_duration, timestamp, household, new_sessions)
    print "*** prev_amount=" + str(prev_amount) + " prev_duration= " + str(prev_duration) + "*** amount=" + str(amt) + " duration= " + str(duration_in_seconds)
    print "*** prev_sessions=" + str(prev_sessions) + "*** new sessions=" + str(new_sessions)
    print "*** New WaterUsage: " + json.dumps(water_usage.__dict__)
    db.child(household).child("flow_sensor_1").child(aggregate_type).child(aggregate_key).set(water_usage.__dict__)
    # TODO: hack solution for now
    if aggregate_type == "yearly_amounts":
        water_usage_summary = WaterUsageSummary(new_amount, new_sessions)
        db.child(household).child("profile").child("total_amount").update(water_usage_summary.__dict__)

def get_usage_amounts(amounts_type, household):
    print "++++ " + household + ": " + amounts_type + ": "
    amounts = db.child(household).child("flow_sensor_1").child(amounts_type).get()
    count = 0
    if len(amounts.each()) > 0:
        for amount in amounts.each():
            json_data = json.dumps(amount.val())
            python_obj = json.loads(json_data)
            count = count + 1
            print str(count) + " - " + json_data
        # TODO return all the amounts not just the last one
    return json_data

#
# rules:
# amount/min > 1.0 G/M
# duration in seconds > 10
def is_valid_data(household, amount, duration_in_seconds):
    is_valid = False

    if (household == demo_family):
        is_valid = True
    else:
        if duration_in_seconds > 10:
            if (amount/(duration_in_seconds/60.0) > 1.0):
                is_valid = True
    
    print "++++ is_valid_data:", household, amount, (duration_in_seconds/60.0), is_valid
    
    return is_valid

def process(amount, duration_in_seconds, timestamp, household):

    water_usage = save_raw_amounts(amount, duration_in_seconds, timestamp, household)
    # only aggregate if duration > 10s or we are demo'ing household name = demo family name
    is_valid = is_valid_data(household, amount, duration_in_seconds)
    if (is_valid):
        update_today_amount(amount, duration_in_seconds, timestamp, household)
        update_daily_amount(amount, duration_in_seconds, timestamp, household)
        update_weekly_amount(amount, duration_in_seconds, timestamp, household)
        update_monthly_amount(amount, duration_in_seconds, timestamp, household)
        update_yearly_amount(amount, duration_in_seconds, timestamp, household)
    return water_usage

### Simulation days of data
def simulate_water_usage(days_to_simulate):
    if days_to_simulate > 1:
        days_to_simulate_str = "last " + str(days_to_simulate) + " days."
    else:
        days_to_simulate_str = "today."
    print "Simulate water usage for " + days_to_simulate_str
    start_date = datetime.datetime.now() - datetime.timedelta(days=(days_to_simulate-1))
    count = 0
    while (count < days_to_simulate):
        now = start_date + datetime.timedelta(days=count)
        count = count + 1
        duration_in_seconds = random.uniform(15, 20) * 60
        print str(count) + " - " + str(now)

        # 2.5 gallons a minute
        amount = 2.5 * duration_in_seconds
        process(amount, duration_in_seconds, now, "Coco")
        # time.sleep( 5 )

def dump_water_usage(household):
    get_usage_amounts("raw_amounts", household)
    get_usage_amounts("today", household)
    get_usage_amounts("daily_amounts", household)
    get_usage_amounts("weekly_amounts", household)
    get_usage_amounts("monthly_amounts", household)
    get_usage_amounts("yearly_amounts", household)

app = Flask(__name__) # Intializes Library

#TODO remove fake data Empty array

# amounts_array = []

# getting data
@app.route('/flow_sensor/api/v1.0/amounts', methods=['GET'])
def get_amounts():
    household = request.args.get('household')    
    amounts = get_usage_amounts("today", household)
    # amounts = get_usage_amounts("raw_amounts")
    print "get_amounts: " + amounts
    return "{\"today\":" + amounts + " }"

# saving data
@app.route('/flow_sensor/api/v1.0/amounts', methods=['POST'])
def post_amounts():
    if not request.json or not 'amount' in request.json:
        abort(400)
    # creating a json object
    amount = request.json['amount']
    duration_in_seconds = request.json['duration_in_seconds']
    household = request.json['household']
    timestamp = datetime.datetime.strptime(request.json['timestamp'], '%a, %d %b %Y %H:%M:%S +0000')
    # timestamp = request.json['timestamp']
    # timestamp = datetime.datetime.now()
    water_usage = process(amount, duration_in_seconds, timestamp, household)

    print(water_usage.__dict__)
    return str(water_usage.__dict__), 201

@app.route('/')
def index():
    infoFromJson = get_amounts()
    return "POTATO POTATO"

if __name__ == '__main__':
    app.run(host='0.0.0.0')
