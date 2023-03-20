from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys

import requests
from invokes import invoke_http

app = Flask(__name__)
CORS(app)

owner_URL = "http://localhost:5000/owner"
sitter_URL = "http://localhost:5001/sitter"
notification_URL = "http://localhost:5002/notification"
session_URL = "http://localhost:5004/session"
job_URL = "http://localhost:5005/job"
payment_URL = "http://localhost:5006/payment"
application_URL = "http://localhost:5008/application"



@app.route("/accept_app", methods=['PUT'])
def acceptApp():
    # Simple check of input format and data of the request are JSON

    ########################
    # sample info data format
    # {
    #     "sitterID":"Name",
    #     "appID":123,
    #     "ownerID": 456,
    #     "jobID":789,
    #     "jobStatus":"Accepted"
    # }
    ########################


    if request.is_json:
        try:
            info = request.get_json()
            print("\nOwner accepted a job app in JSON:", info)

            # do the actual work
            # 1. Send order info {cart items}
            result = processAcceptApp(info)
            return jsonify(result), result["code"]

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            return jsonify({
                "code": 500,
                "message": "_order.py internal error: " + ex_str
            }), 500

    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400


def processAcceptApp(info):

    #1. Invoke App to update status
    update_status = invoke_http(application_URL,method="PUT", json=info["appID"])
    code = update_status["code"]
    if code not in range(200,300):
        #Error
        return{
            "code": 500,
            "data": update_status["data"]
        }



    #2.  Invoke Job to update status

    #3.  Invoke Session to update status

    #4.  Invoke Sitter to update status

    #5.  Invoke Notif to update status

    #6.  AMQP Place payment

    #7. Return status to uI



    # 2. Send the order info {cart items}
    # Invoke the order microservice

    #Note: order is in the following format:
    # {
    #    "customer_id": "Apple TAN",
    #    "cart_item": [{
    #       "book_id": "9781434474234",
    #       "quantity": 1
    #    },
    #    {
    #       "book_id": "9781449474212",
    #       "quantity": 1
    #    }]
    # }

    new_order = invoke_http(order_URL, method="POST", json=order)


    # 4. Record new order
    # record the activity log anyway

    invoke_http(activity_log_URL, method="POST", json=new_order)


    # Check the order result; if a failure, send it to the error microservice.
    code = new_order["code"]
    if code not in range(200,300):
        invoke_http(error_URL, method="POST", json = new_order)
    
        return {
            "code": 500,
            "message": "Order creation failure sent for error handling."
        }

    # Inform the error microservice

    # 7. Return error

    # 5. Send new order to shipping
    # Invoke the shipping record microservice
    shipping_record = invoke_http(shipping_record_URL, method="POST", json = new_order["data"])
    code = shipping_record["code"]
    if code not in range(200,300):
        invoke_http(error_URL, method="POST", json = shipping_record)
        return {
            "code":400,
            "message": "Order should be in JSON."
        }
    

    # Check the shipping result;
    # if a failure, send it to the error microservice.

    # Inform the error microservice

    # 7. Return error

    # 7. Return created order, shipping record
    return {
        "code":201,
        "data":{
            "order_result": new_order,
            "shipping_result": shipping_record
        }
    }


# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) +
          " for placing an order...")
    app.run(host="0.0.0.0", port=5100, debug=True)
    # Notes for the parameters:
    # - debug=True will reload the program automatically if a change is detected;
    #   -- it in fact starts two instances of the same flask program,
    #       and uses one of the instances to monitor the program changes;
    # - host="0.0.0.0" allows the flask program to accept requests sent from any IP/host (in addition to localhost),
    #   -- i.e., it gives permissions to hosts with any IP to access the flask program,
    #   -- as long as the hosts can already reach the machine running the flask program along the network;
    #   -- it doesn't mean to use http://0.0.0.0 to access the flask program.
