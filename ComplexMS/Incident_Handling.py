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


notification_URL = "http://localhost:5002/notification/"
penalty_URL = "http://localhost:5300/Penalty_Handling/"
session_time_URL = "http://localhost:5004/session-time/"
close_session_URL = "http://localhost:5004/close-session/"
job_waitlist_URL = "http://localhost:5005/job/wait_list/"
open_job_URL = "http://localhost:5005/job/"
get_owner_by_id_URL = "http://localhost:5000/owner/"
get_sitter_details_URL = "http://localhost:5001/sitter/"
get_session_by_id_URL = "http://localhost:5004/session/"


@app.route("/incident_handling/<string:sessionId>", methods=['PUT'])
def incident_handling(sessionId):
    # Simple check of input format and data of the request are JSON
    session = invoke_http(get_session_by_id_URL + sessionId)
    if session:
        try:
            print("\nSession in JSON:", session)
            # 1. Send incident info
            result = processIncident(session)
            print('\n------------------------')
            print('\nresult: ', result)
            return jsonify(result), result["code"]

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            return jsonify({
                "code": 500,
                "message": "incident_handling.py internal error: " + ex_str
            }), 500

    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400


def processIncident(session):
    sessionId = session['_id']
    jobId = session['JobID']
    sitterId = session['SitterID']
    ownerId = session['OwnerID']

    # 2. Update session closing time and change session status to closed
    # Invoke session microservice
    print('\n-----Close session (session microservice)-----')
    closing_session_result = invoke_http(close_session_URL + sessionId, method='PUT', json=session)
    print('closing_session_result: ',closing_session_result)

    # 3. Change job status to 'Open'
    print('\n-----Update job status from "Matched" to "Open" (job microservice)-----')
    newStatus = jsonify({'data': {
        'Status': 'Open'
    }})
    open_job_result = invoke_http(open_job_URL + jobId, method='PUT', json=newStatus)
    print('open_job_result: ',open_job_result)


    # 4. check if job was cancelled after 1 day
    # if yes, invoke penalty handling (complex MS)
    if closing_session_result['data']['sessionDuration'] > 24 : 
        # 5. Send pet sitter details to AMQP for penalty handling
        print('\n\n-----Publishing pet sitter details to AMQP with routing_key=sitter.penalty-----')

        message = json.loads({'sitterId': sitterId, 
                              'jobId': jobId})

        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="sitter.penalty", 
        body=message, properties=pika.BasicProperties(delivery_mode = 2)) 

    else:
    # if no, ignore
        pass


    # 6. Retrieve recommended petsitters as replacement (waitlist)
    # Invoke job microservice
    print('\n-----Retrieve waitlist from job microservice-----')
    sitter_replacements_result = invoke_http(job_waitlist_URL + jobId, method='GET')
    print('Sitter Replacements Suggestion: ',sitter_replacements_result)


    # Get owner's email and name
    # Invoke owner microservice
    print('\n-----Retrieve name and email from owner microservice-----')
    owner_name_result = invoke_http(get_owner_by_id_URL + ownerId, method='GET')[0]['Name']
    owner_email_result = invoke_http(get_owner_by_id_URL + ownerId, method='GET')[0]['Email']
    print('Owner name:',owner_name_result,'\nOwner email:',owner_email_result)

    sitters = []
    for sitter in sitter_replacements_result:
        details = invoke_http(get_sitter_details_URL + sitter, method='GET')
        sitters.append(details)

    # 7. Send list of recommended pet sitter replacements
    print('\n\n-----Publishing the list of recommended pet sitter replacements with routing_key=replacement.notification-----')

    message = json.dumps({'jobID': jobId, 
                          'replacements':sitters, 
                          'ownerID': ownerId, 
                          'ownerName': owner_name_result,
                          'ownerEmail': owner_email_result})

    amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="replacement.notification", 
        body=message, properties=pika.BasicProperties(delivery_mode = 2)) 
    # make message persistent within the matching queues until it is received by some receiver 
    # (the matching queues have to exist and be durable and bound to the exchange)


    # - reply from the invocation is not used;
    # continue even if this invocation fails        
    print("\nSitter replacement status ({:d}) published to the RabbitMQ Exchange:", sitter_replacements_result)


    # 8. Return confirmation of cancellation
    return {
        "code": 201,
        "data": {
            "cancellation": closing_session_result,
            "cancelation_status": "confirmed"
        }
    },201



# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) + " for handling an incident...")
    app.run(host="0.0.0.0", port=5200, debug=True)
    # Notes for the parameters: 
    # - debug=True will reload the program automatically if a change is detected;
    #   -- it in fact starts two instances of the same flask program, and uses one of the instances to monitor the program changes;
    # - host="0.0.0.0" allows the flask program to accept requests sent from any IP/host (in addition to localhost),
    #   -- i.e., it gives permissions to hosts with any IP to access the flask program,
    #   -- as long as the hosts can already reach the machine running the flask program along the network;
    #   -- it doesn't mean to use http://0.0.0.0 to access the flask program.
