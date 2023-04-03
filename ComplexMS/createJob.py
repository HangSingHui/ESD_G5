# the complex microservice create a job 
# create a job CMS will receive a HTTP request from the UI and send it to job SMS 
# job SMS received the HTTP requests and create a new record in the job database 

from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys

import requests
from invokes import invoke_http

app = Flask(__name__)
CORS(app)

# thr URLs are just the SMS that the CMS will be sending requests to? 
job_URL = "http://localhost:5100/job"

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


# def processPublishJob(new_job):
#     '''publish messages to the queues that the pet sitters are subscribed to'''

#     message = json.dumps(new_job)

#     if code in range(200, 300):
#         # if job creation is successful 

#         # Inform the error microservice
#         #print('\n\n-----Invoking error microservice as job fails-----')
#         print('\n\n-----Publishing the (job error) message with routing_key=job.error-----')

#         # invoke_http(error_URL, method="POST", json=job_result)
#         amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="job.error", 
#             body=message, properties=pika.BasicProperties(delivery_mode = 2)) 
#         # make message persistent within the matching queues until it is received by some receiver 
#         # (the matching queues have to exist and be durable and bound to the exchange)

#         # - reply from the invocation is not used;
#         # continue even if this invocation fails        
#         print("\njob status ({:d}) published to the RabbitMQ Exchange:".format(
#             code), job_result)

#         # 7. Return error
#         return {
#             "code": 500,
#             "data": {"job_result": job_result},
#             "message": "job creation failure sent for error handling."
#         }

 
    
#     print("\njob published to RabbitMQ Exchange.\n")

#     print('\n\n-----Invoking shipping_record microservice-----')    
    


# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) +
          " for placing an job...")
    app.run(host="0.0.0.0", port=5100, debug=True)
    # Notes for the parameters:
    # - debug=True will reload the program automatically if a change is detected;
    #   -- it in fact starts two instances of the same flask program,
    #       and uses one of the instances to monitor the program changes;
    # - host="0.0.0.0" allows the flask program to accept requests sent from any IP/host (in addition to localhost),
    #   -- i.e., it gives permissions to hosts with any IP to access the flask program,
    #   -- as long as the hosts can already reach the machine running the flask program along the network;
    #   -- it doesn't mean to use http://0.0.0.0 to access the flask program.
