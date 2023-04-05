import pika

# These module-level variables are initialized whenever a new instance of python interpreter imports the module;
# In each instance of python interpreter (i.e., a program run), the same module is only imported once (guaranteed by the interpreter).

hostname = "esd-rabbit" # default hostname
port = 5672 # default port
# connect to the broker and set up a communication channel in the connection
connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname,port=port,heartbeat=3600, blocked_connection_timeout=3600,))
    # Note about AMQP connection: various network firewalls, filters, gateways (e.g., SMU VPN on wifi), may hinder the connections;
    # If "pika.exceptions.AMQPConnectionError" happens, may try again after disconnecting the wifi and/or disabling firewalls.
    # If see: Stream connection lost: ConnectionResetError(10054, 'An existing connection was forcibly closed by the remote host', None, 10054, None)
    # - Try: simply re-run the program or refresh the page.
    # For rare cases, it's incompatibility between RabbitMQ and the machine running it,
    # - Use the Docker version of RabbitMQ instead: https://www.rabbitmq.com/download.html
print('creating channel')
channel = connection.channel()
print('channel created')
# Set up the exchange if the exchange doesn't exist
# - use a 'topic' exchange to enable interaction
exchangename="notification_topic"
exchangetype="topic"
channel.exchange_declare(exchange=exchangename, exchange_type=exchangetype, durable=True)
    # 'durable' makes the exchange survive broker restarts


# Here can be a place to set up all queues needed by the microservices,
# - instead of setting up the queues using RabbitMQ UI.


############   notification queue    #############
#delcare message queue
queue_name = 'notification'
channel.queue_declare(queue=queue_name, durable=True)
    # 'durable' makes the queue survive broker restarts
#bind Activity_Log queue
channel.queue_bind(exchange=exchangename, queue=queue_name, routing_key='#.notification') 
    # bind the queue to the exchange via the key
    # 'routing_key=#' => any routing_key would be matched

queue_name = "payment_success"
channel.queue_declare(queue=queue_name, durable=True)
channel.queue_bind(exchange=exchangename, queue=queue_name, routing_key='*.payment') 

############   penalty queue    #############
#delcare message queue
queue_name = 'penalty'
channel.queue_declare(queue=queue_name, durable=True)
channel.queue_bind(exchange=exchangename, queue=queue_name, routing_key='#.penalty') 
    # bind the queue to the exchange via the key
    # 'routing_key=#' => any routing_key would be matched

# direct exchange 
# exchangename="job_filterby_pet_topic"
# exchangetype="topic"
# channel.exchange_declare(exchange=exchangename, exchange_type=exchangetype, durable=True)

# pets - Dog / Cat / Rabbit / Bird 
# hourly rate - filter in notification.py 

############   Pets - Dog queue   #############
#delcare Error queue
queue_name = 'Dog'
channel.queue_declare(queue=queue_name, durable=True) 
channel.queue_bind(exchange=exchangename, queue=queue_name, routing_key='dog') 

############   Pets - Cat queue   #############
queue_name = 'Cat'
channel.queue_declare(queue=queue_name, durable=True) 
channel.queue_bind(exchange=exchangename, queue=queue_name, routing_key='cat') 

############   Pets - Rabbit queue   #############
queue_name = 'Rabbit'
channel.queue_declare(queue=queue_name, durable=True) 
channel.queue_bind(exchange=exchangename, queue=queue_name, routing_key='rabbit') 

############   Pets - Bird queue   #############
queue_name = 'Bird'
channel.queue_declare(queue=queue_name, durable=True) 
channel.queue_bind(exchange=exchangename, queue=queue_name, routing_key='bird') 

def check_setup():
    # The shared connection and channel created when the module is imported may be expired, 
    # timed out, disconnected by the broker or a client;
    # - re-establish the connection/channel is they have been closed
    global connection, channel, hostname, port, exchangename, exchangetype

    if not is_connection_open(connection):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, port=port, heartbeat=3600, blocked_connection_timeout=3600))
    if channel.is_closed:
        channel = connection.channel()
        channel.exchange_declare(exchange=exchangename, exchange_type=exchangetype, durable=True)


def is_connection_open(connection):
    # For a BlockingConnection in AMQP clients,
    # when an exception happens when an action is performed,
    # it likely indicates a broken connection.
    # So, the code below actively calls a method in the 'connection' to check if an exception happens
    try:
        connection.process_data_events()
        return True
    except pika.exceptions.AMQPError as e:
        print("AMQP Error:", e)
        print("...creating a new connection.")
        return False


