import os, sys, requests, amqp_setup, pika, json
from flask import Flask, request, jsonify
from flask_cors import CORS
from os import environ
from invokes import invoke_http

app = Flask(__name__)
CORS(app)

user_info_URL = environ.get('user_info_URL') or "http://localhost:5006/account"
trading_acc_URL = environ.get('trading_acc_URL') or "http://localhost:5004/trading_acc"
stock_info_URL = environ.get('stock_info_URL') or "http://localhost:5001/stock_info"
user_stock_URL = environ.get('user_stock_URL') or "http://localhost:5007/user_stock/buy"

@app.route("/place_trade", methods=['POST'])
def place_trade():
    head_apikey = request.args.get('apikey')
    trequest = request.get_json(force=True)
    # trequest = json.loads(request.get_data())
    # Simple check of input format and data of the request are JSON
    # if trequest.is_json:
    try:
        trade = trequest #.get_json()
        print("\nReceived an order in JSON: ", trade)

        # do the actual work
        # 1. Send trade info
        result = processPlaceTrade(trade, head_apikey)
        return jsonify(result), result["code"]

    except Exception as e:
        # Unexpected error in code
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
        print(ex_str)

        return jsonify({
            "code": 500,
            "message": "place_trade.py internal error: " + ex_str
        }), 500

