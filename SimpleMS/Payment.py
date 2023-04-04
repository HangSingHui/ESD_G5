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
    total = charge*1.18  # GST
    return total

@app.route('/charge', methods=['POST'])
def change_price():
    details = request.get_json()
    product_id = details["product_id"]
    charge_before_gst = details["charge"]
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

    create_price = stripe.Price.create(
        unit_amount=charge,
        currency="sgd",
        product=product_id
    )

    price_id = create_price["id"]

    return price_id

# @app.route('/create_payment_intent', methods=['POST'])
# def create_payment():
#     # try:
#     #     data = json.loads(request.data)
#     #     print(data)
#     #     # Create a PaymentIntent with the order amount and currency
#     #     intent = stripe.PaymentIntent.create(
#     #         amount=calculate_order_amount(data['Charge']),
#     #         currency='sgd', 
#     #         payment_method_types=['card'],
#     #         # capture_method='manual',
#     #         automatic_payment_methods={
#     #             'enabled': True,
#     #         },
#     #     )
#     #     return jsonify({
#     #         'clientSecret': intent['client_secret']
#     #     })
#     # except Exception as e:
#     #     return jsonify(error=str(e)), 403
#     data = request.get_json()
#     charge_dollars = int(data["Charge"])
#     charge_cents = charge_dollars * 100
#     print(charge_cents)
#     #data contains only the amount to pay with the key name "Charge"
#     try:
#         payment_intent = stripe.PaymentIntent.create(
#             amount=charge_cents,
#             currency="sgd",
#             payment_method_types=["card"],
#             capture_method="manual",
#         )
#         response_data = {"payment_intent_id": payment_intent.id}
#         return jsonify(response_data)

#     except Exception as e:
#         return jsonify(error=str(e)), 403


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



@app.route('/send_payout', methods=['POST'])
def send_payout(card_info):
    try:
        payout = stripe.Payout.create(
            amount=1000,
            currency='sgd',
            method='instant',
            destination=card_info,
        )
        return jsonify({
                'clientSecret': payout['client_secret']
            })
    except Exception as e:
        return jsonify(error=str(e)), 403

# Prices in Stripe model the pricing scheme of your business.
# Create Prices in the Dashboard or with the API before accepting payments
# and store the IDs in your database.
PRICES = {"penalty": "price_1Msn1gFrjIdoqzyMMYL3kADE"}

@app.route("/charge-penalty/<string:Stripe_Id>", methods=['POST'])
def charge_penalty():
    customer_id = request.json.get('data')
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
    invoice = stripe.Invoice.create(
        customer=customer_id,
        collection_method='charge_automatically',
        days_until_due=1,
    )

    # Create an Invoice Item with the Price and Customer you want to charge
    stripe.InvoiceItem.create(
        customer=customer_id,
        price=PRICES["penalty"],
        invoice=invoice.id
    )

    try:
        # Send the Invoice
        stripe.Invoice.send_invoice(invoice.id)

    except:
        return jsonify(
        {
            "code":500, #internal error
            "message": "Internal error. Penalty cannot be charged to sitter's account."
        }
     ),500   

if __name__ == "__main__":
    app.run(port=5006, debug=True)
