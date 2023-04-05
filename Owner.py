from flask import Flask, jsonify, request

from flask_cors import CORS
from os import environ
from bson.json_util import dumps
app = Flask(__name__)
import json

import pymongo

from bson.objectid import ObjectId

client = pymongo.MongoClient("mongodb+srv://jxyong2021:Rypc9koQlPRa0KgC@esdg5.juoh9qe.mongodb.net/?retryWrites=true&w=majority")
owner_db = client.get_database("pet_owner_db")
owner_col = owner_db['pet_owner']


#Function 1: Get all owners - to display on the interface
@app.route("/owner")
def get_all():
    ownerList = owner_col.find()
    num_owners = owner_db.pet_owner.count_documents({})
    if num_owners > 0:
        list_ownerList = list(ownerList)
        json_data = dumps(list_ownerList)
        json_data = json.loads(json_data)
        return jsonify(
            {
            "code": 200,
            "data": json_data
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
def get_owner_by_id(id):
    #search if owner exists first with id
        #search if job exists first with jobID
    query={"_id":ObjectId(id)}
    #job=job_col.find(query)
    num_owner = owner_db.pet_owner.count_documents(query)
    owner = owner_col.find(query)
    if num_owner > 0:
        owner = list(owner)
        json_data = dumps(owner)
        json_data = json.loads(json_data)
    
        return jsonify(
            {
                "code":200,
                "data": json_data
            }
        )
    #if not, return owner not found
    return jsonify(
            {
                "code":404,
                "message":"Owner not found."
            }
        ),404

# Function 3: Get email from owner
@app.route("/owner/email/<string:id>")
def get_email_by_id(id):
    #search if owner exists first with id
        #search if job exists first with jobID
    query={"_id":ObjectId(id)}
    owner = owner_col.find(query)
    if owner:
        json_data = json.loads(dumps(owner))
        email = json_data[0]['Email']
    
        return jsonify(
            {
                "code":200,
                "data": email
            }
        )
    #if not, return owner not found
    return jsonify(
            {
                "code":404,
                "message":"Owner not found."
            }
        ),404




if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
