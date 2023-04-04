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
# app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
# # "mysql+mysqlconnector://root:root@localhost:3306/pet
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db = SQLAlchemy(app)
# CORS(app)


def calculate_order_amount(charge):
    # Replace this constant with a calculation of the order's amount
    # Calculate the order total on the server to prevent
    # people from directly manipulating the amount on the client
    total = charge* 1.18  # GST
    return total

@app.route('/charge', methods=['POST'])
def change_price():
    # details = request.get_json()
    product_id = "prod_NdMqTOurWTf43d"
    charge_before_gst = request.get_json() #this is from job
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
   token = details["card_id"]
   customer = details["customer"]
   charge_details = stripe.Charge.create(amount=2000,currency="sgd",source=token,customer=customer)

   return charge_details
   #json object
    #    {
    #        "card_id":"card_1Msny8FrjIdoqzyMXqxi0Hyu"
    #    }


@app.route('/check_payment')
def check_if_paid():
    #Get latest payment intent
    product_id = "prod_NdMqTOurWTf43d"
    payment_id = retrieve_latest(product_id)
    payment = stripe.PaymentIntent.retrieve(payment_id)
    while payment.status != 'succeeded':
         payment = stripe.PaymentIntent.retrieve(payment_id)
    
    return jsonify({
        "code":200,
        "message": "Successfully received payment from owner."
    })


def retrieve_latest(product_id):
    payment_intents = stripe.PaymentIntent.list(
        product=product_id,
        limit=1,
        expand=["data.charges"],
        sort=[{"created": "desc"}]
    )

    latest_payment_ids = [payment_intent.charges.data[0].payment for payment_intent in payment_intents.data]

    return latest_payment_ids[0] #latest payment is first



# @app.route('/send_payout', methods=['POST'])
# def send_payout(card_info):
#     try:
#         payout = stripe.Payout.create(
#             amount=1000,
#             currency='sgd',
#             method='instant',
#             destination=card_info,
#         )
#         return jsonify({
#                 'clientSecret': payout['client_secret']
#             })
#     except Exception as e:
#         return jsonify(error=str(e)), 403

# Prices in Stripe model the pricing scheme of your business.
# Create Prices in the Dashboard or with the API before accepting payments
# and store the IDs in your database.
# PRICES = {"penalty": "price_1Msn1gFrjIdoqzyMMYL3kADE"}

# @app.route("/charge-penalty/<string:Stripe_Id>", methods=['POST'])
# def charge_penalty():
#     customer_id = request.json.get('data')
    # # Look up a customer in your database
    # customers = [c for c in CUSTOMERS if c["email"] == email]
    # if customers:
    #     customer_id=customers[0]["Stripe_Id"]
    # else:
    #     # Create a new Customer
    #     customer = stripe.Customer.create(
    #         email=email, # Use your email address for testing purposes
    #         description="Customer to invoice",
    #     )
    #     # Store the customer ID in your database for future purchases
    #     CUSTOMERS.append({"Stripe_Id": customer.id, "email": email})
    #     # Read the Customer ID from your database
    #     customer_id = customer.id

    # Create an Invoice
    # invoice = stripe.Invoice.create(
    #     customer=customer_id,
    #     collection_method='charge_automatically',
    #     days_until_due=1,
    # )

    # # Create an Invoice Item with the Price and Customer you want to charge
    # stripe.InvoiceItem.create(
    #     customer=customer_id,
    #     price=PRICES["penalty"],
    #     invoice=invoice.id
    # )

    # try:
    #     # Send the Invoice
    #     stripe.Invoice.send_invoice(invoice.id)

    # except:
    #     return jsonify(
    #     {
    #         "code":500, #internal error
    #         "message": "Internal error. Penalty cannot be charged to sitter's account."
    #     }
    #  ),500   

if __name__ == "__main__":
    app.run(port=5006, debug=True)
