import pymongo

client = pymongo.MongoClient(
        "mongodb+srv://jxyong2021:Rypc9koQlPRa0KgC@esdg5.juoh9qe.mongodb.net/?retryWrites=true&w=majority")
app_db = client.get_database("job_application_db")
app_col = app_db['job_application']
for app in app_col.find():
    print(app)