#!/usr/bin/env python3
import json, os, amqp_setup, sendgrid, base64
from sendgrid.helpers.mail import Mail, Email, To, Content

monitorBindingKey='*.log'

def receiveEmailNotification():
    amqp_setup.check_setup()
    queue_name = 'email_notification'

    # set up a consumer and start to wait for coming messages
    amqp_setup.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    amqp_setup.channel.start_consuming() # an implicit loop waiting to receive messages; 
    #it doesn't exit by default. Use Ctrl+C in the command window to terminate it.

def callback(channel, method, properties, body):
    print("\nReceived an email notification log by " + __file__)
    get_stock_info(json.loads(body))
    print() # print a new line feed

def get_stock_info(senddata):
    system_output = senddata[0]
    user_input = senddata[1]
    text = "U0cuN1ZPa0lCamhROHFFUDdweDdvNkFRUS53OFhmYVJ2QUYxcDZxSHBxclF6dWI5WUFteHZweUtuTm1WZkl5bVFvMXRR"
    msg = base64.b64decode(text)
    key = str(msg.decode('ascii'))
    sg = sendgrid.SendGridAPIClient(api_key=key)
    from_email = Email("dr.stocks.pte.ltd@gmail.com")  # Change to your verified sender
    to_email = To(user_input["email"])
    email = user_input["email"]
    subject = ""
    content_text = ""
    if (str(user_input["transaction_action"]).upper() == 'DEPOSIT'):
        subject = "[Dr. Stocks] - Status update on your deposit"
        if (system_output["code"] == 500):
            content_text = f"Dear {email}, \n\nDeposit service has failed. The server faced an internal error. \nPlease try again later. \n\nRegards, \n\nDr. Stocks PTE LTD"
        elif (system_output["code"] > 300):
            content_text = f"Dear {email}, \n\nDeposit service has failed. There is an error processing the deposit. \nPlease try again later. \n\nRegards, \n\nDr. Stocks PTE LTD"
        else:
            content_text = f"Dear {email}, \n\nDeposit service has been successfully registered. \n\nRegards, \n\nDr. Stocks PTE LTD"
    elif (str(user_input["transaction_action"]).upper() == 'BUY'):
        subject = "[Dr. Stocks] - Status update on your buying stock"
        if (system_output["code"] == 500):
            content_text = f"Dear {email}, \n\nBuying stock service has failed. The server faced an internal error. \nPlease try again later. \n\nRegards, \n\nDr. Stocks PTE LTD"
        elif (system_output["code"] > 300):
            content_text = f"Dear {email}, \n\nBuying stock service has failed. There is an error processing the deposit. \nPlease try again later. \n\nRegards, \n\nDr. Stocks PTE LTD"
        else:
            content_text = f"Dear {email}, \n\nBuying stock service has been successfully registered. \n\nRegards, \n\nDr. Stocks PTE LTD"
    else:
        subject = "[Dr. Stocks] - Error occured when processing your request"
        content_text = f"Dear {email}, \n\nThere is an error processing your request. \n\nRegards, \n\nDr. Stocks PTE LTD"
      # Change to your recipient
    content = Content("text/plain", content_text)
    mail = Mail(from_email, to_email, subject, content)

    # Get a JSON-ready representation of the Mail object
    mail_json = mail.get()

    # Send an HTTP POST request to /mail/send
    response = sg.client.mail.send.post(request_body=mail_json)
    res = str(response.headers).split("\n")
    print(
        {
            "code":str(response.status_code),
            "data":res
        }
    )

if __name__ == '__main__':
    print("\nThis is " + os.path.basename(__file__), end='')
    print(": monitoring routing key '{}' in exchange '{}' ...".format(monitorBindingKey, amqp_setup.exchangename))
    receiveEmailNotification()

