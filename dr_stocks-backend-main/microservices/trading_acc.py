import os, decimal
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL') or 'mysql+mysqlconnector://root@localhost:3306/trading_accDB'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

CORS(app)

db = SQLAlchemy(app)

class Trading_Acc(db.Model):
    __tablename__ = 'trading_acc'
    trade_accid = db.Column(db.Integer, primary_key=True, nullable=False)
    accid = db.Column(db.Integer, nullable=False)
    trade_acc_balance = db.Column(db.Numeric(13, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    def __init__(self, trade_accid, accid, trade_acc_balance, currency):
        self.trade_accid = trade_accid
        self.accid = accid
        self.trade_acc_balance = trade_acc_balance
        self.currency = currency

    def json(self):
        return {
            "trade_accid": self.trade_accid, 
            "accid": self.accid, 
            "trade_acc_balance": self.trade_acc_balance,
            "currency": self.currency
        }

#GET
@app.route("/trading_acc/<string:accid>/<string:currency>")
def find_by_accid(accid, currency):
    currency = str(currency).upper()
    if (len(str(accid)) != 7) or (not str(accid).isdigit):
        return jsonify(
            {
                "code": 404,
                "message": "Invalid account ID."
            }
        ), 404
    if not str(currency).isalpha():
        return jsonify(
            {
                "code": 404,
                "message": "Invalid currency."
            }
        ), 404
    trading_acc = Trading_Acc.query.filter_by(accid=accid, currency=currency).first()
    if trading_acc:
        return jsonify(
            {
                "code": 200,
                "data": trading_acc.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Trading account not found."
        }
    ), 404

#PUT (Minus)
@app.route("/trading_acc/minus/<string:accid>", methods=['PUT'])
def minus(accid):
    trading_acc = Trading_Acc.query.filter_by(accid=accid).first()
    if trading_acc:
        stock_info = request.get_json()[0]["data"]
        user_info = request.get_json()[1]["data"]
        trade = request.get_json()[2]
        if (user_info['trade_accid'] == trading_acc.trade_accid) and (user_info['accid'] == trading_acc.accid):
            if trading_acc.trade_acc_balance >= stock_info['c'] * trade['stock_quantity']: #check balance 
                trading_acc.trade_acc_balance -= decimal.Decimal(stock_info['c']) * decimal.Decimal(trade['stock_quantity'])
                try:    
                    db.session.commit()
                    return jsonify(
                        {
                            "code": 200,
                            "data": trading_acc.json(),
                            "message": "Successfully updated trading account balance."
                        }
                    )
                except:
                    return jsonify(
                        {
                            "code": 500,
                            "data": trading_acc.json(),
                            "message": "An error occurred updating account balance. No changes has been made."
                        }
                    )
            return jsonify(
                {
            "code": 400,
            "data": {
                "accid": accid
            },
            "message": "Insufficient balance in trading account. Please top up"
        }
    ), 404
    return jsonify(
        {
            "code": 404,
            "data": {
                "accid": accid
            },
            "message": "Trading account not found."
        }
    ), 404

#PUT (PLUS)
@app.route("/trading_acc/plus/<string:accid>", methods=['PUT'])
def plus(accid):
    trading_acc = Trading_Acc.query.filter_by(accid=accid).first()
    if trading_acc:
        user_info = request.get_json()[0]["data"]
        deposit = request.get_json()[1]
        # Check if trade acc id and acc id exists
        if (user_info['trade_accid'] != trading_acc.trade_accid) or (user_info['accid'] != trading_acc.accid):
            return jsonify(
                {
                    "code": 404,
                    "data": trading_acc.json(),
                    "message": "User's account id does not match  with trading account id."
                }
            )
        
        # Check if deposit is valid
        if decimal.Decimal(deposit['amount']) < 0:
            return jsonify(
                {
                    "code": 404,
                    "data": trading_acc.json(),
                    "message": "Deposit amount cannot be negative."
                }
            )

        trading_acc.trade_acc_balance += decimal.Decimal(deposit['amount'])
        try:    
            db.session.commit()
            return jsonify(
                {
                    "code": 200,
                    "data": trading_acc.json(),
                    "message": "Successfully updated trading account balance."
                }
            )
        except:
            return jsonify(
                {
                    "code": 500,
                    "data": trading_acc.json(),
                    "message": "An error occurred updating account balance. No changes has been made."
                }
            )

    return jsonify(
        {
            "code": 404,
            "data": {
                "accid": accid
            },
            "message": "Trading account not found."
        }
    ), 404

# Error Handling 
@app.errorhandler(404) 
def invalid_route(e): 
    return jsonify(
        {
            "code": 404,
            "message": "Invalid route."
        }
    ), 404

@app.errorhandler(500) 
def invalid_route(e): 
    return jsonify(
        {
            "code": 500,
            "message": "Unexpected error occured."
        }
    ), 500

@app.errorhandler(405) 
def invalid_route(e): 
    return jsonify(
        {
            "code": 405,
            "message": "Action not allowed."
        }
    ), 405


if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": manage orders ...")
    app.run(host='0.0.0.0',port=5004, debug=True)



