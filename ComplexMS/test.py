from flask import Flask, request, jsonify
# from flask_cors import CORS

import os, sys

# sys.path.append('../SimpleMS')
# import amqp_setup

import requests
from invokes import invoke_http
# import pika

app = Flask(__name__)
# CORS(app)

owner_URL = "http://localhost:5000/owner"
payment_URL = "http://localhost:5006"

# monitorBindingKey='*.payment'

data = jsonify({
    "Charge":500
})

print(data)

with app.app_context():
    status = invoke_http(payment_URL+"/create-payment",method=["POST"],json=data)
    code = status["code"]