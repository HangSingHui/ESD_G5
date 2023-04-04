import json
import os

import amqp_setup

from invokes import invoke_http

# ######## from notfication.py ########
# #!/usr/bin/env python3
# from flask import Flask
# from flask_mail import Mail, Message
# import os

# import json
# import amqp_setup

# app = Flask(__name__)

# mail_settings = {
#     "MAIL_SERVER": 'smtp.gmail.com',
#     "MAIL_PORT": 465,
#     "MAIL_USE_TLS": False,
#     "MAIL_USE_SSL": True,
#     "MAIL_USERNAME": os.environ['EMAIL_USER'], #noreply.petsrus@gmail.com
#     "MAIL_PASSWORD": os.environ['EMAIL_PASSWORD'] #hyilskfcwghyotff
# }

# app.config.update(mail_settings)
# mail = Mail(app)
# #####################################

sitter_URL = "http://localhost:5100/sitter"

monitorBindingKey='dog.*'

def receiveOrderLog():
    amqp_setup.check_setup()
        
    queue_name = 'Dog'
    
    # set up a consumer and start to wait for coming messages
    # message = json.dumps( {
    #     'job_id': new_job['_id'], 
    #     'owner_id': new_job['OwnerID'], 
    #     'pet_species': pet_species, 
    #     'hourly_rate': new_job['Hourly_rate']
    # })
    amqp_setup.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    amqp_setup.channel.start_consuming() # an implicit loop waiting to receive messages; 
    #it doesn't exit by default. Use Ctrl+C in the command window to terminate it.

def callback(channel, method, properties, body): # required signature for the callback; no return
    print("\nReceived a dog log by " + __file__)
    processOrderLog(json.loads(body)) 
    print() # print a new line feed

def processOrderLog(message): #get sitter function
    # invoke job ms to get the job information
    # extract rate and species from job information

    # message = json.dumps( {
    #     'job_id': new_job['_id'], 
    #     'owner_id': new_job['OwnerID'], 
    #     'pet_species': pet_species, 
    #     'hourly_rate': new_job['Hourly_rate']
    # })
    
    #invoke sitter ms to get sitters that fulfil both the prefernence for rate and species
    #for list of sitters, extract the sitteremails

    species = message['pet_species']
    rate  = message['hourly_rate']

    if (rate>30 and rate<40): 
        rate_cat = "cat1"
    if (rate>40 and rate<50): 
        rate_cat = "cat2"
    if (rate>50 and rate<60): 
        rate_cat = "cat3"
    
    # rate argument will be a category -> do validation again in sitter.py func 7 
    print('\n-----Invoking sitter microservice-----')
    sitterList =invoke_http(sitter_URL+"/"+species+"/"+rate_cat) #get all sitters
    # ASSUMING sitterList - json of all the emails of the sitters subscribed to the queue 
    # invoke notification simple microservice to send notif to all the sitters 

    


    print('sitter_result:', sitterList)

    # Check the sitterlist result; if a failure, return error status 
    code = sitterList["code"]
    if code not in range(200, 300):     
        # Return error
        return {
                "code": 500,
                "data": {"sitterlist": sitterList},
                "message": "Sitter list unable to be obtained."
            }
    # if successful job creation, return code 201
    return {
        "code": 201,
        "data": { "sitterlist": sitterList}, 
    }

if __name__ == "__main__":  # execute this program only if it is run as a script (not by 'import')
    print("\nThis is " + os.path.basename(__file__), end='')
    print(": monitoring routing key '{}' in exchange '{}' ...".format(monitorBindingKey, amqp_setup.exchangename))
    receiveOrderLog()
