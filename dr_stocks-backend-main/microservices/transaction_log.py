#!/usr/bin/env python3
import json, os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cors import CORS
from os import environ

import amqp_setup
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL') or 'mysql+mysqlconnector://root@localhost:3306/transaction_logDB'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

CORS(app)

db = SQLAlchemy(app)

class Trans_Log(db.Model):
    __tablename__ = 'transaction_log'
    transactionid = db.Column(db.Integer, primary_key=True, nullable=False)
    accid = db.Column(db.Integer, nullable=False)
    trade_accid = db.Column(db.Integer, nullable=False)
    transaction_action = db.Column(db.String(20), nullable=False)
    transaction_value = db.Column(db.Numeric(13, 2), nullable=False)
    transaction_date = db.Column(db.DateTime, nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    def __init__(self, transactionid, accid, trade_accid, transaction_action, transaction_value, transaction_date, currency, status):
        self.transactionid = transactionid
        self.accid = accid
        self.trade_accid = trade_accid
        self.transaction_action = transaction_action
        self.transaction_value = transaction_value
        self.transaction_date = transaction_date
        self.currency = currency
        self.status = status

    def json(self):
        return  {
            "transactionid": self.transactionid, 
            "accid": self.accid, 
            "trade_accid": self.trade_accid,
            "transaction_action": self.transaction_action, 
            "transaction_value": self.transaction_value,
            "transaction_date": self.transaction_date,
            "currency": self.currency,
            "status" : self.status
        }

monitorBindingKey= '#.transaction'

def receiveTransactionLog():
    amqp_setup.check_setup()
        
    queue_name = 'transaction_log'
    
    # set up a consumer and start to wait for coming messages
    amqp_setup.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    amqp_setup.channel.start_consuming() # an implicit loop waiting to receive messages; 
    #it doesn't exit by default. Use Ctrl+C in the command window to terminate it.

def callback(channel, method, properties, body): # required signature for the callback; no return
    print("\nReceived a transaction log by " + __file__)
    processTransactionLog(json.loads(body))
    print() # print a new line feed

#check if value is positive and check if currency is valid
def processTransactionLog(transaction):
    print("Recording a transaction log:")
    print(transaction)
    system_output = transaction[0]
    user_input = transaction[1]
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    if system_output["code"] > 300:
        status = 'FAILED'
    else:
        status = 'SUCCESS'
    trans_log = Trans_Log(transactionid=None,accid=system_output["data"]["accid"], trade_accid=system_output["data"]["trade_accid"], transaction_action=str(user_input["transaction_action"]).upper(), transaction_value=user_input["amount"], transaction_date=current_time, currency= str(user_input["currency"]).upper(),status=status)
    db.session.add(trans_log)
    db.session.commit()
    print("Successful record transaction log into database")

if __name__ == '__main__':
    print("\nThis is " + os.path.basename(__file__), end='')
    print(": monitoring routing key '{}' in exchange '{}' ...".format(monitorBindingKey, amqp_setup.exchangename))
    receiveTransactionLog()
    app.run(port=5005, debug=True)