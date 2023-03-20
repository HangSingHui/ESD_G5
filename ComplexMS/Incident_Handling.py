from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys

import requests
from invokes import invoke_http

from SimpleMS import amqp_setup_notification
import pika
import json

app = Flask(__name__)
CORS(app)


notification_URL = "http://localhost:5002/notification"
penalty_URL = "http://localhost:5200/Penalty_Handling"
session_time_URL = "http://localhost:5003/session-time"
close_session_URL = "http://localhost:5003/close-session"

@app.route("/incident_handling", methods=['POST'])
def incident_handling():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            session = request.get_json()
            print("\nSession in JSON:", session)

            # do the actual work
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
    sessionId = session['id']
    # 2. Update session closing time
    # Invoke session microservice
    print('\n-----Update session closing time (session microservice)-----')
    closing_session_result = invoke_http(close_session_URL + sessionId, method='PUT', json=session)
    print('closing_session_result:',closing_session_result)

    # 3. Retrieve the session time
    # Invoke session microservice
    print('\n-----Retrieving session creation time (session microservice)-----')
    session_time = invoke_http(session_time_URL + sessionId, method='GET', json=session)
    print('session_time:',session_time)


    # 7. Return confirmation of cancellation
    return {
        "code": 201,
        "data": {
            "cancellation": closing_session_result,
            "cancelation_status": "confirmed"
        }
    }



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
