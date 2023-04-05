from datetime import datetime

from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ
import json
import stripe

# testing API key
# stripe.api_key = 'pk_test_51Ms4GgFrjIdoqzyMIKQv8tYAqcPtO2cm09hNoEoxxnNZC2MlDmmbMYGpmFOHOMXZdJS3u8FI3j8mOjxLdvMHCFeg00I2EsXps1'

stripe.api_key="sk_test_51Ms4GgFrjIdoqzyMioZGnC28QwZsUW48fFwvURhXwbCiJGlw2F85IDkADg02Cq5GBHna0di1jJ5Pjho1A3dw59iC00uxo9ykaY"

app = Flask(__name__)
CORS(app)

def calculate_order_amount(charge):
    # Replace this constant with a calculation of the order's amount
    # Calculate the order total on the server to prevent
    # people from directly manipulating the amount on the client
    total = charge* 1.18 *100  # GST
    return total

@app.route('/payment/charge', methods=['POST'])
def change_price():
    # details = request.get_json()
    product_id = "prod_NdMqTOurWTf43d"
    charge_before_gst = request.get_json() #this is just a number with type string
    print(charge_before_gst)
    charge_before_gst = float(charge_before_gst)
    charge_after_gst = calculate_order_amount(charge_before_gst)
    charge = int(charge_after_gst)
    #JSON object
    # {
    #     "charge": 5000,
    #     "price_id": "price_1Mt7m5FrjIdoqzyMXm2tkOpr"
    # }
    # price = stripe.Price.modify(
    # price_id,
    # unit_amount=5000
    # )

    try:
        create_price = stripe.Price.create(
        unit_amount=charge,
        currency="sgd",
        product=product_id
    )
        
    except Exception as e:
        return jsonify(error=str(e)), 403

    price_id = create_price["id"]

    return jsonify({
        "code":200,
        "price_id":price_id
    })


@app.route('/charge_penalty', methods=['POST'])
def penalty_charge():
   
#    {
#    "card_id":"card_1Msny8FrjIdoqzyMXqxi0Hyu",
#    "customer":"cus_Ne69Q9W8sdVAww"
#      } 
   details = request.get_json()
   print(details)
   token = details['data'][0]["CardInfo"]
   customer = details['data'][0]["Stripe_Id"]
   print(token)
   print(customer)
   charge_details = stripe.Charge.create(amount=2000,currency="sgd",source=token,customer=customer)
   print(charge_details)

   return jsonify({
            "code":200,
            "data": charge_details
        })
   #json object
    #    {
    #        "card_id":"card_1Msny8FrjIdoqzyMXqxi0Hyu"
    #    }


@app.route('/check_payment')
def check_if_paid():
    #Get latest payment intent
    latest = stripe.PaymentIntent.list(limit=1)
    payment_status = latest["data"][0]["status"]
    # latest_priceID = latest["data"][0]["id"]
    if payment_status == "succeeded":
         return jsonify({
            "code":200,
            "message": "Successfully received payment from owner."
         })
    
    #Just invoke, no need AMQP

    
    return jsonify({
        "code":400,
        "message": "Owner failed to make payment."
        
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5006, debug=True)
