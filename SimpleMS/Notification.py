#!/usr/bin/env python3
from flask import Flask
from flask_mail import Mail, Message
import os

import json
import amqp_setup

app = Flask(__name__)

mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": os.environ['EMAIL_USER'], #noreply.petsrus@gmail.com
    "MAIL_PASSWORD": os.environ['EMAIL_PASSWORD'] #hyilskfcwghyotff
}

app.config.update(mail_settings)
mail = Mail(app)


monitorBindingKey='#.notification'

def receiveNotif():
    amqp_setup.check_setup() 
    queue_name = 'notification'
    amqp_setup.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    amqp_setup.channel.start_consuming() 

#Actions on the message - send to the GMAIl API
def callback(channel, method, properties, body): 
    print("\nReceived notification by " + __file__)
    processNotif(json.loads(body),method.routing_key)
    print() # print a new line feed

mail_signature = "\n Do contact us via our support email at inquiries.petsrus@gmail.com for any queries. \n Thank you for using Pets R Us! \n\n Best Regards, Pet R Us (With Pets, For Pets)"

def processNotif(notif,routing_key):
    # print("Recording an order log:")
    # print(order)  

    #structure of AMQP message (JSON - routing key = accept.sitter.notification
    # {
    #    "sitterEmail": "lebubbub@gmail.com",
    #    "jobTitle": "Dog Walking",
    #     "sitterName": "Sally",
    #       "jobID": 123   
    # }

    #Step 1: Check the routing key of the message
    if routing_key == "accept.sitter.notification":
        subject = "[Job Offered: ]" + str(notif.jobID)
        body= "Dear " + notif.sitterName + ",\n We are pleased to inform you that your application for the job titled: "  + notif.jobTitle + "(" + str(notif.jobID) + ") has been accepted by the owner. Kindly indicate your acceptance of the offer in the Pet's R Us mobile application within the next 12 hours." 
        recipient = notif.sitterEmail
    
     #structure of AMQP message (JSON - routing key = hold.payment.notification)
    # {
    #    "ownerEmail": "lebubbub@gmail.com",
    #    "jobTitle": "Dog Walking",
    #     "sitterName": "Sally",
    #      "jobD": 123.
    #       "totalPayable": $40,
    #       "cardInfo": 1314 #last 4 numbers
    # }
    
    elif routing_key=="hold.payment.notification":
        subject = "[On-hold Payment: ]" + str(notif.jobID)
        body= "Dear " + notif.ownerName + ",\n Your accepted sitter" + notif.sitterName + " has confirmed the acceptance of your job posting titled " + notif.jobTitle + "(" + str(notif.jobID) + "). We have successfully placed a hold of " + notif.totalPayable + " on your card ending with " + str(notif.cardInfo) + "."    
        recipient = notif.ownerEmail
    
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





