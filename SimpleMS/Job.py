from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ

from Owner import Owner
from Pet import Pet

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
#"mysql+mysqlconnector://root:root@localhost:3306/job"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)

class Job(db.Model):
    __tablename__ = 'job'

    jobID = db.Column(db.String(13), primary_key =True)
    jobName = db.Column(db.String(25), nullable=False)
    phoneNum = db.Column(db.String(8), nullable = False)
    postal = db.Column(db.String(7), nullable = False)
    cardInfo = db.Column(db.String(20), nullable = False)

    #Foreign Keys
    ownerID = db.column(db.String(13), db.ForeignKey(Owner.ownerID))
    petID = db.column(db.String(13), db.ForeignKey(Pet.petID)) #yet to start Pet.py



    def __init__(self, jobID, jobName, phoneNum, postal, cardInfo, pets):
        self.jobID = jobID
        self.jobName = jobName
        self.phoneNum = phoneNum
        self.postal = postal
        self.pets = pets
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


#Function 2: Get job payment details by jobID
@app.route("/job/payment/<string:jobID>")
def get_payment_details(jobID):
    #search if job exists first with jobID
    job=job.query.filter_by(jobID=jobID).first()

    if job:
        return jsonify(
            {
                "code":200,
                "data":
                {
                    "cardInfo":job.json().cardInfo,
                    "jobNum":job.json().phoneNum
                }
            
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
