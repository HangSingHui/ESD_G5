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

get_sitter_card_info_URL = "http://localhost/card-info/"
deduct_penalty_URL = "http://localhost/create-payment/"

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
    if routing_key == "invoke.penalty":
        sitter_id = message.sitterID

    # 2. Get pet sitter's card info
    print('\n-----Get card info (sitter microservice)-----')
    get_card_info_result = invoke_http(get_sitter_card_info_URL + sitter_id, method='GET')
    print('get_card_info_result: ',get_card_info_result)

    # 3. Deduct payment
    # Invoke payment microservice
    print('\n-----Create Payment Intent (payment microservice)-----')
    # Penalty is $20 (before GST)
    amount = jsonify({'data':{'Charge' : 20}})
    deduct_penalty = invoke_http(deduct_penalty_URL + sitter_id, method='POST', json=amount)
    print('deduct_penalty_result: ',deduct_penalty)

    # 4. Lower sitter rating score by 50 points
    # Invoke sitter microservice
    print('\n-----Deduct sitter score (sitter microservice)-----')
    


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
