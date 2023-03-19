from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ

from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship

from SimpleMS.Sitter import Sitter
from SimpleMS.Notification import Notification

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
#"mysql+mysqlconnector://root:root@localhost:3306/pet
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)

class Session(db.Model):
    __tablename__ = 'session'

    id = db.Column(db.Integer, primary_key=True)
    owner_deposit = db.Column(db.Boolean, nullable=False)
    sitterPaid = db.Column(db.Boolean, nullable=False)
    status = db.Column(db.String(11), nullable=False)
    sitterCompleted = db.Column(db.Boolean, nullable=False)
    ownerCompleted = db.Column(db.Boolean, nullable=False)

    # foreign key is jobId referring to the job table
    jobId = db.Column(db.Integer, db.ForeignKey('job.id'))



    def __init__(self, id, ownerDeposit, sitterPaid, status, sitterCompleted, ownerCompleted, jobId):
        self.id = id
        self.ownerDeposit = ownerDeposit
        self.sitterPaid = sitterPaid
        self.status = status
        self.siterCompleted = sitterCompleted
        self.ownerCompleted = ownerCompleted
        self.jobId = jobId

    
    def json(self):
        return {
            "id": self.id,
            'ownerDeposit': self.ownerDeposit,
            "sitterPaid": self.sitterPaid,
            "status": self.status,
            "sitterCompleted" : self.sitterCompleted,
            "ownerCompleted" : self.ownerCompleted,
            "jobId" : self.jobId
        }

#Function 1: get all created sessions (all/completed/in-progress/cancelled)
# @app.route("/sessions/")
# def create_session(jobId) : 



# Function 2: create session once sitter's confirmation of taking the job is received
# @app.route("/create-session")
# def create_session(jobId) : 
     




if __name__ == "__main__":
    app.run(port=5004, debug=True)