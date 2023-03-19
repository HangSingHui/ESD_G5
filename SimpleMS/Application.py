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



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
#mysql+mysqlconnector://root:root@localhost:3306/application
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Application(db.Model):
    __tablename__ = 'application'

    #values needed: appID, sitterID (foreign key), jobID (foreign key), status, wait listed (nullable)


    appID = db.Column(db.String(13), primary_key =True)
    status = db.Column(db.String(50), nullable=False)
    waitList = db.Column(db.String(8), nullable = False)

    #Foreign keys
    id: Mapped[int] = mapped_column(primary_key=True)
    pets: Mapped[List["Pet.petID"]] = relationship()



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