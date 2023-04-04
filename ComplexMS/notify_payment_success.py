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

monitorBindingKey='#.payment'

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

def paymentNotif():
    amqp_setup.check_setup() 
    queue_name = "payment_success"
    amqp_setup.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    amqp_setup.channel.start_consuming() 

#Actions on the message - send to the Payment MS
def callback(channel, method, properties, body): 
    print("\nReceived notification by " + __file__)
    checkSuccess(json.loads(body),method.routing_key) 
    print() # print a new line feed

#Actions after receiving the AMQP to hold payment on Owner's Account by accept_app.py
@app.route("/checkSuccess", method=["POST"])
def checkSuccess():

    data=request.get_json()

    pmt_details = jsonify({
            "Charge": data["Payout"],
        })

    charge_owner = holdPayment(pmt_details)
    code = charge_owner["code"]

    if code not in range(200,300):
        return jsonify({
            "code":code,
            "message": "Error in charging the owner " + jobDetails["OwnerID"] + " the payout for the accepted job application."
        })



def holdPayment(data):
    status = invoke_http(payment_URL+"/charge",method=["POST"],json=data)
    code = status["code"]
    if code not in range(200,300):
        #Error handling
        return jsonify({
            "code": code,
            "message": "Error in Stripe API. Unable to place a hold on owner's card."
        })
    #To invoke notification to send a notif to inform owner of the charge placed on his card




#     notifyOwner(data)

# def notifyOwner():
#     amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="pmt.hold.success.notification", body=data, properties=pika.BasicProperties(delivery_mode = 2))
    



    
    

       

   






