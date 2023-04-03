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

get_sitter_payment_info_URL = "http://localhost:5001/payment-info/"
deduct_penalty_URL = "http://localhost:5006/charge-penalty/"
deduct_score_URL = "http://localhost:5001/sitter/rating/"
get_sitter_URL = "http://localhost:5001/sitter/"

# binding key
monitorBindingKey='#.penalty'

#Actions on the message - send to the GMAIl API
def callback(channel, method, properties, body): 
    print("\nReceived notification by " + __file__)
    processPenalty(json.loads(body), method.routing_key)
    print() # print a new line feed

def listenToAMQP():
    amqp_setup.check_setup() 
    queue_name = 'penalty'
    amqp_setup.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    amqp_setup.channel.start_consuming() 

def processPenalty(message,routing_key):
    # 1. Check the routing key of the message
    if routing_key == "sitter.penalty":
        sitter_id = message.sitterId
        job_id = message.jobId

    # 2. Get pet sitter's stripe id
    print('\n-----Get stripe id (sitter microservice)-----')
    get_payment_info_result = invoke_http(get_sitter_payment_info_URL + sitter_id, method='GET')
    print('get_payment_info_result: ',get_payment_info_result)

    # 3. Deduct payment
    # Invoke payment microservice
    print('\n-----Charge penalty fee (payment microservice)-----')
    # Penalty is $20 (before GST)
    penalty_amount = jsonify({'data':{'Charge' : 20}})
    deduct_penalty_result = invoke_http(deduct_penalty_URL + sitter_id, method='POST', json=get_payment_info_result)
    print('deduct_penalty_result: ',deduct_penalty_result)

    # 4. Lower sitter rating score by 50 points
    # Invoke sitter microservice
    print('\n-----Deduct sitter score (sitter microservice)-----')
    deduct_score_result = invoke_http(deduct_score_URL + sitter_id, method='PUT')
    print('deduct_score_result: ',deduct_score_result)

    # 5. Send message to sitter that penalty has been charged and rating has been lowered due to last-minute pulling out
    print('\n-----Publish message to AMQP with routing_key=penalty.notification (AMQP)-----')
    sitter_info = invoke_http(get_sitter_URL+sitter_id, method='GET')
    message = json.dumps({'data':{'sitterName': sitter_info['Name'],
                                  'sitterEmail': sitter_info['Email'], 
                                  'sitterUserScore': sitter_info['User_score'],
                                  'jobID': job_id}})

    amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="penalty.notification", 
        body=message, properties=pika.BasicProperties(delivery_mode = 2))


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
