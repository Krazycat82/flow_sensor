import pyrebase

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

# data = {"name": "Mortimer 'Morty' Smith"}
# db.child("users").child("Morty").set(data)

def stream_handler(message):
    print(message["event"]) # put
    print(message["path"]) # /-K7yGTTEp7O549EzTYtI
    print(message["data"]) # {'title': 'Pyrebase', "body": "etc..."}

my_stream = db.child("users").stream(stream_handler)
my_stream.close()
