from flask import Flask, jsonify, request

from flask_cors import CORS
from os import environ

app = Flask(__name__)

import pymongo

from bson.objectid import ObjectId

client = pymongo.MongoClient("mongodb+srv://jxyong2021:Rypc9koQlPRa0KgC@esdg5.juoh9qe.mongodb.net/?retryWrites=true&w=majority")
owner_db = client.get_database("pet_owner_db")
owner_col = owner_db['pet_owner']


#Function 1: Get all owners - to display on the interface
@app.route("/owner")
def get_all():
    ownerList = owner_col.find()

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


#Function 2: Get owner by id
@app.route("/owner/<string:id>")
def get_payment_details(id):
    #search if owner exists first with id
    query={"_id":ObjectId(id)}
    owner=owner_col.find_one(query)

    if owner:
        return jsonify(
            {
                "code":200,
                "data":owner.json()
            
            }
        )

     #if not, return owner not found

    return jsonify(
            {
                "code":404,
                "data":"Owner not found."
            }
        ),404







if __name__ == "__main__":
    app.run(port=5000, debug=True)
