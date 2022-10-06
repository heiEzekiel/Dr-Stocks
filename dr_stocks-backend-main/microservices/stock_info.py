import finnhub, base64, os
from flask import Flask, request, jsonify
from flask_cors import CORS
from os import environ

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL') or 'mysql+mysqlconnector://root@localhost:3306/stock_infoDB'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}
CORS(app)

#GET Stock Info
@app.route("/stock_info/<string:stock_symbol>")
def get_stock_info(stock_symbol):
    stock_symbol = str(stock_symbol).upper()
    if (len(stock_symbol) > 5):
        return jsonify(
            {
                "code": 404,
                "message": "Invalid stock symbol."
            }
        ), 404
    text = "YzhtNWZrYWFkM2k5aHVjcDk4NzA="
    msg = base64.b64decode(text)
    key = str(msg.decode('ascii'))
    finnhub_client = finnhub.Client(api_key=key)
    if finnhub_client.quote(stock_symbol)["d"] != None:
        return {
            "code" : 200,
            "data" : finnhub_client.quote(stock_symbol)
        }
    elif finnhub_client.quote(stock_symbol)["d"] == None:   
        return {
            "code" : 404,
            "message" : "Invalid stock symbol."
        }
    else: 
        return {
            "code" : 500,
            "message" : "Unexpected error has occurred. Please try again later"
        }
    
#GET Company Info
@app.route("/stock_info/profile2/<string:stock_symbol>")
def get_company_info(stock_symbol):
    stock_symbol = str(stock_symbol).upper()
    if (len(stock_symbol) > 5):
        return jsonify(
            {
                "code": 404,
                "message": "Invalid stock symbol.",
                "temp":stock_symbol
            }
        ), 404
    text = "YzhtNWZrYWFkM2k5aHVjcDk4NzA="
    msg = base64.b64decode(text)
    key = str(msg.decode('ascii'))
    finnhub_client = finnhub.Client(api_key=key)
    if len(finnhub_client.company_profile2(symbol=stock_symbol)) <= 0:
        return {
            "code" : 404,
            "message" : "Invalid stock symbol."
        }
    if len(finnhub_client.company_profile2(symbol=stock_symbol)) > 0:
        return {
            "code" : 200,
            "data" : finnhub_client.company_profile2(symbol=stock_symbol)
        }
    else: 
        return {
            "code" : 500,
            "message" : "Unexpected error has occurred. Please try again later"
        }

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
    app.run(host='0.0.0.0', port=5001, debug=True)