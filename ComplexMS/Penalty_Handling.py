from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys

import requests
from invokes import invoke_http

from datetime import datetime, timedelta

import pika
import json

sys.path.append('../SimpleMS')
import amqp_setup

app = Flask(__name__)

get_sitter_payment_info_URL = "http://localhost:5001/payment-info/"
deduct_penalty_URL = "http://localhost:5006/charge_penalty"
deduct_score_URL = "http://localhost:5001/sitter/rating/"
get_sitter_URL = "http://localhost:5001/sitter/"

# binding key
monitorBindingKey='#.penalty'

# def callback(channel, method, properties, body): 
#     print("\nReceived notification by " + __file__)
#     processPenalty(json.loads(body), method.routing_key)
#     print() # print a new line feed

# def listenToAMQP():
#     amqp_setup.check_setup() 
#     queue_name = 'penalty'
#     amqp_setup.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
#     amqp_setup.channel.start_consuming() 

@app.route("/penalty_handling/<string:sitterId>/<string:jobId>", methods=['PUT'])
def penalty_handling(sitterId, jobId):
    # Simple check of input format and data of the request are JSON
    try:
        # 1. Send sitterId and jobId info
        result = processPenalty(sitterId, jobId)
        print('\n------------------------')
        print('result: ', result)
        # return jsonify(result), result['code']
        return result

    except Exception as e:
        # Unexpected error in code
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
        print(ex_str)

        return jsonify({
            "code": 500,
            "message": "penalty_handling.py internal error: " + ex_str
        }), 500

    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400

# def processPenalty(message,routing_key):
#     # 1. Check the routing key of the message
#     if routing_key == "sitter.penalty":
#         sitter_id = message.sitterId
#         job_id = message.jobId

def processPenalty(sitter_id, job_id):

    # 2. Lower sitter rating score by 50 points
    # Invoke sitter microservice
    print('\n-----Deduct sitter score (sitter microservice)-----')
    deduct_score_result = invoke_http(deduct_score_URL + sitter_id, method='PUT')
    print('deduct_score_result: ',deduct_score_result)

    # 3. Get pet sitter's details
    print("\n-----Get sitter's details (sitter microservice)-----")
    sitter_info = invoke_http(get_sitter_URL+sitter_id, method='GET')
    print('sitter_info: ',sitter_info)
    print(sitter_info['data'][0]['Name'])
    print(sitter_info['data'][0]['Email'])
    print(sitter_info['data'][0]['User_score'])

    # 4. Deduct payment
    # Invoke payment microservice
    print('\n-----Charge penalty fee (payment microservice)-----')
    deduct_penalty_result = invoke_http(deduct_penalty_URL, method='POST', json=sitter_info)
    print('deduct_penalty_result: ',deduct_penalty_result)

    # 5. Send message to sitter that penalty has been charged and rating has been lowered due to last-minute pulling out
    print('\n-----Publish message to AMQP with routing_key=penalty.notification (AMQP)-----')
    message = json.dumps({
                            'sitterName': sitter_info['data'][0]['Name'],
                            'sitterEmail': sitter_info['data'][0]['Email'], 
                            'sitterUserScore': sitter_info['data'][0]['User_score'],
                            'jobID': job_id
                            })
    print(message)
    amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="penalty.notification", 
        body=message, properties=pika.BasicProperties(delivery_mode = 2))
    
    return(jsonify
           ({
                "code":200,
                "message":'Penalty Handled!'
            })
        )


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
