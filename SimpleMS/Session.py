from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ
import json
import pymongo

from datetime import datetime

app = Flask(__name__)

client = pymongo.MongoClient(
    "mongodb+srv://jxyong2021:Rypc9koQlPRa0KgC@esdg5.juoh9qe.mongodb.net/?retryWrites=true&w=majority")
session_db = client.get_database("session_db")
session_col = session_db['session']

# Function 1a: get all created sessions for owner


@app.route("/all_sessions/<integer:ownerId>")
def get_all_owner_sessions(ownerId):
    # sessionslist = Session.query.filter_by(ownerId=ownerId)

    query = {"OwnerID": ownerId}
    sessionslist = session_col.find(query)

    if len(sessionslist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "sessions": [session.json() for session in sessionslist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Owner has no sessions."
        }
    ), 404

# Function 1b: get all created sessions for sitter


@app.route("/all_sessions/<integer:sitterId>")
def get_all_sitter_sessions(sitterId):
    # sessionslist = Session.query.filter_by(sitterId=sitterId)

    query = {"SitterID": sitterId}
    sessionslist = session_col.find(query)
    if len(sessionslist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "sessions": [session.json() for session in sessionslist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Sitter has no sessions."
        }
    ), 404

# Function 2a: get created owner's sessions based on session status (closed/in-progress/cancelled)


@app.route("/sessions/<integer:ownerId>/<string:status>")
def get_owner_sessions_by_status(ownerId, status):
    # sessionslist = Session.query.filter_by(ownerId=ownerId,status=status)

    query = {"OwnerID": ownerId,
             "status": status}
    sessionslist = session_col.find(query)

    if len(sessionslist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "sessions": [session.json() for session in sessionslist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "No sessions found."
        }
    ), 404

# Function 2b: get created sitter's sessions based on session status (closed/in-progress/cancelled)
@app.route("/sessions/<integer:sitterId>/<string:status>")
def get_sitter_sessions_by_status(sitterId, status):
    # sessionslist = Session.query.filter_by(sitterId=sitterId, status=status)

    query = {"SitterID": sitterId,
             "status": status}
    sessionslist = session_col.find(query)

    if len(sessionslist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "sessions": [session.json() for session in sessionslist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "No sessions found."
        }
    ), 404


# Function 3: create session once sitter's confirmation of taking the job is received
@app.route("/create_session/<integer:id>", methods=['POST'])
def create_session(sessionId):
    jobId = request.json.get('jobId')
    ownerId = request.json.get('ownerId')
    sitterId = request.json.get('sitterId')

    now = datetime.now()
    creation_time = now.strftime(
        "%Y/%m/%d %H:%M:%S").strptime("%Y/%m/%d %H:%M:%S")

    # session = Session(jobId=jobId,
    #                   ownerId=ownerId,
    #                   sitterId=sitterId,
    #                   status='In Progress', sessionTimeCreated=creation_time,
    #                   ownerDeposit=0,
    #                   sitterPaid=0,
    #                   sitterCompleted=0,
    #                   ownerCompleted=0)

    # cart_item = request.json.get('cart_item')
    # for item in cart_item:
    #     session.order_item.append(Order_Item(
    #         book_id=item['book_id'], quantity=item['quantity']))

    try:
        # db.session.add(session)
        # db.session.commit()
        session_col.insert_one({'JobID':jobId,
                                'OwnerID': ownerId,
                                'sitterID': sitterId,
                                'status': 'In Progress',
                                'sessionTimeCreated': creation_time,
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

    query = {"SessionID": sessionId}
    session = session_col.find_one(query)

    # convert a JSON object to a string and print
    print(json.dumps(session.json(), default=str))
    print()

    return jsonify(
        {
            "code": 201,
            "data": session.json()
        }
    ), 201


# Function 4: return session time when called
@app.route("/session-time/<integer:sessionId>")
def return_session_time(sessionId):
    # session = Session.query.filter_by(id=sessionId).first()

    query = {"SessionID": sessionId}
    session = session_col.find_one(query)

    if session:
        return jsonify(
            {
                "code": 200,
                "data":
                {
                    "sessionId": sessionId,
                    "sessionCreationTime": session.json().sessionTimeCreated
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

# Function 5: close session by updating close session time and the session status

@app.route("on/<int/close-sessieger:sessionId>", method=['PUT'])
def close_session(sessionId):
    # session = Session.query.filter_by(id=sessionId).first()

    query = {"SessionID": sessionId}
    session = session_col.find_one(query)

    if session:
        data = request.get_json()
        now = datetime.now()
        closing_time = now.strftime("%Y/%m/%d %H:%M:%S").strptime("%Y/%m/%d %H:%M:%S")

        update_query = {"status": "In-Progress", "sessionTimeClosed": None}
        new_values = { '$set' : {"status" : "Closed",
                                 "sessionTimeClosed" : closing_time}}
        session.update_one(update_query,new_values)

        session_duration = closing_time - data['sessionTimeCreated']
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


if __name__ == "__main__":
    app.run(port=5004, debug=True)
