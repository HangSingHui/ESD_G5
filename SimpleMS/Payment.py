from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from typing import List
from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ
import json
import stripe

# testing API key
stripe.api_key = 'sk_test_51Mo1LqL5uIojK8Z6pRnFG1BBFjvCTx6qqFWw9j87GVvcloPgkLZZA2dp4Fd2sAbMiPvY91KaqC0midYiICEvcHdDC00k4wIer53'


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
# "mysql+mysqlconnector://root:root@localhost:3306/pet
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)


def calculate_order_amount(charge):
    # Replace this constant with a calculation of the order's amount
    # Calculate the order total on the server to prevent
    # people from directly manipulating the amount on the client
    total = charge*1.17  # GST
    return total


@app.route('/create-payment-intent', methods=['POST'])
def create_payment():
    try:
        data = json.loads(request.data)
        # Create a PaymentIntent with the order amount and currency
        intent = stripe.PaymentIntent.create(
            amount=calculate_order_amount(data['charge']),
            currency='sgd', 
            payment_method_types=['card'],
            capture_method='manual',
            automatic_payment_methods={
                'enabled': True,
            },
        )
        return jsonify({
            'clientSecret': intent['client_secret']
        })
    except Exception as e:
        return jsonify(error=str(e)), 403


if __name__ == "__main__":
    app.run(port=5006, debug=True)
