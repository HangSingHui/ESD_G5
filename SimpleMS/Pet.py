from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_cors import CORS
from os import environ

# from __future__ import annotations
from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship

from SimpleMS.Owner import Owner #not too sure about this part and the foreign key part, can change once the data is added if it doesn't work

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
#"mysql+mysqlconnector://root:root@localhost:3306/pet
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)

class Pet(db.Model):
    __tablename__ = 'pet'

    id= db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    species=db.Column(db.String(50), nullable=False)
    breed=db.Column(db.String(50), nullable=False)
    desc=db.Column(db.Text, nullable=False)
    med_needs=db.Column(db.Text, nullable=True)

    #Putting foreign key on pet, creating new column owner.id in pet database automatically
    owner_id=db.Column(db.Integer, db.ForeignKey('owner.id'))

    def __init__(self, id, name, species, breed, desc, med_needs,owner_id):
        self.id = id
        self.name=name
        self.species=species
        self.breed=breed
        self.desc=desc
        self.med_needs=med_needs
        self.owner_id=owner_id
    
    def json(self):
        return {
            "id":self.id,
            "name":self.name,
            "species":self.species,
            "breed":self.breed,
            "desc":self.desc,
            "med_needs":self.med_needs,
            "owner_id":self.owner_id
        }

#Function 1: Get all pets that belongs to a specific owner #owner id is sent + adding a new pet (POST)
@app.route("/pets/<integer:id>",methods=["GET, POST"])
def get_jobTitle(id):
    if request.method=="GET":
    #search if job exists first with jobID
        petList=job.query.filter_by(owner_id=id)

        if len(petList>0):
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