from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_cors import CORS
from os import environ

from SimpleMS.Pet import Pet 
#not too sure about this part and the foreign key part, can change once the data is added if it doesn't work

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
#"mysql+mysqlconnector://root:root@localhost:3306/owner
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)

class Owner(db.Model):
    __tablename__ = 'owner'

    id = db.Column(db.Integer, primary_key =True)
    name = db.Column(db.String(50), nullable=False)
    phoneNum = db.Column(db.String(8), nullable = False)
    postal = db.Column(db.String(7), nullable = False)
    cardInfo = db.Column(db.String(20), nullable = False)

    #Owner is PARENT to Pet (one to many)
    pets=db.relationship('Pet',backref='owner')


    def __init__(self, id, ownerName, phoneNum, postal, cardInfo, pets):
        self.id = id
        self.ownerName = ownerName
        self.phoneNum = phoneNum
        self.postal = postal
        self.pets = pets
        self.cardInfo=cardInfo

    
    def json(self):
        return {
            "id": self.id,
            'ownerName': self.ownerName,
            "phoneNum": self.phoneNum,
            "postal": self.postal,
            "pets":self.pets,
            "cardInfo":self.cardInfo
        }

#Function 1: Get all owners - to display on the interface
@app.route("/owner")
def get_all():
    ownerList = Owner.query.all()

    if len(ownerList):
        return jsonify(
            {
                "code":200, 
                "data": [owner.json() for owner in ownerList]
            }
        )
    
    return jsonify(
        {
            "code": 404,
            "message": "There are no owners"
        }
    ), 404


#Function 2: Get owner payment details by id
@app.route("/owner/payment/<integer:id>")
def get_payment_details(id):
    #search if owner exists first with id
    owner=Owner.query.filter_by(id=id).first()

    if owner:
        return jsonify(
            {
                "code":200,
                "data":
                {
                    "cardInfo":owner.json().cardInfo,
                    "ownerNum":owner.json().phoneNum
                }
            
            }
        )

    return jsonify(
            {
                "code":404,
                "data":"Owner not found."
            }
        ),404


    #if not, return owner not found


#Function 3: Create a new owner

#Function 4: Update owner details


# @app.route("/owner/<string:id>")
# def find_by_id(id):
#     owner = owner.query.filter_by(isbn13=isbn13).first()
#     if (owner):
#         return jsonify(
#             {
#                 "code": 200,
#                 "data": owner.json()
#             }
#         )
    
#     return jsonify(
#         {
#             "code":404,
#             "message": "owner not found"
#         }
#     ),404


# @app.route("/owner/<string:isbn13>", methods=['POST'])
# def create_owner(isbn13):
#     if (owner.query.filter_by(isbn13=isbn13).first()):
#         return jsonify(
#             {
#                 "code": 400,
#                 "data": {
#                     "isbn13": "1234567890123"
#                 },
#                 "message": "owner already exists"
#             }
#         ),400
    
#     #get user input, where user input is request in JSON format
#     #get_json() converts user input to PYTHON DATA
#     data = request.get_json()
#     #Create instance of the owner
#     owner = owner(isbn13, **data)
   
#     try:
#         #add the owner 
#         db.session.add(owner)
#         #commit the changes
#         db.session.commit


#     except:
#         return jsonify(
#             {
#                 "code": 500,
#                 "data": {
#                     "isbn13": "1234567890123"
#                 },
#                 "message": "An error occured creating the owner."
#             }
#         ),500
    
#     return jsonify(
#         {
#             "code":201,
#             "data": owner.json()
#         }
#     ),201

# @app.route("/owner/<string:isbn13>", methods=['PUT'])
# def update_owner(isbn13):
#     #delete old owner
#     old_owner = owner.query.filter_by(isbn13=isbn13).first()
#     db.session.delete(old_owner)
#     db.session.commit()

#     #Get new data
#     data = request.get_json()
#     new_owner = owner(isbn13, **data)

#     try:
#         db.session.add(new_owner)
#         db.session.commit()
    
#     except:
#         return jsonify(
#         {
#             "code":500,
#             "message": "owner failed to update"
#         }
#      ),500   

#     return jsonify(
#         {
#             "code":201,
#             "data": new_owner.json()
#         }
#     ),201

# @app.route("/owner/<string:isbn13>", methods=['DELETE'])
# def delete_owner(isbn13):
#     owner = owner.query.filter_by(isbn13 = isbn13).first()
#     if (owner):
#         db.session.delete(owner)
#         db.session.commit()
#         return(
#             {
#                 "code":201,
#                 "isbn13": isbn13
#             }
#         ),201
    
#     return(
#         {
#             "code":404, 
#             "data":{
#                 "isbn13": isbn13
#             },
#             "message": "owner not found"
#         }
#     ),404


if __name__ == "__main__":
    app.run(port=5000, debug=True)
