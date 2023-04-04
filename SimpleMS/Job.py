from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ
from datetime import datetime
from bson.json_util import dumps
from bson.objectid import ObjectId
import json
import pymongo
import time


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
@app.route("/createjob/<string:OwnerID>", methods=['GET', 'POST'])
# URL PATH 
def create_job(OwnerID):
    
    data = request.data.decode('utf-8')
    replace = data.replace("'", '"')
    data_json = json.loads(replace)
    
    
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
    
    # Start_datetime = data_json['Start_datetime']
    # End_datetime = data_json['End_datetime']
    # duration_seconds = int(End_datetime) - int(Start_datetime)
 
    # duration_hours = duration_seconds // 3600
    # payout = float(data_json['Hourly_rate']) * duration_hours
    # print(payout)
    
    new_job = { "OwnerID" : data_json['OwnerID'],
                "Title": data_json['Title'], 
            "Desc" : data_json['Description'],
            "Created": now.strftime("%Y/%m/%d %H:%M:%S").strptime("%Y/%m/%d %H:%M:%S"),
            "Start_datetime" : data_json['Start_datetime'],
            "End_datetime" : data_json['End_datetime'],
            "Hourly_rate" : data_json['Hourly_rate'],
            "Duration" : find_hours( data_json['Start_datetime'], data_json['End_datetime']), #strings in seconds if correct,
            "Payout" : format( data_json * rate, '.2f'),
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

#Function 4: Update job status
@app.route("/job/update_job/<string:job_id>/<string:status>", methods=['PUT'])
def update_job(job_id,status):

    info = request.get_json()
    sitter_id = info["sitter_id"]
    print(sitter_id)
    #Change job's status with the id=jobID from matched to open
    queryJob = {"_id":ObjectId(job_id)}
    changeStatus = {"$set":{"status":status,"SitterID":sitter_id}}

    try:
        job_col.update_one(queryJob, changeStatus)
        return jsonify(
            {
                "code": 200,
                "data": {
                    "JobID": job_id
                },
                "message": "Job status updated to " + status +" and accepted sitter is added."
            }
        ), 200

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
    
@app.route("/job/update_job/wait_list/<string:job_id>", methods=['PUT'])
def add_wait_list(job_id):
    wait_list = request.json.get("wait_list")
    print("here again")
    print(wait_list)
    queryJob = {"_id":ObjectId(job_id)}
    update = {"$set":{"Waitlist":wait_list}}
    
    try:
        job_col.update_one(queryJob, update)
        return jsonify(
            {
                "code": 200,
                "data": {
                    "JobID": job_id,
                    "Wait_List": wait_list
                },
                "message": "Waitlist updated for job with jobID: "+ job_id 
            }
        ), 200

    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "JobID": job_id
                },
                "message": "An error occurred while updating waitlist. "
            }
        ), 500
    


def find_hours(startTime, endTime):
    numSec = endTime - startTime
    return numSec/3600


if __name__ == "__main__":
    app.run(port=5005, debug=True)
