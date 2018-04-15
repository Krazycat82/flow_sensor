import pyrebase
import datetime, time
import json
import random
import requests

# dripdropURL = "https://dots-dripdrop-api.herokuapp.com/flow_sensor/api/v1.0/amounts"
dripdropURL = "http://0.0.0.0:5000/flow_sensor/api/v1.0/amounts"


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

firebase = pyrebase.initialize_app(config)
db = firebase.database()

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
    key = now.strftime("%Y%m%d")
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

def post_amount(amt, duration_in_seconds, timestamp):
    amount = {"amount":amt,"timestamp":timestamp, "duration_in_seconds":duration_in_seconds}
    resp = requests.post(dripdropURL, json=amount)
    if resp.status_code != 201:
        raise ApiError('POST /amounts/ {}'.format(resp.status_code))
#    print('Created amounts. ID: {}'.format(resp.json()))

def simulate_water_usage_from_device(days_to_simulate):
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
        post_amount(amount, duration_in_seconds, now.strftime("%D %T"))
        # time.sleep( 5 )

def dump_water_usage():
    get_amounts("raw_amounts")
    get_amounts("today")
    get_amounts("daily_amounts")
    get_amounts("weekly_amounts")
    get_amounts("monthly_amounts")
    get_amounts("yearly_amounts")

###########################################################################################
# simulate today's
simulate_water_usage_from_device(1)
# simulate 16 days
# simulate_water_usage(15)
# simulate_water_usage_from_device(15)
dump_water_usage()
