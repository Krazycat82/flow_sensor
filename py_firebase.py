import pyrebase
import time
import json

config = {
  "apiKey": "AIzaSyBREEXP3HTMN5PLfVlbJ7qIqakbzSql3KE",
  "authDomain": "thedots-19a0e.firebaseapp.com",
  "databaseURL": "https://thedots-19a0e.firebaseio.com",
  "storageBucket": "thedots-19a0e.appspot.com"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

#rest/flow_sensor/daily_amounts

# all_daily_amounts = db.child("rest").child("flow_sensor").child("daily_amounts").get()
# for daily in all_daily_amounts.each():
#     print(daily.val())
#     print(daily.key())

# data = {"name": "Mortimer 'Morty' Smith"}
# db.child("users").push(data)

# data = {"name": "Jane Doe", "score": 10}
# db.child("users").child("Jane").set(data)
# time.sleep( 5 )
#
# data = {
#     "users/Morty/": {
#         "name": "Mortimer 'Morty' Smith",
#         "score": 10
#     },
#     "users/Rick/": {
#         "name": "Rick Sanchez",
#         "score": 3
#     }
# }
#
# db.update(data)
# time.sleep( 5 )
#
all_users = db.child("users").get()
# print(all_users.val())
for user in all_users.each():
    print(user.key()) # Morty
    print(user.val())
    json_data = json.dumps(user.val())
    python_obj = json.loads(json_data)
    name = python_obj["name"]
    score = python_obj["score"]
    print "name=" + name
    print "score=" + str(score)
# time.sleep( 5 )
#
# users_by_name = db.child("users").order_by_child("name").get()
# for user in users_by_name.each():
#     print(user.key()) # Morty
#     print(user.val()) # {name": "Mortimer 'Morty' Smith"}
# time.sleep( 5 )
#
# users_by_name = db.child("users").order_by_child("score").equal_to(10).get()
# for user in users_by_name.each():
#     print(user.key()) # Morty
#     print(user.val()) # {name": "Mortimer 'Morty' Smith"}
# time.sleep( 5 )

# https://thedots-19a0e.firebaseio.com/rest/flow_sensor
