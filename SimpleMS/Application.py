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

    #values needed: appID, sitterID (parent Sitter, foreign key), jobID (parent Job, foreign key), status, wait listed)

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
@app.route("/application/<integer:jobID>")
def getAll(id):
    appList=Application.query.filter_by(job_id=id)
    if appList:
        return{
            "code":200,
            "data": [app.json() for app in appList]
        }

    return{
        "code":404,
        "data": "No applications are available for jobID " + str(id)
    },404


#Function 2: Scenario - When an owner accepts a sitter for a job - To update job with accepted sitter (sitterID) and status to Matched)
#id here is the 
@app.route("/application/<integer:appID>", methods=['PUT'])
def updateSitter(id):
    #Send JSON in through placeOrder
    oldApp=Application.query.filter_by(id=id)
    db.session.delete(oldApp)
    db.session.commit()
    
    #Get new data
    data = request.get_json()
    updatedApp = Application(id, **data)

    try:
        db.session.add(updatedApp)
        db.session.commit()
    
    except:
        return jsonify(
        {
            "code":500, #internal error
            "message": "Appkication failed to update"
        }
     ),500   

    return jsonify(
        {
            "code":201,
            "data": updatedApp.json()
        }
    ),201


if __name__ == '__main__':
    # app.run(port=5001, debug=True)
    app.run(host='0.0.0.0', port=5001, debug=True)

    




    
    
