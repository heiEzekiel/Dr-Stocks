from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL') or 'mysql+mysqlconnector://root@localhost:3306/stock_prefDB'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

CORS(app)

class Stock_Pref(db.Model):
    __tablename__ = 'stock_pref'
    stock_prefid = db.Column(db.Integer, primary_key=True, nullable=False)
    accid = db.Column(db.Integer, nullable=False)
    stock_industry = db.Column(db.String(100), nullable=False)
    def __init__(self, stock_prefid, accid, stock_industry):
        self.stock_prefid = stock_prefid
        self.accid = accid
        self.stock_industry = stock_industry

    def json(self):
        return {
            "stock_prefid": self.stock_prefid, 
            "accID": self.accid, 
            "stock_Industry": self.stock_industry
        }

#GET
@app.route("/stock_pref/<string:accid>")
def find_by_accID(accid):
    if len(str(accid)) != 7 or (not str(accid).isdigit):
        return jsonify(
            {
                "code": 404,
                "message": "Invalid account ID."
            }
        ), 404
    user_stock_pref = Stock_Pref.query.filter_by(accid=accid) #.first()
    if user_stock_pref.first():
        return jsonify(
            {
                "code": 200,
                "data": [stock_pref.json() for stock_pref in user_stock_pref]
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Stock preferences not found."
        }
    ), 404


#POST
@app.route("/stock_pref/add/<string:accid>", methods=['POST'])
def create_stock_pref(accid):
    #Variables
    to_add_list, added_list, success_list, error_list  = [], [], [], []
    senddata = request.get_json(force=True)
    #Check if accID matches
    if (str(accid) != str(senddata['accid'])):
        return jsonify(
            {
                "code": 401,
                "message": "Unauthroised action performed by user."
            }
        )
    #Loop thru items in preferences
    for stock_industry in senddata['stock_industry']:
        stock_industry = str(stock_industry).capitalize()
        if (Stock_Pref.query.filter_by(accid=accid, stock_industry=stock_industry).first()):
            added_list.append(stock_industry)
        else:
            to_add_list.append(stock_industry)
    # #If there is an item in preference that is added before, return
    if len(added_list) == len(senddata['stock_industry']):
        return jsonify(
                {
                    "code": 400,
                    "data": {
                        "accid": accid,
                        "stock_industry": added_list
                    },
                    "message": "Stock(s) preference already exists."
                }
            ), 400
    #Loop thru items in to_add_list
    for stock_industry in to_add_list:
        stock_industry = str(stock_industry).capitalize()
        try:
            stock_pref = Stock_Pref(stock_prefid='',accid=accid, stock_industry = stock_industry)
            db.session.add(stock_pref)
            db.session.commit()
            success_list.append(stock_industry)
        except:
            error_list.append(stock_industry)
    
    #If there are errors and success items, delete success list and try all again
    if (len(error_list)) and (len(success_list)):
        #delete success_list
        for success in success_list:
            stock_pref = Stock_Pref.query.filter_by(accid=accid, stock_industry=success).first()
            db.session.delete(stock_pref)
            db.session.commit()
        return jsonify(
            {
                "code": 500,
                "data": {
                    "accid": accid,
                    "stock_industry": error_list
                },
                "message": "An error occurred adding the stock(s) preference. Please try adding the same preferences again."
            }
        ), 500
    #If all have errors
    elif (len(error_list)) and (not len(success_list)):
        return jsonify(
            {
                "code": 500,
                "data": {
                    "accid": accid,
                    "stock_industry": error_list
                },
                "message": "An error occurred adding the stock preference."
            }
        ), 500
    #If all successfully added
    else:
        return jsonify(
            {
                "code": 200,
                "data":{
                    "accid": accid,
                    "stock_industry": success_list
                },
                "message": "Stock preference successfully added"
            }
        )

#REMOVE
@app.route("/stock_pref/remove/<string:accid>", methods=['POST'])
def delete_stock_pref(accid):
    #Variables
    deleted_list, error_list = [], []
    senddata = request.get_json(force=True)
    #Check if accID matches
    if (str(accid) != str(senddata['accid'])):
        return jsonify(
            {
                "code": 401,
                "message": "Unauthorised action performed by user."
            }
        )
    #Loop thru items in preferences
    for stock_industry in senddata["stock_industry"]:
        stock_industry = str(stock_industry).capitalize()
        stock_pref = Stock_Pref.query.filter_by(accid=accid, stock_industry=stock_industry).first()
        if stock_pref:
            db.session.delete(stock_pref)
            db.session.commit()
            deleted_list.append(stock_industry)
        else:
            #If error occured
            error_list.append(stock_industry)
            return jsonify(
                {
                    "code": 404,
                    "data": {
                        "accid": accid,
                        "stock_industry": stock_industry
                    },
                    "message": "Stock preference not found."
                }
            ), 404
    #If successfully deleted
    if len(deleted_list):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "accid": accid,
                    "stock_industry": deleted_list
                },
                "message": "Stock preference successfully deleted."
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

@app.errorhandler(400) 
def invalid_route(e): 
    return jsonify(
        {
            "code": 400,
            "message": "Bad Request."
        }
    ), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)