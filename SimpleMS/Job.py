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

from SimpleMS.Application import Application


class Base(DeclarativeBase):
    pass

from SimpleMS.Owner import Owner
from SimpleMS.Pet import Pet
from SimpleMS.Sitter import Sitter

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
#"mysql+mysqlconnector://root:root@localhost:3306/job"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)

class Job(db.Model):
    __tablename__ = 'job'

    id = db.Column(db.Integer, primary_key =True)

    title = db.Column(db.String(25), nullable=False)
    desc=db.Column(db.Text, nullable =False)
    status = db.Column(db.String(8), nullable = False)
    startDT = db.Column(db.DateTime(), nullable=False)
    endDT = db.Column(db.DateTime(), nullable=False)
    payout= db.Column(db.Float(2), nullable=False)

    #Foreign key - Job is PARENT to Application (One to Many)
    applications=db.relationship('Application',backref='job')

   
    #Foreign Keys - not updated yet
    # ownerID = db.column(db.String(13), db.ForeignKey(Owner.ownerID)) #one owner many job (one to many)
    # petID = db.column(db.String(13), db.ForeignKey(Pet.petID)) #one pet to many job (one to many)
    # sitterID= db.column(db.String(13), db.ForeignKey(Sitter.sitterID), nullable=True) #one sitter to many job 


    def __init__(self, jobID, jobTitle, jobDescription, status, startDT, endDT, payout, ownerID, petID, sitterID):
        self.jobID = jobID
        self.jobTitle = jobTitle
        self.jobDescription= jobDescription
        self.status = status
        self.start= pets
        self.cardInfo=cardInfo
    
    def json(self):
        return {
            "jobID": self.jobID,
            'jobName': self.jobName,
            "phoneNum": self.phoneNum,
            "postal": self.postal,
            "pets":self.pets,
            "cardInfo":self.cardInfo
        }

#Function 1: Get all jobs - to display on the interface
@app.route("/job")
def get_all():
    jobList = job.query.all()

    if len(jobList):
        return jsonify(
            {
                "code":200, 
                "data": [job.json() for job in jobList]
            }
        )
    
    return jsonify(
        {
            "code": 404,
            "message": "There are no jobs"
        }
    ), 404


#Function 2: Get job title by jobID
@app.route("/accept/<string:jobID>")
def get_jobTitle(jobID):
    #search if job exists first with jobID
    job=job.query.filter_by(jobID=jobID).first()

    if job:
        return jsonify(
            {
                "code":200,
                "data": job.
            
            }
        )

    return jsonify(
            {
                "code":404,
                "data":"job not found."
            }
        ),404


    #if not, return job not found


#Function 3: Create a new job

#Function 4: Update job details


# @app.route("/job/<string:jobID>")
# def find_by_jobID(jobID):
#     job = job.query.filter_by(isbn13=isbn13).first()
#     if (job):
#         return jsonify(
#             {
#                 "code": 200,
#                 "data": job.json()
#             }
#         )
    
#     return jsonify(
#         {
#             "code":404,
#             "message": "job not found"
#         }
#     ),404


# @app.route("/job/<string:isbn13>", methods=['POST'])
# def create_job(isbn13):
#     if (job.query.filter_by(isbn13=isbn13).first()):
#         return jsonify(
#             {
#                 "code": 400,
#                 "data": {
#                     "isbn13": "1234567890123"
#                 },
#                 "message": "job already exists"
#             }
#         ),400
    
#     #get user input, where user input is request in JSON format
#     #get_json() converts user input to PYTHON DATA
#     data = request.get_json()
#     #Create instance of the job
#     job = job(isbn13, **data)
   
#     try:
#         #add the job 
#         db.session.add(job)
#         #commit the changes
#         db.session.commit


#     except:
#         return jsonify(
#             {
#                 "code": 500,
#                 "data": {
#                     "isbn13": "1234567890123"
#                 },
#                 "message": "An error occured creating the job."
#             }
#         ),500
    
#     return jsonify(
#         {
#             "code":201,
#             "data": job.json()
#         }
#     ),201

# @app.route("/job/<string:isbn13>", methods=['PUT'])
# def update_job(isbn13):
#     #delete old job
#     old_job = job.query.filter_by(isbn13=isbn13).first()
#     db.session.delete(old_job)
#     db.session.commit()

#     #Get new data
#     data = request.get_json()
#     new_job = job(isbn13, **data)

#     try:
#         db.session.add(new_job)
#         db.session.commit()
    
#     except:
#         return jsonify(
#         {
#             "code":500,
#             "message": "job failed to update"
#         }
#      ),500   

#     return jsonify(
#         {
#             "code":201,
#             "data": new_job.json()
#         }
#     ),201

# @app.route("/job/<string:isbn13>", methods=['DELETE'])
# def delete_job(isbn13):
#     job = job.query.filter_by(isbn13 = isbn13).first()
#     if (job):
#         db.session.delete(job)
#         db.session.commit()
#         return(
#             {
#                 "code":201,
#                 "isbn13": isbn13
#             }
#         ),201
    
#     return(
#         {
#             "code":404, 
#             "data":{
#                 "isbn13": isbn13
#             },
#             "message": "job not found"
#         }
#     ),404


if __name__ == "__main__":
    app.run(port=5000, debug=True)
