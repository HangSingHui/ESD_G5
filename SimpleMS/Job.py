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

    #Foreign key - OWNER is PARENT to JOB (a job can only have 1 owner, 1 to many)
    owner_id=db.Column(db.Integer, db.ForeignKey('owner.id'))

    #Foreign key - PET is PARENT to JOB (a job can only have 1 pet, 1 to many)
    pet_id=db.Column(db.Integer, db.ForeignKey('pet.id'))

    #Foreign key - SITTER is PARENT to JOB (a job can only have 1 HIRED sitter, 1 to many, can be null, update once sitter confirmed)
    sitter_id=db.Column(db.Integer, db.ForeignKey('sitter.id'))

    #Foreign key - Job is PARENT to Application (One to Many)
    applications=db.relationship('Application',backref='job')



    def __init__(self, id, title, desc, status, startDT, endDT, payout, owner_id, pet_id, sitter_id):
       self.id = id
       self.title=title
       self.desc=desc
       self.status=status
       self.startDT=startDT
       self.endDT=endDT
       self.payout=payout
       self.owner_id=owner_id
       self.pet_id=pet_id
       self.sitter_id=sitter_id

    def json(self):
        return {
            "id": self.id,
            'title': self.title,
            "desc": self.desc,
            "startDT": self.startDT,
            "endDT": self.endDT,
            "payout":self.payout,
            "owner_id":self.owner_id,
            "pet_id":self.pet_id,
            "sitter_id":self.sitter_id
        }

#Function 1: Get all jobs - to display on the interface
@app.route("/job")
def get_all():
    jobList = Job.query.all()

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
@app.route("/job/<integer:jobID>")
def getTitle(jobID):
    #search if job exists first with jobID
    job=job.query.filter_by(jobID=id).first()

    if job:
        return jsonify(
            {
                "code":200,
                "data": job.title
            
            }
        )

    return jsonify(
            {
                "code":404,
                "data":"Job not found."
            }
        ),404


    #if not, return job not found


#Function 3: Create a new job
@app.route("/job/<integer:OwnerID>", methods=['POST'])
# URL PATH 
def create_job(owner_id):
    ## order.py lab 5 ##
    # job_id = request.json.get('job_id', None)
    # order = Job(job_id=job_id, status='NEW')

    # cart_item = request.json.get('cart_item')
    # for item in cart_item:
    #     order.order_item.append(Order_Item(
    #         book_id=item['book_id'], quantity=item['quantity']))

    #  try:
    #     db.session.add(order)
    #     db.session.commit()
    # except Exception as e:
    #     return jsonify(
    #         {
    #             "code": 500,
    #             "message": "An error occurred while creating the order. " + str(e)
    #         }
    #     ), 500

    # return jsonify(
    #     {
    #         "code": 201,
    #         "data": order.json()
    #     }
    # ), 201

    # no validation for the same job by same ownerid? 

    data = request.get_json()
    new_job = Job(owner_id, **data)

    try:
        db.session.add(new_job)
        db.session.commit()

    except:
        return jsonify(
            {
                "code": 500,
                 "data": new_job.json(),
                "message": "An error occurred creating the job."
            }
        ), 500
    
    return jsonify(
        {
            "code": 201,
            "data": new_job.json()
        }
    ), 201

#Function 4: Update job details
@app.route("/order/<string:JobID>", methods=['PUT'])
def update_order(job_id):
    try:
        job = Job.query.filter_by(JobID=job_id).first()
        if not job:
            return jsonify(
                {
                    "code": 404,
                    "data": {
                        "JobID": job_id
                    },
                    "message": "Job not found."
                }
            ), 404

        # update status
        data = request.get_json()
        if data['status']:
            job.status = data['status']
            db.session.commit()
            return jsonify(
                {
                    "code": 200,
                    "data": job.json()
                }
            ), 200
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "JobID": job_id
                },
                "message": "An error occurred while updating the order. " + str(e)
            }
        ), 500



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
    app.run(port=5005, debug=True)
