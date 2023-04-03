from flask import Flask, request, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ
from bson.json_util import dumps
from bson.objectid import ObjectId
import json



app = Flask(__name__)
#"mysql+mysqlconnector://root:root@localhost:3306/sitter
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)

import pymongo

client = pymongo.MongoClient("mongodb+srv://jxyong2021:Rypc9koQlPRa0KgC@esdg5.juoh9qe.mongodb.net/?retryWrites=true&w=majority")
pet_sitter_db = client.get_database("pet_sitter_db")
pet_sitter_col = pet_sitter_db['pet_sitter']


# Function 1: display ALL sitters
@app.route("/sitter")
def get_all():
    sitterList = pet_sitter_col.find()
    len_sitters = pet_sitter_db.pet_sitter.count_documents({})

    if len_sitters > 0:
        list_sitterList = list(sitterList)
        json_data = dumps(list_sitterList)
        json_data = json.loads(json_data)
        return jsonify(
            {
                "code":200, 
                "data": json_data
            }
        )
    
    return jsonify(
        {
            "code": 404,
            "message": "There are no existing sitters."
        }
    ), 404



# Function 2: display sitter info by ID
@app.route("/sitter/<string:id>")
def find_by_id(id):
    query={"_id":ObjectId(id)}
    sitter=pet_sitter_col.find(query)
    num_sitter = pet_sitter_db.pet_sitter.count_documents({})
    
    if num_sitter > 0:
        sitter = list(sitter)
        json_data = dumps(sitter)
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
            "message": "Sitter not found."
        }
    ), 404

'''
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
'''

'''
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
'''

'''
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
'''
# # Function 6: recommend replacement sitters
# @app.route("/replacement_sitter/<integer:jobId>", methods=['GET'])
# def find_replacements(jobId):
#     replacementlist = Sitter.query.filter_by(id = id).first()




if __name__ == '__main__':
    # app.run(port=5001, debug=True)
    app.run(host='0.0.0.0', port=5001, debug=True)
