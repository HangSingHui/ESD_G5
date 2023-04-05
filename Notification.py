#!/usr/bin/env python3
from flask import Flask, jsonify
from flask_mail import Mail, Message
import os, sys

import json
# sys.path.append('../SimpleMS')
import amqp_setup

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

monitorBindingKey='#.notification'

def receiveNotif():
    amqp_setup.check_setup() 
    queue_name = 'notification'
    amqp_setup.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    amqp_setup.channel.start_consuming() 

#Actions on the message - send to the GMAIl API
def callback(channel, method, properties, body): 
    print("\nReceived notification by " + __file__)
    body = body.decode('utf-8')
    print(body)
    processNotif(body,method.routing_key)
    print() # print a new line feed

mail_signature = "\n\nDo contact us via our support email at inquiries.petsrus@gmail.com for any queries.\n\nThank you for using Pets R Us!\n\nBest Regards,\nPet R Us (With Pets, For Pets)"

def processNotif(info,routing_key):

    subject="[None - Do Not Reply]"
    body = ""

    #Step 1: Check the routing key of the message
    if routing_key == "accept.sitter.notification":
        subject = "[Job Offer!]"
        body= "Dear Pets R Us Sitter ,\n\nWe are pleased to inform you that you have been accepted as a sitter! Please access the app to view more details. Should you wish to turn down the offer, kindly indicate in the Pet's R Us mobile application within the next 12 hours." 
        recipient = info
    
    
    # message to OWNER about CONFIRMATION OF JOB ACCEPTANCE (SC. 2)
    elif routing_key=="pmt.hold.success.notification":
        subject = "[Successful Payment!]"
        body= "Dear Pets R Us User,\n\nWe have successfully received your payment for your recent sitter acceptance."
        recipient = info

    # message to SITTER about CHARGED PENALTY AND DEDUCTION OF POINTS FOR PULLING OUT (SC. 3)
    elif routing_key == 'penalty.notification':
        notif = json.loads(info)
        subject = "[Penalty Charged] for job <jobID: " + str(notif['jobID'])+">"
        body= "Dear " + notif['sitterName'] + ",\n\nYou have been charged a penalty fee of $20 due to the last-minute pull out from job <jobID: "+ str(notif['jobID']) + ">. We have also deduct your user score by 50 points. Your current user score is "+ str(notif['sitterUserScore']) +" points. Please avoid pulling out from a job less than 24 hours before the job commences.\n\nThank you."   
        recipient = notif['sitterEmail']

    # message to OWNER about SITTER PULLING OUT AND SITTER REPLACEMENTS (SC. 3)
    elif routing_key=='replacement.notification':
        notif = json.loads(info)
        subject = "[Petsitter Replacements Suggestion] for job <jobID: " + str(notif['jobID'])+">"
        body= "Dear " + notif['ownerName'] +",\n\nWe are sorry to let you know that your matched sitter has pulled out from the job <jobID: "+ str(notif['jobID']) +">.\n\nWe would like to suggest you a list of sitters that could act as a replacement:\n\n"

        num = 1
        # loop to add each sitter's details
        for sitter in notif['replacements']:
            body += str(num)+".\tName: "+sitter['Name'] + ' ('+str(sitter['_id'])+')\n\tRate: '+str(sitter['Hourly_rate'])+"/hr\n\tContact: "+str(sitter['Phone'])+"\n"
            num += 1
        recipient = notif['ownerEmail']

    # message to OWNER about SITTER PULLING OUT (SC. 3)
    elif routing_key=='no.replacement.notification':
        notif = json.loads(info)
        subject = "[Petsitter Pulled Out Last Minute] for job <jobID: " + str(notif['jobID'])+">"
        body= "Dear " + notif['ownerName'] +",\n\nWe are deeply sorry to let you know that your matched sitter has pulled out from the job <jobID: "+ str(notif['jobID']) +">. We hope that you can find another petsitter soon."
        recipient = notif['ownerEmail']

    
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
    receiveNotif()