def processPlaceTrade(trade, head_apikey):
    # 2.Retrieve trade_accid
    # Inoke the user_info microservice
    print('\n-----Invoking user_info microservice-----')
    new_user_info_URL = user_info_URL + '/email/' + trade["email"]
    user_info = invoke_http(new_user_info_URL, method='GET', headers={'apikey': head_apikey})
    print('user_info', user_info)
    
    code = user_info["code"]
    if code not in range(200,300):
        #4. Send error message to error microservice
        #Inform the error microservice
        print('\n\n-----Publishing the (user error) message with routing_key=user.error-----')
        user_error_message = json.dumps(user_info)
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="user.error", 
            body=user_error_message, properties=pika.BasicProperties(delivery_mode = 2)) 
        # make message persistent within the matching queues until it is received by some receiver 
        # (the matching queues have to exist and be durable and bound to the exchange)
        # delivery_mode = 2: make message persistent within the matching queues until it is received by some receiver

        # 9. Return error
        return {
            "code": 500,
            "data": {"user_info": user_info},
            "message": "User not found and sent for error handling."
        }
    
    # 3. Retrieve stock price
    # Invoke the stock_info microservice
    print('\n-----Invoking stock_info microservice-----')
    new_stock_info_URL = stock_info_URL +  "/" + trade["stock_symbol"] 
    stock_info = invoke_http(new_stock_info_URL, method='GET')
    print('stock_info', stock_info)

    code = stock_info["code"]
    if code not in range(200,300):
        print('\n\n-----Publishing the (user error) message with routing_key=stock_info.error-----')
        stock_info_error_message = json.dumps(stock_info)
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="stock_info.error", 
            body=stock_info_error_message, properties=pika.BasicProperties(delivery_mode = 2)) 
        # make message persistent within the matching queues until it is received by some receiver 
        # (the matching queues have to exist and be durable and bound to the exchange)
        # delivery_mode = 2: make message persistent within the matching queues until it is received by some receiver

        # 9. Return error
        return {
            "code": 500,
            "data": {"stock_info": stock_info},
            "message": "Stock information not found and sent for error handling."
        }
    # 4. Update trade balance if sufficient
    # Invoke the trading_acc microservice
    print('\n\n-----Invoking trading_acc microservice-----')
    new_trade_acc_URL = trading_acc_URL + '/minus/' + str(user_info["data"]["accid"])
    trade_balance_result = invoke_http(new_trade_acc_URL, method='PUT', json= [stock_info, user_info, trade])
    print('trade_balance_result' , trade_balance_result)

    # Check the trade balance result; if a failure, send it to error microservice
    code = trade_balance_result["code"]
    if code not in range(200, 300):
        trade_log_message = json.dumps([trade_balance_result, trade, stock_info])
        print('\n\n-----Publishing the (trade_log) message with routing_key = trade_log.trade-----')
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="trade_log.trade", body=trade_log_message, properties=pika.BasicProperties(delivery_mode = 2))
        print("\nTrade status ({:d}) published to the RabbitMQ Exchange:".format(
            code), trade_balance_result)
        
        error_message = json.dumps(trade_balance_result)
        print('\n\n-----Publishing the (order error) message with routing_key=trade_balance.error-----')
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="trade_balance.error", body=error_message, properties=pika.BasicProperties(delivery_mode = 2))
        # - reply from the invocation is not used; 
        # continue even if this invocation fails
        print("\nTrade status ({:d}) published to the RabbitMQ Exchange:".format(
            code), trade_balance_result)

        # Return error
        return {
            "code": 500,
            "data": {"trade_balance_result": trade_balance_result},
            "message": "Trade creation failure sent for error handling."
        }
    
    print('\n-----Invoking user_stock microservice-----')
    new_user_stock_URL = user_stock_URL + '/' + str(user_info["data"]["accid"])
    user_stock_result = invoke_http(new_user_stock_URL, method='POST', json= [stock_info, user_info, trade])
    print('user_stock_result' , user_stock_result)
    code = user_stock_result["code"]
    # 5. Record trade activity
    # Invoke the trade_log microservice
    # print('\n\n-----Invoking trade_log microservice-----')
    # new_trade_log_URL = trade_log_URL + '/' + str(user_info["data"]["accid"])
    # trade_log_result = invoke_http(new_trade_log_URL, method='POST', json=[user_info, stock_info, trade])
    # print('trade_log_result' , trade_log_result)
    
    # code = trade_log_result["code"]
    # message = json.dumps(trade_balance_result)
    if code not in range(200, 300):
        # deposit balance back into trading account
        print('\n-----Invoking trading account microservice-----')
        deposit = {
            "amount" : round(stock_info["data"]["c"] * trade["stock_quantity"], 2)
        }
        new_trade_acc_URL = trading_acc_URL + '/plus/' + str(user_info["data"]["accid"])
        deposit_result = invoke_http(new_trade_acc_URL, method='PUT',json= [user_info, deposit])
        print('deposit_result:', deposit_result)

        trade_log_message = json.dumps([trade_balance_result, trade, stock_info])
        print('\n\n-----Publishing the (trade_log) message with routing_key = trade_log.trade-----')
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="trade_log.trade", body=trade_log_message, properties=pika.BasicProperties(delivery_mode = 2))
        print("\nTrade status ({:d}) published to the RabbitMQ Exchange:".format(
            code), trade_balance_result)

        error_message = json.dumps(trade_balance_result)
        print('\n\n-----Publishing the (order error) message with routing_key=order.error-----')
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="trade_log.error", body=error_message, properties=pika.BasicProperties(delivery_mode = 2))
        # - reply from the invocation is not used; 
        # continue even if this invocation fails
        print("\nOrder status ({:d}) published to the RabbitMQ Exchange:".format(
            code), trade_balance_result)

        # Return error
        return {
            "code": 500,
            "data": {"trade_balance_result": trade_balance_result},
            "message": "Trade creation failure sent for error handling."
        }

    
    print('\n\n-----Publishing the (trade_log) message with routing_key = trade_log.trade-----')
    trade_log_message = json.dumps([trade_balance_result, trade, stock_info])
    amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="trade_log.trade", body=trade_log_message, properties=pika.BasicProperties(delivery_mode = 2))
    print("\nTrade status ({:d}) published to the RabbitMQ Exchange:".format(
        code), trade_balance_result)
    #6. Send trade confirmation
    # Invoke email_notification microservice
    print('\n\n-----Publishing the (email) message with routing_key=email.log-----') 
    # invoke_http(email_notification_URL, method='POST',json=deposit_log)           
    email_log_message = json.dumps([user_stock_result, trade])
    amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="email.log", 
        body=email_log_message)
    print("\nDeposit action performed and notified user.\n")
    
    return {
        "code": 201,
        "data" : {
            "stock_info" : stock_info,
            "trade_balance_result" : trade_balance_result,
            "user_stock_result" : user_stock_result
        }
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

@app.errorhandler(400) 
def invalid_route(e): 
    return jsonify(
        {
            "code": 400,
            "message": "Invalid JSON input"
        }
    ), 400

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
    print("This is flask " + os.path.basename(__file__) + " for placing an trade...")
    app.run(host="0.0.0.0", port=5100, debug=True)
