from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ
import json

from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship

from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
#"mysql+mysqlconnector://root:root@localhost:3306/pet
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)

class Session(db.Model):
    __tablename__ = 'session'

    id = db.Column(db.Integer, primary_key=True)
    ownerDeposit = db.Column(db.Boolean, nullable=False)
    sessionTimeCreated = db.Column(db.Datetime, nullable=False)
    sessionTimeClosed = db.Column(db.Datetime)
    sitterPaid = db.Column(db.Boolean, nullable=False)
    status = db.Column(db.String(11), nullable=False)
    sitterCompleted = db.Column(db.Boolean, nullable=False)
    ownerCompleted = db.Column(db.Boolean, nullable=False)

    # foreign key is jobId referring to the job table
    jobId = db.Column(db.Integer, db.ForeignKey('job.id'))
    ownerId = db.Column(db.Integer, db.ForeignKey('owner.id'))
    sitterId = db.Column(db.Integer, db.ForeignKey('sitter.id'))


    def __init__(self, id, ownerDeposit, sessionTimeCreated, sessionTimeClosed, sitterPaid, status, sitterCompleted, ownerCompleted, jobId, ownerId, sitterId):
        self.id = id
        self.ownerDeposit = ownerDeposit
        self.sessionTimeCreated = sessionTimeCreated
        self.sessionTimeClosed = sessionTimeClosed
        self.sitterPaid = sitterPaid
        self.status = status
        self.sitterCompleted = sitterCompleted
        self.ownerCompleted = ownerCompleted
        self.jobId = jobId
        self.ownerId = ownerId
        self.sitterId = sitterId

    
    def json(self):
        return {
            "id" : self.id,
            'ownerDeposit' : self.ownerDeposit,
            "sessionTimeCreated" : self.sessionTimeCreated,
            "sessionTimeClosed" : self.sessionTimeClosed,
            "sitterPaid" : self.sitterPaid,
            "status": self.status, # cancelled, closed, in-progress
            "sitterCompleted" : self.sitterCompleted,
            "ownerCompleted" : self.ownerCompleted,
            "jobId" : self.jobId
        }

#Function 1a: get all created sessions for owner
@app.route("/all_sessions/<integer:ownerId>")
def get_all_owner_sessions(ownerId):
    sessionslist = Session.query.filter_by(ownerId=ownerId)
    if len(sessionslist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "sessions": [sessionslist.json() for session in sessionslist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Owner has no sessions."
        }
    ), 404

#Function 1b: get all created sessions for sitter
@app.route("/all_sessions/<integer:sitterId>")
def get_all_sitter_sessions(sitterId):
    sessionslist = Session.query.filter_by(sitterId=sitterId)
    if len(sessionslist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "sessions": [sessionslist.json() for session in sessionslist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Sitter has no sessions."
        }
    ), 404

#Function 2a: get created owner's sessions based on session status (closed/in-progress/cancelled)
@app.route("/sessions/<integer:ownerId>/<string:status>")
def get_owner_sessions_by_status(ownerId,status):
    sessionslist = Session.query.filter_by(ownerId=ownerId,status=status)
    if len(sessionslist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "sessions": [sessionslist.json() for session in sessionslist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "No sessions found."
        }
    ), 404

#Function 2b: get created sitter's sessions based on session status (closed/in-progress/cancelled)
@app.route("/sessions/<integer:sitterId>/<string:status>")
def get_sitter_sessions_by_status(sitterId,status):
    sessionslist = Session.query.filter_by(sitterId=sitterId,status=status)
    if len(sessionslist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "sessions": [sessionslist.json() for session in sessionslist]
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
@app.route("/create_session", methods=['POST'])
def create_session():
    jobId = request.json.get('jobId')
    ownerId = request.json.get('ownerId')
    sitterId = request.json.get('sitterId')

    now = datetime.now()
    creation_time = now.strftime("%Y/%m/%d %H:%M:%S").strptime("%Y/%m/%d %H:%M:%S")

    session = Session(jobId=jobId, 
                      ownerId=ownerId,
                      sitterId=sitterId,
                      status='In Progress', sessionTimeCreated=creation_time,
                      ownerDeposit=0,
                      sitterPaid=0,
                      sitterCompleted=0,
                      ownerCompleted=0)

    # cart_item = request.json.get('cart_item')
    # for item in cart_item:
    #     session.order_item.append(Order_Item(
    #         book_id=item['book_id'], quantity=item['quantity']))

    try:
        db.session.add(session)
        db.session.commit()
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while creating the session. " + str(e)
            }
        ), 500
    
    print(json.dumps(session.json(), default=str)) # convert a JSON object to a string and print
    print()

    return jsonify(
        {
            "code": 201,
            "data": session.json()
        }
    ), 201
     

# Function 4: return session time when called
@app.route("/session-time/<integer:sessionId>")
def return_session_time(sessionId) : 
    session = Session.query.filter_by(id=sessionId).first()
    if session:
        return jsonify(
            {
                "code":200,
                "data":
                {
                    "sessionId":sessionId,
                    "sessionCreationTime":session.json().sessionTimeCreated
                }
            }
        )

    return jsonify(
            {
                "code":404,
                "data":"Session not found."
            }
        ),404

    #if not, return session not found

# Function 5: close session by updating close session time and the session status
@app.route("/close-session/<integer:sessionId>",method=['PUT'])
def close_session(sessionId) : 
    session = Session.query.filter_by(id=sessionId).first()
    if session:
        data = request.get_json()
        if data['status'] == 'In-Progress':
            session.status = 'Closed'
        now = datetime.now()
        closing_time = now.strftime("%Y/%m/%d %H:%M:%S").strptime("%Y/%m/%d %H:%M:%S")
        data['sessionTimeClosed'] = closing_time
        db.session.commit()

        session_duration = closing_time - data['sessionTimeCreated']
        return jsonify(
            {
                "code":200,
                "data":
                {
                    "sessionId":sessionId,
                    "sessionDuration":session_duration
                }
            
            }
        )

    return jsonify(
            {
                "code":404,
                "data":"Session not found."
            }
        ),404

    #if not, return session not found

if __name__ == "__main__":
    app.run(port=5003, debug=True)