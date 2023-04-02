from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ
from datetime import datetime

from bson.objectid import ObjectId

import pymongo

client = pymongo.MongoClient("mongodb+srv://jxyong2021:Rypc9koQlPRa0KgC@esdg5.juoh9qe.mongodb.net/?retryWrites=true&w=majority")
job_db = client.get_database("job_db")
job_col = job_db['job']

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)


#Function 1: Get all jobs - to display on the interface
@app.route("/job")
def get_all():
    jobList = job_col.find()

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


#Function 2: Get job by jobid
@app.route("/job/<string:jobID>")
def getJob(jobID):
    #search if job exists first with jobID
    query={"JobID":ObjectId(jobID)}
    job=job_col.find_one(query)

    if job:
        return jsonify(
            {
                "code":200,
                "data": job.json()
            
            }
        )
    
    #if not, return job not found
    return jsonify(
            {
                "code":404,
                "message":"Job not found."
            }
        ),404



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

    #Job details
    # _id
    # OwnerID 
    # Created (Created datetime in UNIX format e.g. 1680421271) 
    # PetID (Array of pet _id involved)
    # SitterID (When a Pet Sitter is hired)
    # Title
    # Description
    # Status (Open - No Pet Sitter hired, Matched - Pet Sitter hired, Closed - Job Closed, Completed - Session linked to this job is completed)
    # Start_datetime
    # End_datetime
    # Hourly_rate
    # Payout (Amount to be paid to Pet Sitter) (Hourly rate * End_datetime - Start_datetime)
    

    details = { "name": "John", "address": "Highway 37" }

    x = mycol.insert_one(mydict)

    data = request.get_json()

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
        # data = request.get_json()
        # if data['status']:
        #     job.status = data['status']
        #     db.session.commit()
        #     return jsonify(
        #         {
        #             "code": 200,
        #             "data": job.json()
        #         }
        #     ), 200
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



if __name__ == "__main__":
    app.run(port=5005, debug=True)
