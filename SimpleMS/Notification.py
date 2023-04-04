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
        body= "Dear " + notif.sitterName + ",\n We are pleased to inform you that your application for the job titled: "  + notif.jobTitle + "(" + str(notif.jobID) + ") has been accepted by the owner. Should you wish to turn down the offer, kindly indicate in the Pet's R Us mobile application within the next 12 hours." 
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
    
    # message to OWNER about CONFIRMATION OF JOB ACCEPTANCE (SC. 2)
    elif routing_key=="pmt.hold.success.notification":
        subject = "[On-hold Payment] for job " + str(notif.jobID)
        body= "Dear " + notif.ownerName + ",\n You" + notif.sitterName + " has confirmed the acceptance of your job posting titled " + notif.jobTitle + "(" + str(notif.jobID) + "). We have successfully placed a hold of " + notif.totalPayable + " on your card ending with " + str(notif.cardInfo) + "."    
        recipient = notif.ownerEmail

    # message to SITTER about CHARGED PENALTY AND DEDUCTION OF POINTS FOR PULLING OUT (SC. 3)
    elif routing_key == 'penalty.notification':
        subject = "[Penalty Charged] for job " + str(notif.jobID)
        body= "Dear " + notif.sitterName + ",\nYou have been charged a penalty fee of $20 due to the last-minute pull out from job "+ str(notif.jobID) + ". We have also deduct your user score by 50 points. Your current user score is "+ notif.sitterUserScore +". Please avoid pulling out from a job more than a day after the job has been confirmed. Thank you."   
        recipient = notif.sitterEmail

    # message to OWNER about SITTER REPLACEMENTS (SC. 3)
    elif routing_key=='replacement.notification':
        subject = "[Petsitter Replacements Suggestion] for job " + str(notif.jobID)
        body= "Dear " + notif.ownerName +",\nWe are sorry to say that your matched sitter has pulled out from the job "+ str(notif.jobID) +".\nWe would like to suggest you a list of sitters that could act as a replacement:"

        num = 1
        # loop to add each sitter's details
        for sitter in notif.replacements:
            body += str(num)+". \tName: "+sitter['Name'] + ' ('+str(sitter['_id'])+')\n\tRate: '+sitter['Hourly_rate']+"/hr\n\tContact: "+sitter['Phone']
            num += 1
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





