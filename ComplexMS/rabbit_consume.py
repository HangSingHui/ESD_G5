#!/usr/bin/env python3
import json
import os, sys

sys.path.append("../SimpleMS")
import amqp_setup

from invokes import invoke_http

from flask import Flask
from flask_mail import Mail, Message


app = Flask(__name__)

mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": os.environ.get('EMAIL_USER', 'noreply.petsrus@gmail.com'),
    "MAIL_PASSWORD": os.environ.get('EMAIL_PASSWORD', 'qadqazlflabbbaym')
}


app.config.update(mail_settings)
mail = Mail(app)

sitter_URL = "http://localhost:5100/sitter" #to invoke later on
job_URL ="http://localhost:5005/job"

monitorBindingKey='rabbit.#'

def receiveJob():
    amqp_setup.check_setup() 
    queue_name = 'Rabbit'
    amqp_setup.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    amqp_setup.channel.start_consuming() 

#Actions on the message - send to the GMAIl API
def callback(channel, method, properties, body): 
    print("\nReceived notification by " + __file__)
    body = body.decode('utf-8')
    print(body) #body is just the jobID
    processJob(body,method.routing_key)
    print() # print a new line feed


def processJob(jobID,routing_key): 

    #invoke job to get the rate
    get_job = invoke_http(job_URL+"/"+jobID,method="GET")
    code = get_job["code"]
    if code not in range(200,300):
        return jsonify({
            "code":404,
            "message": "Job not found."
        })
    
    rate = int(get_job["data"][0]["Hourly_rate"]["$numberDecimal"])
    title = get_job["data"][0]["Title"]
    # print(rate)

    # categorise rate 
    if (rate>30 and rate<40): 
        rate_cat = "cat1"
    elif (rate>40 and rate<50): 
        rate_cat = "cat2"
    if (rate>50 and rate<60): 
        rate_cat = "cat3"
    
    # rate argument will be a category -> do validation again in sitter.py func 7 
    print('\n-----Invoking sitter microservice-----')
    getEmailList =invoke_http(sitter_URL+"/Rabbit"+"/"+rate_cat) #get email of all sitters
    emailList = getEmailList["emails"]

    # Check the sitterlist result; if a failure, return error status 
    code = getEmailList["code"]
    if code not in range(200, 300):     
        # Return error
        return {
                "code": 500,
                "message": "Sitter list unable to be obtained."
            }
    
    #Send email
    mail_signature = "\n Do contact us via our support email at inquiries.petsrus@gmail.com for any queries. \n Thank you for using Pets R Us! \n\n Best Regards, Pet R Us (With Pets, For Pets)"

    if routing_key == "rabbit.*":
        subject = "[Available job posting]"
        body= "Dear Pets R Us Sitter,\n We are pleased to inform you that there is an available job posting with your indicated species and within the range of your hourly rate preference: " + title + "\nShould you wish to to take up the job, please indicate in the Pet's R Us mobile application, while still available." 
        recipient = emailList

        body += mail_signature
        with app.app_context():
            msg = Message(subject=subject,
                        sender=app.config.get("MAIL_USERNAME"),
                        recipients=[recipient], 
                        body=body)
            mail.send(msg)


if __name__ == "__main__":  # execute this program only if it is run as a script (not by 'import')
    print("\nThis is " + os.path.basename(__file__), end='')
    print(": monitoring routing key '{}' in exchange '{}' ...".format(monitorBindingKey, amqp_setup.exchangename))
    receiveJob()
