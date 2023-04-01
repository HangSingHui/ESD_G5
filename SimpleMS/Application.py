from flask import Flask, jsonify, request
from flask_cors import CORS
from os import environ

app = Flask(__name__)
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

import pymongo

client = pymongo.MongoClient("mongodb+srv://jxyong2021:Rypc9koQlPRa0KgC@esdg5.juoh9qe.mongodb.net/?retryWrites=true&w=majority")
app_db = client.get_database("job_application_db")
app_col = app_db['job_application']

#Function 1: To get all applications given a jobID HTTP GET - by sending in jobID
@app.route("/application/<integer:jobID>")
def getAll(id):

    query = {"JobID": id}
    appList = app_col.find(query)

    if appList:
        return{
            "code":200,
            "data": [app.json() for app in appList]
        }

    return{
        "code":404,
        "data": "No applications are available for jobID " + str(id)
    },404

@app.route("/application/<integer:appID>") #1 unique ID for each app
def getAppByID(appID):

    query = {"ApplicationID": appID}
    app=app_col.find_one(query)
    
    if app:
        return{
            "code":200,
            "data": app.json()
        }

    return{
        "code":404,
        "data": "No applications are available for jobID " + str(id)
    },404



#Function 2: Scenario - When an owner accepts a sitter for a job - To update job with accepted sitter (sitterID) and status to Matched)

#Change status from Pending to Accepted for application with applicationid = id
#Change status of the remaining applications from Pending to rejected 

@app.route("/application", methods=['PUT'])
def acceptUpdate(appID):
    
    #Get new data
    data = request.get_json() 
    newStatus = data["jobStatus"]

    #Get jobID
    queryApp = {"ApplicationID":appID}
    queryJobID = {"JobID":1, "_id":0}
    jobID = app_col.find_one(queryApp,queryJobID)["JobID"]

    #Change all applications with the id=jobID from pending to rejected
    queryAll = {"JobID":jobID}
    rejectStatus = {"$set":{"Status":"Rejected"}}
    acceptStatus = {"$set":{"Status":newStatus}}



    try:
        app_col.update_all(queryAll,rejectStatus)
        app_col.update_one(queryApp,acceptStatus)

    except:
        return jsonify(
        {
            "code":500, #internal error
            "message": "Internal error. Application failed to update status from Pending to Accepted."
        }
     ),500   

    app = getAppByID(appID)

    return jsonify(
        {
            "code":201,
            "data": app["data"]
        }
    ),201






if __name__ == '__main__':
    # app.run(port=5001, debug=True)
    app.run(host='0.0.0.0', port=5008, debug=True)

    

    