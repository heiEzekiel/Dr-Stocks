#!/usr/bin/env python3
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cors import CORS
import json
import os
from os import environ

import amqp_setup
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL') or 'mysql+mysqlconnector://root@localhost:3306/trade_logDB'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

CORS(app)

class Trade_Log(db.Model):
    __tablename__ = 'trade_log'
    tradeid = db.Column(db.Integer, primary_key=True, nullable=False)
    accid = db.Column(db.Integer, nullable=False)
    trade_date = db.Column(db.DateTime, nullable=False)
    trade_value = db.Column(db.Numeric(13, 2), nullable=False)
    trade_stock_symbol = db.Column(db.String(5), nullable=False)
    trade_quantity = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    trade_action = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    def __init__(self, tradeid, accid, trade_date, trade_value, trade_stock_symbol, trade_quantity, currency, trade_action, status):
        self.tradeid = tradeid
        self.accid = accid
        self.trade_date = trade_date
        self.trade_value = trade_value
        self.trade_stock_symbol = trade_stock_symbol
        self.trade_quantity = trade_quantity
        self.currency = currency
        self.trade_action = trade_action
        self.status = status

    def json(self):
        return {
            "tradeid": self.tradeid, 
            "accid": self.accid, 
            "trade_date": self.trade_date,
            "trade_value": self.trade_value, 
            "trade_stock_symbol": self.trade_stock_symbol,
            "trade_quantity": self.trade_quantity,
            "currency": self.currency,
            "trade_action": self.trade_action,
            "status" : self.status
        }

monitorBindingKey = "#.trade"

def receiveTradeLog():
    amqp_setup.check_setup()
        
    queue_name = 'trade_log'
    
    # set up a consumer and start to wait for coming messages
    amqp_setup.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    amqp_setup.channel.start_consuming() # an implicit loop waiting to receive messages; 
    #it doesn't exit by default. Use Ctrl+C in the command window to terminate it.

def callback(channel, method, properties, body): # required signature for the callback; no return
    print("\nReceived a transaction log by " + __file__)
    processTradeLog(json.loads(body))

    print() # print a new line feed

def processTradeLog(trade):
    print("Recording a trade log:")
    print(trade)
    system_output = trade[0]
    user_input = trade[1]
    stock_info = trade[2]
    trading_value = round(stock_info["data"]["c"] * user_input["stock_quantity"],2)
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    if system_output["code"] > 300:
        status = 'FAILED'
    else:
        status = 'SUCCESS'
    trade_log = Trade_Log(tradeid=None,accid=system_output["data"]["accid"], trade_date=current_time, trade_value=trading_value, trade_stock_symbol=str(user_input["stock_symbol"]).upper(),trade_quantity=user_input["stock_quantity"],currency=str(user_input["currency"]).upper(),trade_action=str(user_input["transaction_action"]).upper(), status=str(status).upper())
    db.session.add(trade_log)
    db.session.commit()
    print("Successful record transaction log into database")

if __name__ == '__main__':
    print("\nThis is " + os.path.basename(__file__), end='')
    print(": monitoring routing key '{}' in exchange '{}' ...".format(monitorBindingKey, amqp_setup.exchangename))
    receiveTradeLog()
    app.run(host='0.0.0.0', port=5003, debug=True)