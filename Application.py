from os import environ
import json
import pymongo
import flask
from flask import Flask, jsonify, request
from flask_cors import CORS
import bson.json_util as json_util
from bson.json_util import dumps

app = flask.Flask(__name__)
CORS(app)
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

import pymongo

from bson import ObjectId

client = pymongo.MongoClient("mongodb+srv://jxyong2021:Rypc9koQlPRa0KgC@esdg5.juoh9qe.mongodb.net/?retryWrites=true&w=majority")
app_db = client.get_database("job_application_db")
app_col = app_db['job_application']


#Function 1: To get all applications given a jobID HTTP GET - by sending in jobID
@app.route("/application/job/<string:job_id>")
def getAll(job_id):

    query={"JobID":ObjectId(job_id)}

    query={"JobID":ObjectId(job_id)}

    app_doc = app_col.find(query)
    len_app = app_db.job_application.count_documents(query)

    if len_app > 0:
        list_app = list(app_doc)
        json_data = dumps(list_app)
        json_data = json.loads(json_data)
        return jsonify(
            {"code":200,
            "data": json_data
    })

    return{
        "code": 404,
        "message": "No applications are available for jobID: " + job_id
    },404
        

@app.route("/application/<string:app_id>") #1 unique ID for each app
def getAppByID(app_id):

    query={"_id":ObjectId(app_id)}
    app_doc = app_col.find_one(query)
    if app_doc is None:
        return{
            "code": 404,
            "message": "There is no application with the app id: " + app_id
        },404

    json_data = dumps(app_doc)
    json_data = json.loads(json_data)
    return jsonify(
        {"code":200,
        "data": json_data
        })

    
#TO CHANGE SELECTED APPLICATION TO REJECTED
@app.route("/application/reject_one/<string:app_id>", methods=["GET", "PUT"])
def reject_one(app_id):
    queryApp = {"_id": ObjectId(app_id)}  
    rejectStatus = {"$set":{"Status":"Rejected"}}
    try:
        app_col.update_one(queryApp,rejectStatus)
        return jsonify({
            "code": 201,
            "message": "Application status successfully changed to rejected"
        }),201
    except:
        return jsonify(
        {
            "code":500, #internal error
            "message": "Internal error. Application failed to update status from Pending to Accepted."
        }
     ),500   


#Function 2: Scenario - When an owner accepts a sitter for a job - To update job with accepted sitter (sitterID) and status to Matched)

#Change status from Pending to Accepted for application with applicationid = id
#Change status of the remaining applications from Pending to rejected 

@app.route("/application/accept/<string:app_id>", methods=['GET', 'PUT'])
def acceptUpdate(app_id):

    #Get job_id from app_id
    queryApp = {"_id": ObjectId(app_id)}  
    job_id = app_col.find_one(queryApp)["JobID"] #This returns an ObjectId
    sitter_id = app_col.find_one(queryApp)["SitterID"]
    # print(job_id)
    # print(type(job_id))

    # #Get jobID
    # queryApp = {"_id":job_id}

    #Change all applications with the id=jobID from pending to rejected
    queryAll = {"JobID":job_id}
    rejectStatus = {"$set":{"Status":"Rejected"}}
    acceptStatus = {"$set":{"Status":"Accepted"}}

    try:
        app_col.update_many(queryAll,rejectStatus)
        app_col.update_one(queryApp,acceptStatus)

    except:
        return jsonify(
        {
            "code":500, #internal error
            "message": "Internal error. Application failed to update status from Pending to Accepted."
        }
     ),500   

    #Get appid of all applications with jobid = given jobid
    waitList = []
    all_applications = getAll(job_id).json
    for data in all_applications["data"]:
        if data["Status"] == "Rejected" and data["Waitlist_if_rejected"] == "Yes":
            waitList.append(data["SitterID"]["$oid"])


    return jsonify(
        {
            "code":201,
            "message": "Application successfully updated from Pending to Accepted.",
            "data":{
                "wait_list":waitList,
                "job_id":str(job_id),
                "sitter_id":str(sitter_id)
            }
           
        }
    ),201

##Add prompt to be waitlisted
    



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5008, debug=True)

    

    