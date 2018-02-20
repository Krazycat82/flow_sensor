'''
https://dots-dripdrop-api.herokuapp.com/flow_sensor/api/v1.0/amounts
TODO add discription of program
post example:
curl -i -H "Content-Type: application/json" -X POST -d  '{"amount":201,"timestamp":"2017/11/06 22:00:00", "duration_in_seconds":1245}' http://localhost:5000/flow_sensor/api/v1.0/amounts
get example:
curl http://localhost:5000/flow_sensor/api/v1.0/amounts
'''
from flask import Flask,jsonify, request
from json2html import *
from pymongo import MongoClient

# Connect to the MongoDB, change the connection string per your MongoDB environment
client = MongoClient('mongodb://thedots:vAwru&ax8zaB@ds241668.mlab.com:41668/dripdrop')
db=client.dripdrop

app = Flask(__name__) # Intializes Library

#TODO remove fake data Empty array

# amounts_array = []

# getting data
@app.route('/flow_sensor/api/v1.0/amounts', methods=['GET'])
def get_amounts():
    amounts = []
    for doc in db.amounts.find({}, {'_id': False}):
        print(doc)
        amounts.append(doc)
    print(amounts)
    return jsonify({'amounts': amounts})

# saving data
@app.route('/flow_sensor/api/v1.0/amounts', methods=['POST'])
def post_amounts():
    if not request.json or not 'amount' in request.json:
        abort(400)
    # creating a json object
    amount = {
        # 'id': ,
        'timestamp': request.json['timestamp'],
        'amount': request.json['amount'],
        'duration_in_seconds': request.json['duration_in_seconds']
    }
    # amounts_array.append(amount)   # adds amount to amounts array
    result=db.amounts.insert_one(amount)
    print(amount)
    return str(amount), 201

@app.route('/')
def index():
    infoFromJson = get_amounts()
    return "POTATO POTATO"

if __name__ == '__main__':
    app.run(host='0.0.0.0')
