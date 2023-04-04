#Consume from AMQP and send to AMQP 

from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys

sys.path.append('../SimpleMS')
import amqp_setup

import requests
from invokes import invoke_http
import pika

app = Flask(__name__)
CORS(app)

owner_URL = "http://localhost:5000/owner"
payment_URL = "http://localhost:5006"
session_URL = "http://localhost:5004/session"
owner_URL = "http://localhost:5000/owner"

# monitorBindingKey='#.payment'

#Consume from AMQP first to get the payment details
#Data sent from accept_app.py
##########################################
# _id
# OwnerID 
# Created
# PetID 
# SitterID (When a Pet Sitter is hired)
# Title
# Description
# Status (Open - No Pet Sitter hired, Matched - Pet Sitter hired, Closed - Job Closed, Completed - Session linked to this job is completed)
# Start_datetime
# End_datetime
# Payout (Amount to be paid to Pet Sitter)
#Wait_list
##########################################

# def paymentNotif():
#     amqp_setup.check_setup() 
#     queue_name = "payment_success"
#     amqp_setup.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
#     amqp_setup.channel.start_consuming() 

# #Actions on the message - send to the Payment MS
# def callback(channel, method, properties, body): 
#     print("\nReceived notification by " + __file__)
#     checkSuccess(json.loads(body),method.routing_key) 
#     print() # print a new line feed

#Actions after receiving the AMQP to hold payment on Owner's Account by accept_app.py

@app.route("/process_payment_success/<string:price_id>",method="GET")
def process_payment_success(price_id):
    #1. Check whether payment is successful - invoke payment microservice
    payment_status = invoke_http(payment_URL+"/check_payment", method="GET")
    code = payment_status['code']
    if code not in range(200,300):
        return jsonify({
            "code": 400,
            "message": "Owner failed to make payment."
        }),400
    
    #2. Retrieve session object using price_id
    get_session = invoke_http(session_URL+"/<string:price_id>",method="GET")
    code = get_session['code']
    if code not in range(200,300):
        return jsonify({
            "code": 404,
            "message": "No session with price id " + price_id + " available."        
            }),404
    
    #Returns a session object
    owner_id = get_session["OwnerID"]

    #3. Retrieve ownerEmail using Ownerid in session object
    get_owner = invoke_http(owner_URL+"/"+owner_id, method="GET")
    code = get_owner['code']
    if code not in range(200,300):
        return jsonify({
            "code": 404,
            "message": "No owner with owner id " + owner_id + " found."        
            }),404

    ownerEmail = get_owner["data"][0]["Email"]
    #4. Send ownerEmail via AMQP to broker
    
    amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="pmt.hold.success.notification", body=ownerEmail, properties=pika.BasicProperties(delivery_mode = 2))


    
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) +
          " for placing an order...")
    app.run(host="0.0.0.0", port=5500, debug=True)



    
    

       

   






