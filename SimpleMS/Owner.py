from flask import Flask, jsonify, request
# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy.orm import relationship
# from flask_cors import CORS
# from os import environ

# from SimpleMS.Pet import Pet 
#not too sure about this part and the foreign key part, can change once the data is added if it doesn't work

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
# #"mysql+mysqlconnector://root:root@localhost:3306/owner
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db = SQLAlchemy(app)
# CORS(app)

# class Owner(db.Model):
#     __tablename__ = 'owner'

#     id = db.Column(db.Integer, primary_key =True)
#     name = db.Column(db.String(50), nullable=False)
#     phoneNum = db.Column(db.String(8), nullable = False)
#     postal = db.Column(db.String(7), nullable = False)
#     cardInfo = db.Column(db.String(20), nullable = False)

#     #Owner is PARENT to Pet (one to many)
#     pets=db.relationship('Pet',backref='owner')

#     #Owner is PARENT to Job (one to many)
#     jobs=db.relationship('Job',backref='owner')


#     def __init__(self, id, ownerName, phoneNum, postal, cardInfo, pets):
#         self.id = id
#         self.ownerName = ownerName
#         self.phoneNum = phoneNum
#         self.postal = postal
#         self.pets = pets
#         self.cardInfo=cardInfo

    
#     def json(self):
#         return {
#             "id": self.id,
#             'ownerName': self.ownerName,
#             "phoneNum": self.phoneNum,
#             "postal": self.postal,
#             "pets":self.pets,
#             "cardInfo":self.cardInfo
#         }

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




if __name__ == "__main__":
    app.run(port=5000, debug=True)
