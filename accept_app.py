from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from bson.json_util import dumps

import os, sys

# sys.path.append('../SimpleMS')
import amqp_setup 


import requests
from invokes import invoke_http
import pika

app = Flask(__name__)
CORS(app)

owner_URL = "http://owner:5000/owner"
sitter_URL = "http://sitter:5001/sitter"
session_URL = "http://session:5004/session"
job_URL = "http://job:5005/job"
payment_URL = "http://payment:5006/payment"
application_URL = "http://application:5008/application"
# success_notif_URL = "http://localhost:5500"

@app.route("/accept_app/<string:app_id>", methods=['PUT'])
def acceptApp(app_id):
    # Simple check of input format and data of the request are JSON

    print(app_id)
    print(type(app_id))

    if request.is_json:
        try:
            print("\nOwner accepted a job app with app id:" + app_id )

            # do the actual work
            # 1. Send order info {cart items}
            result = processAcceptApp(app_id)
            print(result)
            return result
            # return jsonify(result), result["code"]

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            return jsonify({
                "code": 500,
                "message": "accept_app.py internal error: " + ex_str
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

def processAcceptApp(app_id):

    #1. Change status of all application ID linked to the same jobID
    # app_id = info["app_id"]
    update_app_status = invoke_http(application_URL+"/accept/"+app_id,method="PUT")
    code = update_app_status["code"]

    if code not in range(200,300):
        #Error
        return{
            "code": code,
            "message": update_app_status["message"]
        }
    
    
    #Return is list of waitListed sitters
    # {
    #     "code":201,
    #     "message":"Application...",
    #     "wait_list":waitList,
    #     "job_id": 1234

    # }
    job_id = update_app_status["data"]["job_id"]  
    print(job_id)  
    data= update_app_status["data"]
    print(data) #
    #2. Update job to matched and accepted sitterid
    update_matched = invoke_http(job_URL+"/update_job/"+job_id+"/Matched", method='PUT',json=data)
    code = update_matched["code"]

    if code not in range(200,300):
    #Error
        return{
            "code": code,
            "message": update_matched["message"]
     } 

    #3. Update job waitlist 
    update_waitlist = invoke_http(job_URL+"/update_job/wait_list/"+job_id, method='PUT',json=data)
    code = update_waitlist["code"]
    if code not in range(200,300):
    #Error
        return{
            "code": code,
            "message": update_waitlist["message"]
     } 
    #3.  Invoke Job to fetch job
    getJob = invoke_http(job_URL+"/"+job_id,method="GET")
    code = getJob["code"]
    if code not in range(200,300):
    #Error
        return{
            "code": code,
            "message": getJob["message"]
        }   
    
    # print(getJob["data"])
    job = getJob["data"][0]
    sitter_id = job["SitterID"]
    job_id = job["_id"]["$oid"]
    print(job_id)

    
    #3.  Invoke Session to update status
    createSession = invoke_http(session_URL+"/create_session/"+job_id,method="POST", json=job)
    #info contains owner_id and sitter_id
    code = createSession["code"]
    if code not in range(200,300):
    #Error
        return{
            "code": code,
            "message":  createSession["message"]
     }   

    #4.  Get sitter email
    getSitter = invoke_http(sitter_URL+"/"+sitter_id, method="GET")
    code = getSitter["code"]
    if code not in range(200,300):
        return{
            "code": code,
            "message":  getSitter["message"]
        } 
    
    sitterEmail = getSitter["data"][0]["Email"]

    #5.  Invoke Notif to send confirmation acceptance to sitter
    amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="accept.sitter.notification", body=sitterEmail, properties=pika.BasicProperties(delivery_mode = 2))
    print("Done AMQP?")

    #Get price_id first
    if code not in range(200,300):
        
        return jsonify({
            "code": 500,
            "message":"Error on Stripe Server. Unable to create new price to charge owner."
        }),500

    # print(job["Payout"])
    payout = job["Payout"]["$numberDecimal"] #Just a string
    # print(payout)
    # payout = {"price_id":price_id}
    create_price = invoke_http(payment_URL+"/charge", method="POST",json=payout)
    code=create_price["code"]
    # print(create_price["data"])

    #7. Invoke payment to return the price_id to the UI
    price_id = create_price["price_id"]

    #Update session with price_id

    # print(type(job_id))
    update_price_id = invoke_http(session_URL+"/addPrice/"+job_id,method="PUT",json=price_id)
    code = update_price_id["code"]
    if code not in range(200,300):
        return jsonify({
            "code": 500,
            "message": "Failed to update price_id for job with job id: " + job_id
        })


    return {
            "code":200,
            "message": "You have successfully accepted your desired sitter. Awaiting for owner to make a payment.",
            "price_id":price_id
    }


# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) +
          " for accepting a job application...")
    app.run(host="0.0.0.0", port=5100, debug=True)
