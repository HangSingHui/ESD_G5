# the complex microservice create a job 
# create a job CMS will receive a HTTP request from the UI and send it to job SMS 
# job SMS received the HTTP requests and create a new record in the job database 

from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys

import requests
from invokes import invoke_http

app = Flask(__name__)
CORS(app)

# thr URLs are just the SMS that the CMS will be sending requests to? 
job_URL = "http://localhost:5100/job"

@app.route("/createjob", methods=['POST'])
def create_job():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            new_job = request.get_json()
            print("\nReceived a job creation request in JSON:", new_job)

            # do the actual work
            # 1. Send job info {}
            # if request's format is JSON and data is valid JSON, this function invokes processPlaceOrder() to do the actual work. Result returned by processPlaceOrder() is sent back to the user as a JSON response. 
            result = processJobCreation(new_job)
            return jsonify(result), result["code"]

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            return jsonify({
                "code": 500,
                "message": "createJob.py internal error: " + ex_str
            }), 500

    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400


def processJobCreation(new_job):
    # called by create_job function to create job
    # invoke job microservice which will create job in the DB 
    # result returned by job MS? 

    print('\n-----Invoking job microservice-----')
    job_result = invoke_http(job_URL, method='POST', json=order)
    print('order_result:', job_result)

    # Check the order result; if a failure, return error status 
    code = job_result["code"]
    if code not in range(200, 300):

    # 7. Return error
        return {
                "code": 500,
                "data": {"order_result": job_result},
                "message": "Job creation failure sent for error handling."
            }


def processPlaceJob(new_job):
    '''publish messages to the queues that the pet sitters are subscribed to'''
    # retrieve the pet sitter data? look at sitter preferences & region preference 
    # 2. Send the order info {cart items}
    # Invoke the order microservice
    print('\n-----Invoking order microservice-----')
    new_job_result = invoke_http(job_URL, method='POST', json=new_job)
    print('order_result:', new_job_result)
  

    # Check the order result; if a failure, send it to the error microservice.
    code = new_job_result["code"]
    message = json.dumps(new_job_result)

    if code not in range(200, 300):
        # Inform the error microservice
        #print('\n\n-----Invoking error microservice as order fails-----')
        print('\n\n-----Publishing the (order error) message with routing_key=order.error-----')

        # invoke_http(error_URL, method="POST", json=order_result)
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="order.error", 
            body=message, properties=pika.BasicProperties(delivery_mode = 2)) 
        # make message persistent within the matching queues until it is received by some receiver 
        # (the matching queues have to exist and be durable and bound to the exchange)

        # - reply from the invocation is not used;
        # continue even if this invocation fails        
        print("\nOrder status ({:d}) published to the RabbitMQ Exchange:".format(
            code), order_result)

        # 7. Return error
        return {
            "code": 500,
            "data": {"order_result": order_result},
            "message": "Order creation failure sent for error handling."
        }

    # Notice that we are publishing to "Activity Log" only when there is no error in order creation.
    # In http version, we first invoked "Activity Log" and then checked for error.
    # Since the "Activity Log" binds to the queue using '#' => any routing_key would be matched 
    # and a message sent to “Error” queue can be received by “Activity Log” too.

    else:
        # 4. Record new order
        # record the activity log anyway
        #print('\n\n-----Invoking activity_log microservice-----')
        print('\n\n-----Publishing the (order info) message with routing_key=order.info-----')        

        # invoke_http(activity_log_URL, method="POST", json=order_result)            
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="order.info", 
            body=message)
        # If there is no error, it publishes the message with routing_key=order.info. Only Activity Log  will receive the message.
    
    print("\nOrder published to RabbitMQ Exchange.\n")
    # - reply from the invocation is not used;
    # continue even if this invocation fails
    
    # 5. Send new order to shipping
    # Invoke the shipping record microservice
    print('\n\n-----Invoking shipping_record microservice-----')    
    
    shipping_result = invoke_http(
        shipping_record_URL, method="POST", json=order_result['data'])
    print("shipping_result:", shipping_result, '\n')

    # Check the shipping result;
    # if a failure, send it to the error microservice.
    code = shipping_result["code"]
    if code not in range(200, 300):
        # Inform the error microservice
        #print('\n\n-----Invoking error microservice as shipping fails-----')
        print('\n\n-----Publishing the (shipping error) message with routing_key=shipping.error-----')

        # invoke_http(error_URL, method="POST", json=shipping_result)
        message = json.dumps(shipping_result)
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="shipping.error", 
            body=message, properties=pika.BasicProperties(delivery_mode = 2))

        print("\nShipping status ({:d}) published to the RabbitMQ Exchange:".format(
            code), shipping_result)

        # 7. Return error
        return {
            "code": 400,
            "data": {
                "order_result": order_result,
                "shipping_result": shipping_result
            },
            "message": "Simulated shipping record error sent for error handling."
        }

    # 7. Return created order, shipping record
    return {
        "code": 201,
        "data": {
            "order_result": order_result,
            "shipping_result": shipping_result
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
