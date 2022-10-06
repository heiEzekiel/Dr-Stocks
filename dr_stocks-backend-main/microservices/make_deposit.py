import os, sys, amqp_setup, pika, json, requests
from os import environ
from flask import Flask, request, jsonify
from flask_cors import CORS
from invokes import invoke_http

app = Flask(__name__)
CORS(app)

trading_acc_URL = environ.get('trading_acc_URL') or "http://localhost:5004/trading_acc/plus"
user_info_URL = environ.get('user_info_URL') or "http://localhost:5006/account/email"

@app.route("/make_deposit", methods=['POST'])
def make_deposit():
    head_apikey = request.args.get('apikey')
    trequest = request.get_json(force=True)
    # Simple check of input format and data of the request are JSON
    try:
        deposit = trequest
        print("\nReceived an deposit in JSON:", deposit)

        # do the actual work
        # 2. Accept Deposit amount
        result = processDeposit(deposit, head_apikey)
        return jsonify(result), result["code"]

    except Exception as e:
        # Unexpected error in code
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
        print(ex_str)

        return jsonify({
            "code": 500,
            "message": "make_deposit.py internal error: " + ex_str
        }), 500


def processDeposit(deposit, head_apikey):
    # 3. Retrieve the amount trader has 
    # Invoke the user info microservice
    print('\n-----Invoking user_info microservice-----')
    new_user_info_URL = user_info_URL + '/' + deposit["email"]
    user_info = invoke_http(new_user_info_URL, method='GET', headers={'apikey': head_apikey})
    print("user_info", user_info)

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

    # 5. Update amount deposited 
    # Invoke trading account microservice
    print('\n-----Invoking trading account microservice-----')
    new_trading_acc_URL = trading_acc_URL + '/' + str(user_info["data"]["accid"])
    deposit_result = invoke_http(new_trading_acc_URL, method='PUT',json= [user_info, deposit])
    print('deposit_result:', deposit_result)

    # Check the deposit result; if a failure, send it to the error microservice.
    code = deposit_result["code"]
    print("hello", code)
    # deposit_log_message = json.dumps([deposit_result, deposit])
    if code not in range(200,300):
        # Inform the error microservice
        #print('\n\n-----Invoking error microservice as order fails-----')
        print('\n\n-----Publishing the (deposit error) message with routing_key=deposit.error-----')
        # invoke_http(error_URL, method="POST", json=deposit_result)
        deposit_error_message = json.dumps(deposit_result)
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="deposit.error", 
            body= deposit_error_message, properties=pika.BasicProperties(delivery_mode = 2)) 
        # make message persistent within the matching queues until it is received by some receiver 
        # (the matching queues have to exist and be durable and bound to the exchange)

        # - reply from the invocation is not used;
        # continue even if this invocation fails        
        # print("\nDeposit status ({:d}) published to the RabbitMQ Exchange:".format(
            # code), deposit_result)

        deposit_failure_message = json.dumps([deposit_result, deposit])
        print('hello',deposit_failure_message)
        # 7. Sent amount deposited
        # Invoke transaction log microservice
        # print('\n\n-----Publishing the (deposit.transaction) message with routing_key=deposit.transaction-----') 
        # new_transaction_log_URL = transaction_log_URL + "/" + str(user_info["data"]["accID"])
        # invoke_http(new_transaction_log_URL, method='POST',json=deposit_log)
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="deposit.failure.transaction", 
                body=deposit_failure_message)
        print("\nDeposit transaction published to transaction log\n")

        # 9. Return error
        return {
            "code": 500,
            "data": {"deposit_log": deposit_result},
            "message": "Deposit action failure sent for error handling."
        }

    else:
        deposit_success_message = json.dumps([deposit_result, deposit])
        # 7. Sent amount deposited
        # Invoke transaction log microservice
        # print('\n\n-----Publishing the (deposit.transaction) message with routing_key=deposit.transaction-----') 
        # new_transaction_log_URL = transaction_log_URL + "/" + str(user_info["data"]["accID"])
        # invoke_http(new_transaction_log_URL, method='POST',json=deposit_log)
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="deposit.success.transaction", 
                body=deposit_success_message)
        print("\nDeposit transaction published to transaction log\n")

    # 8. Notify trader
    # Invoke email notification microservice
    print('\n\n-----Publishing the (email) message with routing_key=email.log-----') 
    # invoke_http(email_notification_URL, method='POST',json=deposit_log)           
    email_log_message = json.dumps([deposit_result, deposit])
    amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="email.log", 
        body=email_log_message)
    print("\nDeposit action performed and notified user.\n")

    # - reply from the invocation is not used;
    # continue even if this invocation fails
    # 9. Return confirmation of deposit
    return {
        "code": 201,
        "data": {"deposit_log": deposit_result}
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
    print("This is flask " + os.path.basename(__file__) + " for placing a deposit...")
    app.run(host="0.0.0.0", port=5101, debug=True)