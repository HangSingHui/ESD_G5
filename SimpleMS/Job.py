from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ
from datetime import datetime
from bson.json_util import dumps
from bson.objectid import ObjectId
import json
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
    num_jobs = job_db.job.count_documents({})
    if num_jobs > 0:
        jobs = list(jobList)
        json_data = dumps(jobs)
        json_data = json.loads(json_data)
        return jsonify(
            {
                "code":200, 
                "data": json_data
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
    query={"_id":ObjectId(jobID)}
    #job=job_col.find(query)
    num_jobs = job_db.job.count_documents(query)
    job = job_col.find(query)
    if num_jobs > 0:
        jobs = list(job)
        json_data = dumps(jobs)
        json_data = json.loads(json_data)
    
        return jsonify(
            {
                "code":200,
                "data": json_data
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
<<<<<<< Updated upstream
@app.route("/createjob/<string:OwnerID>", methods=['POST'])
=======
@app.route("/createjob/<string:OwnerID>", methods=["POST"])
>>>>>>> Stashed changes
# URL PATH 
def create_job(OwnerID):

    

    # no validation for the same job by same ownerid? 
    # SitterID (When a Pet Sitter is hired)
    '''
    ownerId = owner_id
    title = request.json.get('Title')
    desc = request.json.get('Description')
    start_datetime = request.json.get('Start_datetime')
    end_datetime = request.json.get('End_datetime')
    rate = request.json.get('Hourly_rate')  
    numHours = find_hours(start_datetime, end_datetime) #strings in seconds if correct
    payout = format(numHours * rate, '.2f')
    pets = request.json.get('PetID')

    now = datetime.now()
    creation_time = now.strftime("%Y/%m/%d %H:%M:%S").strptime("%Y/%m/%d %H:%M:%S")
    '''

    '''
    #TEST DATA FOR CREATING JOB
    owner_id = '64291e7a06864f6b8cac1f28'
    title = 'Test_title'
    desc = 'Test_description'
    start_datetime = 'Test_start'
    end_datetime = 'Test_end'
    rate = '45'
    test_duration = '5'
    payout = '150'
    '''

    new_job = { "OwnerID" : ObjectId(owner_id),
                "Title": request.json.get('Title'), 
               "Desc" : request.json.get('Description'),
               "Created": now.strftime("%Y/%m/%d %H:%M:%S").strptime("%Y/%m/%d %H:%M:%S"),
               "Start_datetime" : request.json.get('Start_datetime'),
               "End_datetime" : request.json.get('End_datetime'),
               "Hourly_rate" : request.json.get('Hourly_rate'),
               "Duration" : find_hours(start_datetime, end_datetime), #strings in seconds if correct,
               "Payout" : format(numHours * rate, '.2f'),

               }

    try:
        job_col.insert_one( new_job )
        
    # Status (Open - No Pet Sitter hired, Matched - Pet Sitter hired, Closed - Job Closed, Completed - Session linked to this job is completed)
    # Start_datetime
    # End_datetime
    # Hourly_rate
    # Payout (Amount to be paid to Pet Sitter) (Hourly rate * End_datetime - Start_datetime)



    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while creating the job. " + str(e)
            }
        ), 500
    
    return jsonify(
        {
            "code": 201,
            "message": "New job successfully created."
        }
    ), 201

#Function 4: Update job details
@app.route("/updatejob/<string:JobID>", methods=['PUT'])
def update_job(job_id):

    #Get new data
    data = request.get_json() #get Info JSON 
    newStatus = data["Status"]
    ownerID = data['OwnerID']
    sitterID = data['sitterID']
    hourly_rate = data['Hourly_rate']
    desc = data['Description']
    title = data['Title']

    #Change job's status with the id=jobID from matched to open
    queryJob = {"_id":ObjectId(str(job_id))}
    openStatus = {"$set":{"Status":newStatus}}

    try:
        job_col.update_one(queryJob, openStatus)
        return jsonify(
            {
                "code": 200,
                "data": {
                    "JobID": job_id
                },
                "message": "Job status updated to Open. " + str(e)
            }
        ), 200

        # if not job:
        #     return jsonify(
        #         {
        #             "code": 404,
        #             "data": {
        #                 "JobID": job_id
        #             },
        #             "message": "Job not found."
        #         }
        #     ), 404

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
                "message": "An error occurred while updating the job. " + str(e)
            }
        ), 500

def find_hours(startTime, endTime):
    numSec = endTime - startTime
    return numSec/3600


if __name__ == "__main__":
    app.run(port=5005, debug=True)
