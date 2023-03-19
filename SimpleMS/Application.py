from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_cors import CORS
from os import environ

from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship

from SimpleMS.Job import Job



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
#mysql+mysqlconnector://root:root@localhost:3306/application
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Application(db.Model):
    __tablename__ = 'application'

    #values needed: appID, sitterID (child, foreign key), jobID (child, foreign key), status, wait listed)

    id = db.Column(db.Integer, primary_key =True)
    status = db.Column(db.String(10), nullable=False)
    waitList = db.Column(db.String(5), nullable = False)

    #Foreign keys
    job_id=db.Column(db.Integer, db.ForeignKey('job.id'))
    sitter_id=db.Column(db.Integer, db.ForeignKey('sitter.id'))


    def __init__(self, ownerID, ownerName, phoneNum, postal, cardInfo, pets):
        self.ownerID = ownerID
        self.ownerName = ownerName
        self.phoneNum = phoneNum
        self.postal = postal
        self.pets = pets
        self.cardInfo=cardInfo

    
    def json(self):
        return {
            "ownerID": self.ownerID,
            'ownerName': self.ownerName,
            "phoneNum": self.phoneNum,
            "postal": self.postal,
            "pets":self.pets,
            "cardInfo":self.cardInfo
        }

#Function 1: To get all applications given a jobID HTTP GET - by sending in jobID
@app.route("/applications/<integer:id>")
def getAllApps(id):
    
    
