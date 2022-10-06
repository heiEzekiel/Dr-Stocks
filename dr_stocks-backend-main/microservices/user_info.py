import os, re
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL') or 'mysql+mysqlconnector://root@localhost:3306/userDB'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

CORS(app)

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'
    accid = db.Column(db.Integer, primary_key=True, nullable=False)
    trade_accid = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    birthdate = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    apikey = db.Column(db.String(100), nullable=False)
    def __init__(self, accid, trade_accid, name, birthdate, email, password, apikey):
        self.accid = accid
        self.trade_accid = trade_accid
        self.name = name
        self.birthdate = birthdate
        self.email = email
        self.password = password
        self.apikey = apikey

    def json(self):
        return  {
            "accid": self.accid, 
            "trade_accid": self.trade_accid, 
            "name": self.name, 
            "birthdate": self.birthdate,
            "email": self.email,
            "password": self.password,
            "apikey": self.apikey
        }

@app.route("/account/login")
def login():
    head_email = str(request.args.get('email'))
    head_password = str(request.args.get('password'))
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if(not re.fullmatch(regex, head_email)) or (head_email.isspace()):
        return jsonify(
        {
            "code": 404,
            "message": "Invalid email address."
        }
    ), 404
    user = User.query.filter_by(email=head_email).first()
    if user:
        if user.password == head_password:
            return jsonify(
                {
                    "code": 200,
                    "data": user.json()
                }
            )
        return jsonify(
            {
                "code": 404,
                "message": "Invalid password."
            }
        ), 404
    else:
        return jsonify(
            {
                "code": 404,
                "message": "User not found."
            }
        ), 404

@app.route("/account/email/<string:email>")
def find_by_email(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if(not re.fullmatch(regex, email)) or (email.isspace()):
        return jsonify(
        {
            "code": 404,
            "message": "Invalid email address."
        }
    ), 404
    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify(
            {
                "code": 200,
                "data": user.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "User not found."
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
    app.run(host='0.0.0.0', port=5006, debug=True)