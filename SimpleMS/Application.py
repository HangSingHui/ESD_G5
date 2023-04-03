from os import environ
import json
from flask_pymongo import PyMongo
import flask
from flask import Flask, jsonify, request
from flask_cors import CORS
import bson.json_util as json_util

app = flask.Flask(__name__)
CORS(app)
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

import pymongo

from bson import ObjectId
client = pymongo.MongoClient("mongodb+srv://jxyong2021:Rypc9koQlPRa0KgC@esdg5.juoh9qe.mongodb.net/?retryWrites=true&w=majority")
app_db = client.get_database("job_application_db")
app_col = app_db['job_application']


# ObjectId = require('mongodb').ObjectID

#Function 1: To get all applications given a jobID HTTP GET - by sending in jobID
@app.route("/application/<string:jobID>")
def getAll(jobID):

    query={"JobID":ObjectId(jobID)}
    appCursor = app_col.find(query)

    # if appCursor == None:
    #     return{
    #         "code": 400,
    #         "message": "There is no job with the id "+ jobID
    #     }
    
    appList =[]

    for app in appCursor:
        appList.append(json_util.dumps(app))
    
    if len(appList)>0:

        return {
            "code":200,
            "data":appList
        }

    return{
        "code": 404,
        "message": "No applications are available for jobID: " + jobID
    },404
        

@app.route("/application/<string:appID>") #1 unique ID for each app
def getAppByID(appID):

    # query = {"ApplicationID": ObjectId(appID)}
    # app=app_col.find_one(query)
    
    # if app:
    #     return{
    #         "code":200,
    #         "data": app.json()
    #     }

    # return{
    #     "code":404,
    #     "data": "No applications are available for jobID " + str(id)
    # },404


    query={"ApplicationID":ObjectId(appID)}
    appCursor = app_col.find(query)

    # if appCursor == None:
    #     return{
    #         "code": 400,
    #         "message": "There is no applications with the id "+ jobID
    #     }
    
    appList =[]

    for app in appCursor:
        appList.append(json_util.dumps(app))
    
    if len(appList)>0:

        return {
            "code":200,
            "data":appList
        }

    return{
        "code": 404,
        "message": "No applications are available for jobID: " + jobID
    },404


#Function 2: Scenario - When an owner accepts a sitter for a job - To update job with accepted sitter (sitterID) and status to Matched)

#Change status from Pending to Accepted for application with applicationid = id
#Change status of the remaining applications from Pending to rejected 

@app.route("/application", methods=['PUT'])
def acceptUpdate():

    #Info JSON format:
    # {   
    #     "sitterID":1234,
    #     "jobID": 4567,
    #     "ownerID":7890
    #     "appID"1234,
    #     "jobStatus":"Accepted"
    # }

    #Get new data
    data = request.get_json() #get Info JSON 
    newStatus = data["jobStatus"]
    appID = data["appID"]
    jobID = data["jobID"]

    #Get jobID
    queryApp = {"_id":ObjectId(str(appID))}

    #Change all applications with the id=jobID from pending to rejected
    queryAll = {"JobID":ObjectId(str(jobID))}
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

##Add prompt to be waitlisted



if __name__ == '__main__':
    # app.run(port=5001, debug=True)
    app.run(host='0.0.0.0', port=5008, debug=True)

    

    