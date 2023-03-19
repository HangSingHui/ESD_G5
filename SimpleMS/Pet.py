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
    name = db.Column(db.String(50))
    
    #Putting foreign key on pet, creating new column owner.id in pet database automatically
    owner_id=db.Column(db.Integer, db.ForeignKey('owner.id'))

