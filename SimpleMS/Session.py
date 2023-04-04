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
import datetime

from bson.objectid import ObjectId
import json
from datetime import datetime
import time
from bson.objectid import ObjectId
app = Flask(__name__)


client = pymongo.MongoClient(
    "mongodb+srv://jxyong2021:Rypc9koQlPRa0KgC@esdg5.juoh9qe.mongodb.net/?retryWrites=true&w=majority")
session_db = client.get_database("session_db")
session_col = session_db['session']


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



@app.route("/all_sessions/sitter/<string:sitter_id>")
def get_all_sitter_sessions(sitter_id):

    query = {"SitterID": ObjectId(sitter_id)}
    session_doc = session_col.find(query)
    len_session = session_db.session.count_documents(query)

@app.route("/sitter_all_sessions/<string:sitterId>")
def get_all_sitter_sessions(sitterId):
    # sessionslist = Session.query.filter_by(sitterId=sitterId)
    query= {'SitterID': ObjectId(sitterId)}
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
        "message": "No sessions are available for sitter with sitter ID: " + sitter_id
    },404

# Function 2a: get created owner's sessions based on session status (closed/in-progress/cancelled)


@app.route("/sessions/owner/<string:owner_id>/<string:status>")
def get_owner_sessions_by_status(owner_id, status):
    # sessionslist = Session.query.filter_by(ownerId=ownerId,status=status)

    query = {"OwnerID": ObjectId(owner_id),"Status": status}
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


    query = {"$and":[{"SitterID": ObjectId(sitter_id)},{"status": status}]}
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

    #Check if the session with the job_id above has already been created
    query = {"JobID": ObjectId(job_id)}
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
                                'Status': 'In Progress',
                                'sessionTimeCreated': utc_time,
                                'sessionTimeClosed':None,
                                'ownerDeposit':0,
                                'sitterPaid': 0,
                                'sitterCompleted': 0,
                                'ownerCompleted': 0
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

# Function 5: close session by updating close session time and the session status

<<<<<<< HEAD
# @app.route("on/<int/close-sessieger:sessionId>", method=['PUT'])
# def close_session(sessionId):
#     # session = Session.query.filter_by(id=sessionId).first()
#     query = {"SessionID": ObjectId(sessionId)}
#     session = session_col.find_one(query)
#     if session:
#         data = request.get_json()
#         now = datetime.now()
#         closing_time = now.strftime("%Y/%m/%d %H:%M:%S").strptime("%Y/%m/%d %H:%M:%S")
#         update_query = {"status": "In-Progress", "sessionTimeClosed": None}
#         new_values = { '$set' : {"status" : "Closed",
#                                  "sessionTimeClosed" : closing_time}}
#         session.update_one(update_query,new_values)
#         session_duration = closing_time - data['sessionTimeCreated']
#         return jsonify(
#             {
#                 "code": 200,
#                 "data":
#                 {
#                     "sessionId": sessionId,
#                     "sessionDuration": session_duration
#                 }
#             }
#         )
#     return jsonify(
#         {
#             "code": 404,
#                 "data": "Session not found."
#         }
#     ), 404
#     # if not, return session not found
=======
@app.route("/close-session/<string:sessionId>", methods=['PUT'])
def close_session(sessionId):
    # session = Session.query.filter_by(id=sessionId).first()
    query = {"_id": ObjectId(sessionId)}
    session = session_col.find_one(query)
    if session:
        closing_time = time.time()
        # closing_time = now.strftime("%Y/%m/%d %H:%M:%S")
        # closing_time = datetime.strptime(closing_time,"%Y/%m/%d %H:%M:%S")
        update_query = {"status": "In Progress", "sessionTimeClosed": None}
        new_values = { '$set' : {"status" : "Closed",
                                 "sessionTimeClosed" : closing_time}}
        session_col.update_one(query,new_values)

        # calculate session duration (in hours)
        session_duration = (closing_time - session['sessionTimeCreated'])/60/60
        return jsonify(
            {
                "code": 200,
                "data":
                {
                    "sessionId": sessionId,
                    "sessionDuration": session_duration
                }
            }
        )
    return jsonify(
        {
            "code": 404,
                "data": "Session not found."
        }
    ), 404
    # if not, return session not found
>>>>>>> 8a94c480bb6622053b01afa3e16e4ddbc8fe20dd


if __name__ == "__main__":
    app.run(port=5004, debug=True)
