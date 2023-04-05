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
    num_sitter = pet_sitter_db.pet_sitter.count_documents(query)
    print(num_sitter)
    if num_sitter > 0:
        sitter = list(sitter)
        json_data = dumps(sitter)
        json_data = json.loads(json_data)
        print(json_data)
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

# Function 3: retrieve card info by sitter ID
@app.route('/sitter/payment-info/<string:sitter_id>')
def get_payment_info(sitter_id):
    query={"_id":ObjectId(sitter_id)}
    sitter_doc = pet_sitter_col.find_one(query)
    if sitter_doc is None:
        return{
            "code": 404,
            "message": "There is no pet sitter with the sitter id: " + sitter_id
        },404

    payment_info = dumps({'customer': sitter_doc['Stripe_Id'],
                          'card_id': sitter_doc['CardInfo']
                        })
    payment_info = json.loads(payment_info)
    return jsonify(
        {"code":200,
        "data": payment_info
        })

# Function 4: change (Reduce) rating of sitter
@app.route('/sitter/rating/<string:sitter_id>', methods=['GET', 'PUT'])
def update_rating(sitter_id):
    # find sitter by id
    query={"_id":ObjectId(sitter_id)}
    sitter_doc = pet_sitter_col.find_one(query)
    # check if sitter exists
    if sitter_doc is None:
        return{
            "code": 404,
            "message": "There is no pet sitter with the sitter id: " + sitter_id
        },404

    newScore = {"$inc" : {'User_score' : -50}}

    try:
        pet_sitter_col.update_one(query,newScore)
        return jsonify(
            {
                "code":200, 
                "data": "50 points deducted from Pet Sitter User_score"
            }
        )

    except:
        return jsonify(
        {
            "code":500, #internal error
            "message": "Internal error. Sitter.py failed to deduct 50 points from pet sitter."
        }
     ),500   
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

# Function 7: retrieve sitter pet preference 
@app.route("/sitter/<string:species>/<string:rate_cat>", methods=['GET'])
def retrieve_sitters(species, rate_cat):
    # once new job is created, pass in the species and hourly rate of that job
    # find sitter by species and rate 
    # output should contain a json object of all the emails of the sitters 

    # cannot query rate directly -> must check range :(())
    # 31-40
    # 41-50 
    # 51-60
    # print(species)
    # print(rate_cat)
    if rate_cat=="cat1": 
        # query range 31-40
        # sitter = pet_sitter_col.find({ "species":ObjectId(species), Hourly_rate : { $gt :  30, $lt : 41}})
        query = {
            "$and": [
                {"Species_preference": species},
                {"Hourly_rate": {"$gte": 30, "$lte":40}}
            ]
            }
    elif rate_cat=="cat2": 
        # query range 41-50 
        query = {
            "$and": [
                {"Species_preference": species},
                {"Hourly_rate": {"$gt": 40, "$lte":50}}
            ]
            }
    else:
        # query range 51-60
       query = {
            "$and": [
                {"Species_preference": species},
                {"Hourly_rate": {"$gt": 50, "$lte":60}}
            ]
            }

    sitter_doc = pet_sitter_col.find(query)
    len_sitter = pet_sitter_db.pet_sitter.count_documents(query)
    # print(len_sitter)

    email_list=[]
    if len_sitter > 0:
        for sitter in sitter_doc:
            email_list.append(sitter["Email"])
        return jsonify(
            {"code":200,
            "emails": email_list
        })

    return{
        "code": 404,
        "message": "No sitters with that preference"
    },404
        





if __name__ == '__main__':
    # app.run(port=5001, debug=True)
    app.run(host='0.0.0.0', port=5001, debug=True)
