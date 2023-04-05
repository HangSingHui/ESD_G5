from os import environ
import json
# from flask_pymongo import pymongo
import pymongo
import flask
from flask import Flask, jsonify, request
from flask_cors import CORS
import bson.json_util as json_util
from bson.json_util import dumps
import calendar
from bson.objectid import ObjectId
import json
from datetime import datetime
import datetime
import time
from bson.objectid import ObjectId
import calendar
app = Flask(__name__)
CORS(app)

client = pymongo.MongoClient(
    "mongodb+srv://jxyong2021:Rypc9koQlPRa0KgC@esdg5.juoh9qe.mongodb.net/?retryWrites=true&w=majority")
session_db = client.get_database("session_db")
session_col = session_db['session']


#Function: Get session by sessionID
@app.route("/session/<string:sessionID>")
def getsession(sessionID):
    #search if session exists first with sessionID
    query={"_id":ObjectId(sessionID)}
    #job=job_col.find(query)
   
    num_sessions = session_db.session.count_documents(query)
    session = session_col.find(query)
    if num_sessions> 0:
        session = list(session)
        json_data = dumps(session)
        json_data = json.loads(json_data)
    
        return jsonify(
            {
                "code":200,
                "data": json_data
            }
        )
    #if not, return job not found
    return jsonify(
            {
                "code":404,
                "message":"Session not found."
            }
        ),404




# Function 1a: get all created sessions for owner

@app.route("/all_sessions/owner/<string:owner_id>")
def get_all_owner_sessions(owner_id):

    query = {"OwnerID": ObjectId(owner_id)}
    session_doc = session_col.find(query)
    len_session = session_db.session.count_documents(query)
    if len_session > 0:
        list_session = list(session_doc)
        json_data = dumps(list_session)
        json_data = json.loads(json_data)

        return jsonify({"code":200,
            "data": json_data})

    return{
        "code": 404,
        "message": "No sessions are available for owner with owner ID: " + owner_id
    },404


@app.route("/sitter_all_sessions/<string:sitterId>")
def get_all_sitter_sessions(sitterId):
    # sessionslist = Session.query.filter_by(sitterId=sitterId)
    query= {'sitterID': ObjectId(sitterId)}
    sessions = session_col.find(query)
    num_sessions = session_db.session.count_documents(query)
    if num_sessions>0:
        sessions = list(sessions)
        json_data = dumps(sessions)
        json_data = json.loads(json_data)

        return jsonify({"code":200,
            "data": json_data})

    return{
        "code": 404,
        "message": "No sessions are available for sitter with sitter ID: " + sitterId
    },404

# Function 2a: get created owner's sessions based on session status (closed/in-progress/cancelled)
@app.route("/sessions/owner/<string:owner_id>/<string:status>")
def get_owner_sessions_by_status(owner_id, status):
    # sessionslist = Session.query.filter_by(ownerId=ownerId,status=status)

    query = {"OwnerID": ObjectId(owner_id),"status": status}
    session_doc = session_col.find(query)
    len_session = session_db.session.count_documents(query)

    if len_session > 0:
        list_session = list(session_doc)
        json_data = dumps(list_session)
        json_data = json.loads(json_data)

        return jsonify({"code":200,
            "data": json_data})

    return{
        "code": 404,
        "message": "No sessions with the status" + status +" is available for the owner with owner id: " + owner_id
    },404

# Function 2b: get created sitter's sessions based on session status (closed/in-progress/cancelled)
@app.route("/sessions/sitter/<string:sitter_id>/<string:status>")
def get_sitter_sessions_by_status(sitter_id, status):

    query = {"sitterID": ObjectId(sitter_id),"status": status}
    #query = {"$and":[{"SitterID": ObjectId(sitter_id)},{"status": status}]}
    session_doc = session_col.find(query)
    len_session = session_db.session.count_documents(query)

    if len_session > 0:
        list_session = list(session_doc)
        json_data = dumps(list_session)
        json_data = json.loads(json_data)

        return jsonify({"code":200,
            "data": json_data})

    return{
        "code": 404,
        "message": "No sessions with the status " + status +" is available for the sitter with sitter id: " + sitter_id
    },404


