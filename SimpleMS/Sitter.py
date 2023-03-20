from flask import Flask, request, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
#"mysql+mysqlconnector://root:root@localhost:3306/sitter
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)

class Sitter(db.Model):
    __tablename__ = 'sitter'

    id = db.Column(db.Integer, primary_key =True)
    name = db.Column(db.String(50), nullable=False)
    phoneNum = db.Column(db.String(8), nullable = False)
    postal = db.Column(db.String(7), nullable = False)
    cardInfo = db.Column(db.String(20), nullable = False)
    outstanding_charges = db.Column(db.Float(precision=2), nullable=False)
    is_blocked = db.Column(db.Boolean, nullable = False)
    species_preference = db.Column(db.String(50), nullable = False)
    region_preference = db.Column(db.String(50), nullable = False)
    skills = db.Column(db.String(50), nullable = False)
    hourly_rate = db.Column(db.Float(precision=2), nullable=False)
    #stripe_details = db.Column(db.String(50), nullable = False)


    def __init__(self, id, name, phoneNum, postal, cardInfo, outstanding_charges, is_blocked, species_preference, region_preference, skills, hourly_rate):
        self.id = id
        self.name = name
        self.phoneNum = phoneNum
        self.postal = postal
        self.cardInfo = cardInfo
        self.outstanding_charges = outstanding_charges
        self.is_blocked = is_blocked
        self.species_preference = species_preference
        self.region_preference = region_preference
        self.skills = skills
        self.hourly_rate = hourly_rate

    def json(self):
        return {
            "id": self.id, 
            "name": self.name, 
            "phoneNum": self.phoneNum, 
            "postal": self.postal,
            "cardInfo": self.cardInfo,
            "outstanding_charges": self.outstanding_charges,
            "is_blocked": self.is_blocked,
            "species_preference": self.species_preference,
            "region_preference": self.region_preference,
            "skills": self.skills,
            "hourly_rate": self.hourly_rate
        }


# Function 1: display ALL sitters
@app.route("/sitter")
def get_all():
    sitterList = Sitter.query.all()
    if len(sitterList):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "sitters": [sitter.json() for sitter in sitterList]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no sitters."
        }
    ), 404



# Function 2: display sitter info by ID
@app.route("/sitter/<integer:id>")
def find_by_id(id):
    sitter = Sitter.query.filter_by(id=id).first()
    if sitter:
        return jsonify(
            {
                "code": 200,
                "data": sitter.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Sitter not found."
        }
    ), 404



# Function 3: create new sitter
@app.route("/sitter/<integer:id>", methods=['POST'])
def create_sitter(id):
    if (Sitter.query.filter_by(id=id).first()):
        return jsonify(
            {
                "code": 400,
                "data": {
                    "id": id
                },
                "message": "Sitter already exists."
            }
        ), 400

    data = request.get_json()
    sitter = Sitter(id, **data)

    try:
        db.session.add(sitter)
        db.session.commit()
    except:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "id": id
                },
                "message": "An error occurred creating the sitter."
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "data": sitter.json()
        }
    ), 201


# Function 4: update sitter details
@app.route("/sitter/<integer:id>", methods=['PUT'])
def update_sitter(id):

    #delete old sitter
    old_sitter = Sitter.query.filter_by(id=id).first()
    db.session.delete(old_sitter)
    db.session.commit()

    #Get new data
    data = request.get_json()
    new_sitter = Sitter(id, **data)

    try:
        db.session.add(new_sitter)
        db.session.commit()
    
    except:
        return jsonify(
        {
            "code":500,
            "message": "sitter failed to update"
        }
     ),500   

    return jsonify(
        {
            "code":201,
            "data": new_sitter.json()
        }
    ),201



# Function 5: delete sitter
@app.route("/sitter/<integer:id>", methods=['DELETE'])
def delete_owner(id):
    sitter = Sitter.query.filter_by(id = id).first()
    if (sitter):
        db.session.delete(sitter)
        db.session.commit()
        return(
            {
                "code":201,
                "id": id
            }
        ),201
    
    return(
        {
            "code":404, 
            "data":{
                "sitter": sitter
            },
            "message": "sitter not found"
        }
    ),404




if __name__ == '__main__':
    # app.run(port=5001, debug=True)
    app.run(host='0.0.0.0', port=5001, debug=True)
