import json
import os, sys

sys.path.append("SimpleMS")

from SimpleMS import amqp_setup

from invokes import invoke_http

######## from notfication.py ########
#!/usr/bin/env python3
from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)

mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": os.environ.get('EMAIL_USER','noreply.petsrus@gmail.com'),
    "MAIL_USERNAME": os.environ.get('EMAIL_PASSWORD','hyilskfcwghyotff')
}

app.config.update(mail_settings)
mail = Mail(app)
#####################################

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
    # processSpecies return emails of sitters 
    result= processSpecies(json.loads(body)) 
    print() # print a new line feed

    # UDPATE THIS
    emails = result["data"]["sitterlist"] #assuming the sittelist contains only the emails?? 

    ######## from notfication.py ########
    processNotif(json.loads(emails),method.routing_key)
    #####################################


def processSpecies(message): #get sitter function
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

    # categorise rate 
    if (rate>30 and rate<40): 
        rate_cat = "cat1"
    if (rate>40 and rate<50): 
        rate_cat = "cat2"
    if (rate>50 and rate<60): 
        rate_cat = "cat3"
    
    # rate argument will be a category -> do validation again in sitter.py func 7 
    print('\n-----Invoking sitter microservice-----')
    sitterList =invoke_http(sitter_URL+"/"+species+"/"+rate_cat) #get all sitters

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

######## from notfication.py ########

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
    # include url to find by jobid?? 
    if routing_key == "dog.*":
        subject = "[Available job posting: ]" + str(notif.jobID)
        body= "Dear " + notif.sitterName + ",\n We are pleased to inform you that there is an available job posting with your indicated species and around the range of your hourly rate preference: "  + notif.jobTitle + "(" + str(notif.jobID) + ". Should you wish to to take up the job, please indicate in the Pet's R Us mobile application, while still available." 
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
    
    # # message to OWNER about CONFIRMATION OF JOB ACCEPTANCE (SC. 2)
    # elif routing_key=="pmt.hold.success.notification":
    #     subject = "[On-hold Payment] for job " + str(notif.jobID)
    #     body= "Dear " + notif.ownerName + ",\n You" + notif.sitterName + " has confirmed the acceptance of your job posting titled " + notif.jobTitle + "(" + str(notif.jobID) + "). We have successfully placed a hold of " + notif.totalPayable + " on your card ending with " + str(notif.cardInfo) + "."    
    #     recipient = notif.ownerEmail

    # # message to SITTER about CHARGED PENALTY AND DEDUCTION OF POINTS FOR PULLING OUT (SC. 3)
    # elif routing_key == 'penalty.notification':
    #     subject = "[Penalty Charged] for job " + str(notif.jobID)
    #     body= "Dear " + notif.sitterName + ",\nYou have been charged a penalty fee of $20 due to the last-minute pull out from job "+ str(notif.jobID) + ". We have also deduct your user score by 50 points. Your current user score is "+ notif.sitterUserScore +". Please avoid pulling out from a job more than a day after the job has been confirmed. Thank you."   
    #     recipient = notif.sitterEmail

    # # message to OWNER about SITTER REPLACEMENTS (SC. 3)
    # elif routing_key=='replacement.notification':
    #     subject = "[Petsitter Replacements Suggestion] for job " + str(notif.jobID)
    #     body= "Dear " + notif.ownerName +",\nWe are sorry to say that your matched sitter has pulled out from the job "+ str(notif.jobID) +".\nWe would like to suggest you a list of sitters that could act as a replacement:"

    #     num = 1
    #     # loop to add each sitter's details
    #     for sitter in notif.replacements:
    #         body += str(num)+". \tName: "+sitter['Name'] + ' ('+str(sitter['_id'])+')\n\tRate: '+sitter['Hourly_rate']+"/hr\n\tContact: "+sitter['Phone']
    #         num += 1
    #     recipient = notif.ownerEmail

    
    body += mail_signature
    with app.app_context():
        msg = Message(subject=subject,
                    sender=app.config.get("MAIL_USERNAME"),
                    recipients=[recipient], 
                    body=body)
        mail.send(msg)
#####################################

if __name__ == "__main__":  # execute this program only if it is run as a script (not by 'import')
    print("\nThis is " + os.path.basename(__file__), end='')
    print(": monitoring routing key '{}' in exchange '{}' ...".format(monitorBindingKey, amqp_setup.exchangename))
    receiveOrderLog()