# Function 3: create session once sitter's confirmation of taking the job is received
@app.route("/session/create_session/<string:job_id>", methods=['POST'])
def create_session(job_id):
    #Only these 3 are sent as a request
    owner_id = request.json.get('OwnerID')
    sitter_id = request.json.get('SitterID')

    #Check if the session with the job_id above has already been created and in not closed
    query = {"$and":[{"JobID": ObjectId(job_id)},{"status":"In-Progress"}]}

    session_doc = session_col.find_one(query)
    if not session_doc is None:
        return jsonify({
            "code":400,
            "message":"A session with the job_id " + job_id + " already exists! Please remove previous session before creating a new session!"
        })

    #Get current date time to log when session is created
    date = datetime.datetime.utcnow()
    utc_time = calendar.timegm(date.utctimetuple())


    try:

        session_col.insert_one({'JobID':ObjectId(job_id),
                                'OwnerID': ObjectId(owner_id),
                                'sitterID': ObjectId(sitter_id),
                                'status': 'In-Progress',
                                'sessionTimeCreated': utc_time,
                                'sessionTimeClosed':None,
                                'ownerDeposit':0,
                                'sitterPaid': 0,
                                'sitterCompleted': 0,
                                'ownerCompleted': 0,
                                'Price_Id':""
                                })
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while creating the session. " + str(e)
            }
        ), 500

    # query = {"SessionID": ObjectId(sessionId)}
    # session = session_col.find_one(query)

    # # convert a JSON object to a string and print
    # print(json.dumps(session.json(), default=str))
    # print()

    return jsonify(
        {
            "code": 201,
            "data": "New session is created."
        }
    ), 201

#WHAT IS THIS FOR????? >:(
# # Function 4: return session time when called
# @app.route("/session-time/<string:sessionId>")
# def return_session_time(sessionId):
#     # session = Session.query.filter_by(id=sessionId).first()

#     query = {"SessionID": ObjectId(sessionId)}
#     session = session_col.find_one(query)

#     if session:
#         return jsonify(
#             {
#                 "code": 200,
#                 "data":
#                 {
#                     "sessionId": sessionId,
#                     "sessionCreationTime": session.json().sessionTimeCreated
#                 }
#             }
#         )

#     return jsonify(
#         {
#             "code": 404,
#                 "data": "Session not found."
#         }
#     ), 404

    # if not, return session not found

#Function: Cancel session -> Update session to "Closed" and add column "sessionTimeClosed"
@app.route("/cancel-session/<string:sessionId>", methods=['PUT'])
def cancel_session(sessionId):
    query= {'_id': ObjectId(sessionId)}
    session = session_col.find(query)
    num_sessions = session_db.session.count_documents(query)
    print(num_sessions)
    #IF SESSION FOUND
    if num_sessions > 0:
        date = datetime.datetime.utcnow()
        utc_time = calendar.timegm(date.utctimetuple())
        closestatus = {"$set":{"status": "Cancelled","sessionTimeCancelled": utc_time}}

        try:
            session_col.update_one(query, closestatus)

            return jsonify(
            {
                "code": 200,
                "data": {
                    "SessionID": sessionId,
                    "sessionTimeCancelled" : utc_time
                },
                "message": "Job status changed to cancelled and sessionTimeCancelled added"
            }
        ), 200

        except Exception as e:
            return jsonify(
                {
                    "code": 500,
                    "data": {
                        "JobID": sessionId
                    },
                    "message": "An error occurred while cancelling the session" 
                }
            ), 500


#
@app.route("/session/addPrice/<string:job_id>",methods=["PUT"])
def update_price_id(job_id):
    price_id = request.get_json()
    print(price_id)
    # price_id = price_id["price_id"]
    print(price_id)
    print(type(price_id))
    print(job_id)
    query = {"$and": [{"JobID":ObjectId(job_id)},{"status":"In-Progress"}]}

    result = session_col.find(query)
    len_session = session_db.session.count_documents(query)
    print(len_session)
   
    update_price = {"$set":{"Price_Id":str(price_id)}}

    try:
        test = session_col.update_many(query,update_price)
    
    except:
        return jsonify(
        {
            "code":500, #internal error
            "message": "Internal error. Application failed to update status from Pending to Accepted."
        }
     ),500   
    

    return jsonify({
        "code":200,
        "message": "Successfully updated price_id for open session with job id: " + job_id
    })

@app.route("/session/get-session-by-price/<string:priceID>")
def getSessionByPrice(priceID):
    #search if session exists first with sessionID
    print(priceID)
    query= {'Price_Id': priceID}
    print(query)
    session_doc = session_col.find_one(query)
    # print(session)
    # owner_id = session["OwnerID"]
    # print(owner_id)


    if session_doc is None:
        return {
            "code":404,
            "message":"Session not found."
        },404
    
    print("here")
    print(session_doc)
    print(str(session_doc["OwnerID"]))
    # json_data = dumps(session_doc)
    # json_data = json.loads(session_doc)

    return{
            "code":200,
            "data": str(session_doc["OwnerID"])
        }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004, debug=True)
