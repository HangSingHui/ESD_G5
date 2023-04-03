from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_cors import CORS
from os import environ

# from __future__ import annotations


app = Flask(__name__)
# # app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
# # #"mysql+mysqlconnector://root:root@localhost:3306/pet
# # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db = SQLAlchemy(app)
# CORS(app)

import pymongo

from bson.objectid import ObjectId

client = pymongo.MongoClient("mongodb+srv://jxyong2021:Rypc9koQlPRa0KgC@esdg5.juoh9qe.mongodb.net/?retryWrites=true&w=majority")
pet_db = client.get_database('pet_db')
pet_col = pet_db['pet']
for pet in pet_col.find():
    print(pet)


#Function 1: Get all pets that belongs to a specific owner #owner id is sent + adding a new pet (POST)
@app.route("/pets/<string:id>",methods=["GET, POST"])
def get_jobTitle(id):
    if request.method=="GET":
    #search if job exists first with jobID
        query={"OwnerID":ObjectId(id)}
        petList = pet_col.find(query)

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



if __name__ == "__main__":
    app.run(port=5005, debug=True)