from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys

sys.path.insert(0, 'SimpleMS')

import amqp_setup

import requests
from invokes import invoke_http
import pika

app = Flask(__name__)
# CORS(app)

owner_URL = "http://localhost:5000/owner"
sitter_URL = "http://localhost:5001/sitter"
notification_URL = "http://localhost:5002/notification"
session_URL = "http://localhost:5004/session"
job_URL = "http://localhost:5005/job"
payment_URL = "http://localhost:5006/payment"
application_URL = "http://localhost:5008/application"

@app.route("/accept_app", methods=['PUT'])
def acceptApp():
    # Simple check of input format and data of the request are JSON

    if request.is_json:
        try:
            info = request.get_json()
            print("\nOwner accepted a job app in JSON:", info)

            # do the actual work
            # 1. Send order info {cart items}
            result = processAcceptApp(info)
            return jsonify(result), result["code"]

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            return jsonify({
                "code": 500,
                "message": "_order.py internal error: " + ex_str
            }), 500

    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400

# #Info JSON format:
# {   
#     "sitterID":1234,
#     "jobID": 4567,
#     "ownerID":7890
#     "appID"1234,
#     "jobStatus":"Accepted"
# }

def processAcceptApp(info):

    #1. Change status of all application ID linked to the same jobID
    update_status = invoke_http(application_URL,method="PUT", json=info)
    code = update_status["code"]
    if code not in range(200,300):
        #Error
        return{
            "code": code,
            "message": update_status["message"]
        }


    #2.  Invoke Job to fetch job
    getJob = invoke_http(job_URL,method="GET", json=info["jobID"])
    code = update_status["code"]
    if code not in range(200,300):
    #Error
        return{
            "code": code,
            "message": getJob["message"]
     }   
    

    #3.  Invoke Session to update status
    createSession = invoke_http(session_URL,method="POST", json=info)
    code = createSession["code"]
    if code not in range(200,300):
    #Error
        return{
            "code": code,
            "message":  createSession["message"]
     }   

    #4.  Get sitter email
    getSitter = invoke_http(sitter_URL+"/"+str(info["sitterID"]), method="GET")
    code = getSitter["code"]
    if code not in range(200,300):
        return{
            "code": code,
            "message":  getSitter["message"]
        } 

    sitterEmail = getSitter["data"]["sitterEmail"]

    #5.  Invoke Notif to send confirmation acceptance to sitter
    
    amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="accept.sitter.notification", body=sitterEmail, properties=pika.BasicProperties(delivery_mode = 2))

    # #6. Invoke place_pmt complex to charge owner - don't know if we're still doing this???
    amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="hold.payment", body=getJob["data"] , properties=pika.BasicProperties(delivery_mode = 2))



    #7. Return status to UI
    return{
        "code":200,
        "message": "You have successfully accepted your desired sitter."
    }



# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) +
          " for placing an order...")
    app.run(host="0.0.0.0", port=5100, debug=True)
    # Notes for the parameters:
    # - debug=True will reload the program automatically if a change is detected;
    #   -- it in fact starts two instances of the same flask program,
    #       and uses one of the instances to monitor the program changes;
    # - host="0.0.0.0" allows the flask program to accept requests sent from any IP/host (in addition to localhost),
    #   -- i.e., it gives permissions to hosts with any IP to access the flask program,
    #   -- as long as the hosts can already reach the machine running the flask program along the network;
    #   -- it doesn't mean to use http://0.0.0.0 to access the flask program.
