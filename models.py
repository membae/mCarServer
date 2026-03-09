from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime

metadata = MetaData()

db = SQLAlchemy(metadata=metadata)

class User(db.Model, SerializerMixin):
    __tablename__='users'
    
    id=db.Column(db.Integer, primary_key=True)
    first_name=db.Column(db.String, nullable=False)
    last_name=db.Column(db.String, nullable=False)
    email=db.Column(db.String, unique=True, nullable=False)
    phone=db.Column(db.String, nullable=False)
    password=db.Column(db.String, nullable=False)
    role=db.Column(db.String, default='buyer')
    location=db.Column(db.String, default='Nairobi')
    is_verified=db.Column(db.Boolean, default=False)
    created_at=db.Column(db.DateTime, default=datetime.utcnow)
    
    mechanic=db.relationship('Mechanic', back_populates='user', cascade="all, delete_orphan")
    garages=db.relationship('Garage', back_populates='owner',cascade='all,delete_orphan')
    

class Mechanic(db.Model, SerializerMixin):
    __tablename__='mechanics'
    
    id=db.Column(db.Integer, primary_key=True)
    specialization=db.Column(db.String)
    hourly_rate=db.Column(db.Integer)
    rating=db.Column(db.Float,default=0)
    
    user_id=db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    garage_id=db.Column(db.Integer, db.ForeignKey('garages.id'),)
    
    user=db.relationship('User', back_populates='mechanic')
    services=db.relationship('Service', back_populates='mechanic',cascade="all, delete_orphan")
    garage=db.relationship('Garage',back_populates='mechanics')
    
class Service(db.Model, SerializerMixin):
    __tablename__='services'
    
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String, nullable=False)
    description=db.Column(db.Text)
    price=db.Column(db.Integer)
    
    mechanic_id=db.Column(db.Integer, db.ForeignKey('mechanics.id'))
    garage_id=db.Column(db.Integer, db.ForeignKey('garages.id'))
    
    mechanic=db.relationship('Mechanic', back_populates='services')
    garage=db.relationship('Garage', back_populates='services')
    
    

class Garage(db.Model,SerializerMixin):
    
    __tablename__='garages'
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String, nullable=False)
    location=db.Column(db.String, nullable=False)
    rating=db.Column(db.Float, default=0)
    created_at=db.Column(db.DateTime, default=datetime.utcnow)
    
    owner_id=db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    owner=db.relationship('User', back_populates='garages')
    mechanics=db.relationship('Mechanic', back_populates='garage')
    services=db.relationship('Service', back_populates='garage', cascade='all, delete_orphan')
    