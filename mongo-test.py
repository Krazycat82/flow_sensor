from pymongo import MongoClient
# Connect to the MongoDB, change the connection string per your MongoDB environment
client = MongoClient('mongodb://thedots:vAwru&ax8zaB@ds241668.mlab.com:41668/dripdrop')

db=client.dripdrop

amount = {
    'timestamp': "2018/02/19 22:02:10",
    'amount': 0.1465,
    'duration_in_seconds': 9.3
}
result=db.amounts.insert_one(amount)

# read all back
amounts = []
for doc in db.amounts.find({}, {'_id': False}):
    print(doc)
    amounts.append(doc)
print(amounts)
