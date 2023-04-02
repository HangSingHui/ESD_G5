from flask import Flask, jsonify, request

from flask_cors import CORS
from os import environ

# from SimpleMS.Pet import Pet 
#not too sure about this part and the foreign key part, can change once the data is added if it doesn't work

app = Flask(__name__)

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


#Function 2: Get owner
@app.route("/owner/<integer:id>")
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
