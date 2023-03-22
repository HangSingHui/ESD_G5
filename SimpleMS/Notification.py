#!/usr/bin/env python3
from flask import Flask
from flask_mail import Mail, Message
import os

app = Flask(__name__)

mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": os.environ['EMAIL_USER'],
    "MAIL_PASSWORD": os.environ['EMAIL_PASSWORD']
}

app.config.update(mail_settings)
mail = Mail(app)

import json
import os

import amqp_setup

monitorBindingKey='*.notification'

def receiveNotif():
    amqp_setup.check_setup()
        
    queue_name = 'notification'
    
    amqp_setup.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    amqp_setup.channel.start_consuming() 

#Actions on the message - send to the GMAIl API
def callback(channel, method, properties, body): 
    print("\nReceived notification by " + __file__)
    processNotif(json.loads(body))
    print() # print a new line feed

def sendNotif(notif):
    # print("Recording an order log:")
    # print(order)
    pass

if __name__ == '__main__':
    with app.app_context():
        msg = Message(subject="Hello",
                      sender=app.config.get("MAIL_USERNAME"),
                      recipients=["<recipient email here>"], # replace with your email for testing
                      body="This is a test email I sent with Gmail and Python!")
        mail.send(msg)



# if __name__ == "__main__": 
#     print("\nThis is " + os.path.basename(__file__), end='')
#     print(": monitoring routing key '{}' in exchange '{}' ...".format(monitorBindingKey, amqp_setup.exchangename))
#     receiveNotification()




