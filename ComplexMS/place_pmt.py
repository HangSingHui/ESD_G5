#Consume from AMQP and send to AMQP 

from flask import Flask, request, jsonify
from flask_cors import CORS

import amqp_setup

import os, sys

sys.path.insert(0, 'SimpleMS')

import requests
from invokes import invoke_http
import pika

app = Flask(__name__)
CORS(app)

owner_URL = "http://localhost:5000/owner"
payment_URL = "http://localhost:5006/payment"

monitorBindingKey='*.payment'

#Consume from AMQP first to get the payment details
#Data sent from accept_app.py
##########################################
# _id
# OwnerID 
# Created (date??)
# PetID 
# SitterID (When a Pet Sitter is hired)
# Title
# Description
# Status (Open - No Pet Sitter hired, Matched - Pet Sitter hired, Closed - Job Closed, Completed - Session linked to this job is completed)
# Start_datetime
# End_datetime
# Payout (Amount to be paid to Pet Sitter)
##########################################

def paymentNotif():
    amqp_setup.check_setup() 
    queue_name = "payment"
    amqp_setup.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    amqp_setup.channel.start_consuming() 

#Actions on the message - send to the Payment MS
def callback(channel, method, properties, body): 
    print("\nReceived notification by " + __file__)
    holdPayment(json.loads(body),method.routing_key)
    print() # print a new line feed

def holdPayment(jobDetails, routingkey):
    #get owner account number 
    getOwner = invoke_http(owner_URL+"/"+str(jobDetails["OwnerID"]),method=["GET"])
    code = getOwner["code"]
    if code not in range(200,300):
        #it is an error
        
   






