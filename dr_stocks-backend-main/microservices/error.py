#!/usr/bin/env python3
import os, json, amqp_setup

monitorBindingKey = '*.error'

def receiveError():
    amqp_setup.check_setup()
    
    queue_name = "error"  

    # set up a consumer and start to wait for coming messages
    amqp_setup.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    amqp_setup.channel.start_consuming() # an implicit loop waiting to receive messages; 
    #it doesn't exit by default. Use Ctrl+C in the command window to terminate it.

def callback(channel, method, properties, body): # required signature for the callback; no return
    print("\nReceived an error by " + __file__)
    processError(body)
    print() # print a new line feed

def processError(errorMsg):
    print("Printing the error message:")
    try:  # check if valid JSON
        error = json.loads(errorMsg)
        print("--JSON:", error)
    except Exception as e:
        print("--INVALID JSON:", e)
        print("--DATA:", errorMsg)
    print() # print a new line feed as a separator

if __name__ == "__main__":  # execute this program only if it is run as a script (not by 'import')    
    print("\nThis is " + os.path.basename(__file__), end='')
    print(": monitoring routing key '{}' in exchange '{}' ...".format(monitorBindingKey, amqp_setup.exchangename))
    receiveError()
