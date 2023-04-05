from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_cors import CORS
from os import environ
from bson.json_util import dumps
from bson.objectid import ObjectId
import json

# from __future__ import annotations


app = Flask(__name__)
# # app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
# # #"mysql+mysqlconnector://root:root@localhost:3306/pet
# # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db = SQLAlchemy(app)
CORS(app)

import pymongo

from bson.objectid import ObjectId

client = pymongo.MongoClient("mongodb+srv://jxyong2021:Rypc9koQlPRa0KgC@esdg5.juoh9qe.mongodb.net/?retryWrites=true&w=majority")
pet_db = client.get_database('pet_db')
pet_col = pet_db['pet']



#Function 1: Get all pets that belongs to a specific owner #owner id is sent + adding a new pet (POST)
@app.route("/pets/<string:id>")
def get_pets(id):

    #search if job first exists
    query = {'OwnerID': ObjectId(id)}
    pets = pet_col.find(query)
    num_pets = pet_db.pet.count_documents(query)
    print(num_pets)
    
    if num_pets > 0:
        pets = list(pets)
        json_data = dumps(pets)
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
            "message": "There are no pets for the owners."
        }
    ), 404
    '''
    if request.method=="GET":
    #search if job exists first with jobID
        query={"OwnerID":ObjectId(id)}
        petList = pet_col.find(query)   
        print(petList)
        
        if petList:
            return jsonify(
                {
                    "code":200,
                    "data": [pet.json() for pet in petList]
                }
            )

        return jsonify(
                {
                    "code":404,
                    "data":"You have no existing pets."
                }
            ),404
            
    else:
        pass #do next time
    '''

#Function 2
@app.route("/pets/get_species/<string:id>")
def get_pet_species(id):

    #search if job first exists
    query = {'_id': ObjectId(id)}
    pets = pet_col.find(query)
    num_pets = pet_db.pet.count_documents(query)
    print(num_pets)
    
    if num_pets > 0:
        pets = list(pets)
        json_data = dumps(pets)
        json_data = json.loads(json_data)
        species = json_data[0]['Species'] 
        return jsonify(
            {
            "code": 200,
            "data": species
            }
        )
        '''
        species = print(json_data[0]['Species'])
        return species
        '''
    return jsonify(
        {
            "code": 404,
            "message": "Pet not found."
        }
    ), 404
        

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5007, debug=True)