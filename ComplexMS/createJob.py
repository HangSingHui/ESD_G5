# the complex microservice create a job 
# create a job CMS will receive a HTTP request from the UI and send it to job SMS 
# job SMS received the HTTP requests and create a new record in the job database 

from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys

import requests
from invokes import invoke_http

from SimpleMS import amqp_setup
from datetime import datetime, timedelta

from SimpleMS import amqp_setup_notification
import pika
import json

app = Flask(__name__)
CORS(app)

# thr URLs are just the SMS that the CMS will be sending requests to? 
job_URL = "http://localhost:5100/job"
pet_URL = "http://localhost:5007/pet"

@app.route("/createjob", methods=['POST'])
def create_job():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            new_job = request.get_json() #entire job info
            print("\nReceived a job creation request in JSON:", new_job)

            # Create job by invoking func processJobCreation
            # func results either success or failure response 
            result = processJobCreation(new_job)
            code = result["code"]

            if code in range(200, 300):     
                # if the job creation is successful, send the message to the fanout exchange 
                published_result = processPublishJob(new_job) # new_job contains entire job info 
                # what is published_result? 

            return jsonify(result), result["code"]
        
        #if is 201, then access rate and species -pasas into amqp
        # filter the hourly rate into categories 
        # 3 hoursly rates

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            return jsonify({
                "code": 500,
                "message": "createJob.py internal error: " + ex_str
            }), 500
    
    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400


def processJobCreation(new_job):
    # called by create_job function to create job
    # invoke job microservice which will create job in the DB 

    data = request.get_json()
    print('\n-----Invoking job microservice-----')
    owner_id = request.json.get("OwnerID") #ASSUME THIS IS STRING
    job_result = invoke_http(job_URL+"/"+owner_id, method='POST', json=data)
    print('job_result:', job_result)

    # Check the job result; if a failure, return error status 
    code = job_result["code"]
    if code not in range(200, 300):     
        # Return error
        return {
                "code": 500,
                "data": {"job_result": job_result},
                "message": "Job creation failure sent for error handling."
            }
    # if successful job creation, return code 201
    return {
        "code": 201,
        "data": { "job_result": job_result}, 
    }


def processPublishJob(new_job):
    '''publish messages to the queues that the pet sitters are subscribed to'''

    # if this function is reached, it is assumed that the job has been successfully created
    # there is no need to check success of status
    # extract the pet type and publish to the queues 

    # job_id = new_job['_id']   
    # owner_id = new_job['OwnerID']
    pet_species = find_by_petID(new_job)
    # print(pet_species)   
    hourly_rate_result = new_job['Hourly_rate']

    # json. dumps() method - convert a python object into an equivalent JSON object
    message = json.dumps( {
        'job_id': new_job['_id'], 
        'owner_id': new_job['OwnerID'], 
        'pet_species': pet_species, 
        'hourly_rate': new_job['Hourly_rate']
    })

    # filter by pet 
    # if dog -> routing key = dog.*
    # if cat -> routing key = cat.*

    ########### Send to different queues based on pet species type ###########

    if pet_species == 'dog': 
        # send to dog queue 
        print('\n\n-----Publishing the (dog) message with routing_key=dog.*-----')

        # invoke_http(error_URL, method="POST", json=order_result)
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="dog.*", 
            body=message, properties=pika.BasicProperties(delivery_mode = 2)) 
        # make message persistent within the matching queues until it is received by some receiver 
        # (the matching queues have to exist and be durable and bound to the exchange)

    if pet_species == 'cat': 
        # send to cat queue 
        print('\n\n-----Publishing the (dog) message with routing_key=cat.*-----')
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="cat.*", 
            body=message, properties=pika.BasicProperties(delivery_mode = 2)) 
    
    
def find_by_petID(newjob): 
    print('\n-----Invoking pet microservice-----')
    # owner_id = request.json.get("OwnerID") #ASSUME THIS IS STRING
    pet_id = newjob['petID'] 
    pet_result = invoke_http(pet_URL+"/"+pet_id, method='GET')
    print('pet_result:', pet_result) 
    return pet_result # pet_result - json pet species 



# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) +
          " for placing an job...")
    app.run(host="0.0.0.0", port=5400, debug=True)
    # Notes for the parameters:
    # - debug=True will reload the program automatically if a change is detected;
    #   -- it in fact starts two instances of the same flask program,
    #       and uses one of the instances to monitor the program changes;
    # - host="0.0.0.0" allows the flask program to accept requests sent from any IP/host (in addition to localhost),
    #   -- i.e., it gives permissions to hosts with any IP to access the flask program,
    #   -- as long as the hosts can already reach the machine running the flask program along the network;
    #   -- it doesn't mean to use http://0.0.0.0 to access the flask program.
