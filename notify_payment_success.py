#Consume from AMQP and send to AMQP 

from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys

# sys.path.append('../SimpleMS')
import amqp_setup

import requests
from invokes import invoke_http
import pika

app = Flask(__name__)
CORS(app)

owner_URL = "http://owner:5000/owner"
payment_URL = "http://payment:5006"
session_URL = "http://session:5004/session"

#Actions after receiving the AMQP to hold payment on Owner's Account by accept_app.py

@app.route("/process-payment-success/<string:price_id>",methods=["GET"])
def process_payment_success(price_id):
    #1. Check whether payment is successful - invoke payment microservice
    payment_status = invoke_http(payment_URL+"/check_payment", method="GET")
    code = payment_status['code']
    if code not in range(200,300):
        return jsonify({
            "code": 400,
            "message": "Owner failed to make payment."
        }),400
    
    print(price_id)
    print(type(price_id))
    
    #2. Retrieve session object using price_id
    get_session = invoke_http(session_URL+"/get-session-by-price/"+price_id,method="GET")
    code = get_session['code']
    if code not in range(200,300):
        return jsonify({
            "code": 404,
            "message": "No session with price id " + price_id + " available."        
            }),404
    
    #Returns a session object
    owner_id = get_session["data"]

    #3. Retrieve ownerEmail using Ownerid in session object
    get_owner = invoke_http(owner_URL+"/"+owner_id, method="GET")
    code = get_owner['code']
    if code not in range(200,300):
        return jsonify({
            "code": 404,
            "message": "No owner with owner id " + owner_id + " found."        
            }),404

    ownerEmail = get_owner["data"][0]["Email"]
    # print(ownerEmail)
    #4. Send ownerEmail via AMQP to broker

    amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="pmt.hold.success.notification", body=ownerEmail, properties=pika.BasicProperties(delivery_mode = 2))

    return jsonify({
        "code":200,
        "message":"Payment has been successful. Sending email to notify owner of successful transaction."
    })


    
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) +
          " for placing an order...")
    app.run(host="0.0.0.0", port=5555, debug=True)



    
    

       

   






