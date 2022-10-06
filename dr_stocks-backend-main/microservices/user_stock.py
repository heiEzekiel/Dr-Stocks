import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL') or 'mysql+mysqlconnector://root@localhost:3306/user_stockDB'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

CORS(app)

db = SQLAlchemy(app)


class User_Stock(db.Model):
    __tablename__ = 'user_stock'
    user_stockid = db.Column(db.Integer, primary_key=True, nullable=False)
    accid = db.Column(db.Integer, nullable=False)
    tradeid = db.Column(db.Integer, nullable=False)
    stock_symbol = db.Column(db.String(5), nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False)
    purchased_price = db.Column(db.Numeric(13, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    def __init__(self, user_stockid, accid, tradeid, stock_symbol, stock_quantity, purchased_price, currency):
        self.user_stockid = user_stockid
        self.accid = accid
        self.tradeid = tradeid
        self.stock_symbol = stock_symbol
        self.stock_quantity = stock_quantity
        self.purchased_price = purchased_price
        self.currency = currency

    def json(self):
        return {
            "user_stockid": self.user_stockid, 
            "accid": self.accid, 
            "tradeid": self.tradeid, 
            "stock_symbol": self.stock_symbol,
            "stock_quantity": self.stock_quantity,
            "purchased_price": self.purchased_price,
            "currency": self.currency
        }

#GET
@app.route("/user_stock/<string:accid>")
def find_by_accID(accid):
    if len(str(accid)) != 7 or (not str(accid).isdigit):
        return jsonify(
            {
                "code": 404,
                "message": "Invalid account ID."
            }
        ), 404
    user_stock_list = User_Stock.query.filter_by(accid=accid)#.first()
    if user_stock_list.first():
        return jsonify(
            {
                "code": 200,
                "user_stocks": [user_stock.json() for user_stock in user_stock_list]
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "No user stock found."
        }
    ), 404


#POST
@app.route("/user_stock/buy/<string:accid>", methods=['POST'])
def buying_user_stock(accid):
    stock_info = request.get_json()[0]["data"]
    user_info = request.get_json()[1]["data"]
    trade = request.get_json()[2]
    #Check if accID matches
    if (str(accid) != str(user_info['accid'])):
        return jsonify(
            {
                "code": 401,
                "message": "Unauthorised action performed by user."
            }
        )
    try:
        user_stock = User_Stock(user_stockid="",accid=accid, tradeid=user_info["trade_accid"], stock_symbol=str(trade["stock_symbol"]).upper(), stock_quantity=trade["stock_quantity"], purchased_price=stock_info["c"], currency=str(trade["currency"]).upper())
        db.session.add(user_stock)
        db.session.commit()
    except:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "accid": accid,
                },
                "message": "An error occurred buying user stock(s)."
            }
        )
    return jsonify(
            {
                "code": 200,
                "data":{
                    "accid": accid,
                },
                "message": "User stock(s) successfully bought"
            }
    )

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
    app.run(host='0.0.0.0', port=5007, debug=True)