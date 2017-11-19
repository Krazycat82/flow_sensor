'''

TODO add discription of program
post example:
curl -i -H "Content-Type: application/json" -X POST -d  '{"amount":201,"timestamp":"2017/11/06 22:00:00", "duration_in_seconds":1245}' http://localhost:5000/flow_sensor/api/v1.0/amounts
get example:
curl http://localhost:5000/flow_sensor/api/v1.0/amounts
'''
from flask import Flask,jsonify, request

app = Flask(__name__) # Intializes Library

#TODO remove fake data Empty array
amounts_array = [
    {
        'id': 1,
        'timestamp': '2017/11/04 22:00:00',
        'amount': 123,
        'duration_in_seconds': 1245
    },
    {
        'id': 2,
        'timestamp': '2017/11/05 22:08:12',
        'amount': 122,
        'duration_in_seconds': 1243
    }
]
    
# getting data
@app.route('/flow_sensor/api/v1.0/amounts', methods=['GET']) 
def get_amounts():
    return jsonify({'amounts': amounts_array})

# saving data
@app.route('/flow_sensor/api/v1.0/amounts', methods=['POST'])
def post_amounts():
    if not request.json or not 'amount' in request.json:
        abort(400)

    # creating a json object
    amount = {
        'id': amounts[-1]['id'] + 1,  # amounts[-1] last element
        'timestamp': request.json['timestamp'],
        'amount': request.json['amount'],
        'duration_in_seconds': request.json['duration_in_seconds']
    }
    amounts_array.append(amount)   # adds amount to amounts array
    return jsonify({'amount': amount}), 201

@app.route('/')
def index():
    return "POTATO POTATO"

if __name__ == '__main__':
    app.run(host='0.0.0.0')
