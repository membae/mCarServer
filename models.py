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
    
    mechanic=db.relationship('Mechanic', back_populates='user', cascade="all, delete-orphan")
    garages=db.relationship('Garage', back_populates='owner',cascade='all,delete-orphan')
    cars=db.relationship('Car', back_populates='owner', cascade='all, delete-orphan')
    spareparts=db.relationship('Sparepart', back_populates='seller', cascade='all, delete-orphan')
    reviews=db.relationship('Review', back_populates='user', cascade='all, delete-orphan')
    
    serialize_rules=('-mechanic.user',)
    

class Mechanic(db.Model, SerializerMixin):
    __tablename__='mechanics'
    
    id=db.Column(db.Integer, primary_key=True)
    specialization=db.Column(db.String)
    hourly_rate=db.Column(db.Float)
    rating=db.Column(db.Float,default=0)
    
    user_id=db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    garage_id=db.Column(db.Integer, db.ForeignKey('garages.id'),)
    
    user=db.relationship('User', back_populates='mechanic')
    services=db.relationship('Service', back_populates='mechanic',cascade="all, delete-orphan")
    garage=db.relationship('Garage',back_populates='mechanics')
    
    serialize_rules=('-user.mechanic',)
    
class Service(db.Model, SerializerMixin):
    __tablename__='services'
    
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String, nullable=False)
    description=db.Column(db.Text)
    price=db.Column(db.Float)
    
    mechanic_id=db.Column(db.Integer, db.ForeignKey('mechanics.id'))
    garage_id=db.Column(db.Integer, db.ForeignKey('garages.id'))
    
    mechanic=db.relationship('Mechanic', back_populates='services')
    garage=db.relationship('Garage', back_populates='services')
    
    serialize_rules=('-mechanic.services',)
    
    

class Garage(db.Model,SerializerMixin):
    
    __tablename__='garages'
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String, nullable=False)
    location=db.Column(db.String, nullable=False)
    rating=db.Column(db.Float, default=0)
    created_at=db.Column(db.DateTime, default=datetime.utcnow)
    
    owner_id=db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    owner=db.relationship('User', back_populates='garages')
    mechanics=db.relationship('Mechanic', back_populates='garage', cascade='all, delete-orphan')
    services=db.relationship('Service', back_populates='garage', cascade='all, delete-orphan')
    spareparts=db.relationship('Sparepart', back_populates='garage', cascade='all, delete-orphan')
    reviews=db.relationship('Review', back_populates='garage', cascade='all, delete-orphan')
  
  
class Car(db.Model,SerializerMixin):
    __tablename__='cars'
    
    id=db.Column(db.Integer, primary_key=True)
    make=db.Column(db.String,nullable=False)
    model=db.Column(db.String)
    year_of_manufacture=db.Column(db.Integer)
    color=db.Column(db.String)
    engine_capacity=db.Column(db.Float)
    fuel_type=db.Column(db.String)
    transmission=db.Column(db.String)
    mileage=db.Column(db.Integer)
    registration_number=db.Column(db.String, unique=True)
    price=db.Column(db.Float)
    description=db.Column(db.Text)
    created_at=db.Column(db.DateTime, default=datetime.utcnow)
    location=db.Column(db.String)
    
    owner_id=db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    owner=db.relationship('User', back_populates='cars')
    images=db.relationship('CarImage', back_populates='car', cascade='all, delete-orphan')
    

class Sparepart(db.Model, SerializerMixin):
    __tablename__='spareparts'
    
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String, nullable=False)
    description=db.Column(db.Text)
    part_number=db.Column(db.String, unique=True)
    brand=db.Column(db.String)
    condition=db.Column(db.String, default='New')
    price=db.Column(db.Float, nullable=False)
    quantity=db.Column(db.Integer, nullable=False)
    created_at=db.Column(db.DateTime, default=datetime.utcnow)
    
    seller_id=db.Column(db.Integer, db.ForeignKey('users.id'),nullable=False)
    garage_id=db.Column(db.Integer,db.ForeignKey('garages.id'))
    
    seller=db.relationship('User', back_populates='spareparts')
    garage=db.relationship('Garage', back_populates='spareparts')
    images=db.relationship('SpareImage', back_populates='sparepart', cascade='all,delete-orphan')
    
    

class Review(db.Model,SerializerMixin):
    __tablename__='reviews'
    
    id=db.Column(db.Integer, primary_key=True)
    rating=db.Column(db.Integer, nullable=False)
    comment=db.Column(db.Text)
    created_at=db.Column(db.DateTime, default=datetime.utcnow)
    
    user_id=db.Column(db.Integer, db.ForeignKey('users.id'),nullable=False)
    garage_id=db.Column(db.Integer, db.ForeignKey('garages.id'))
    
    user=db.relationship('User', back_populates='reviews')
    garage=db.relationship('Garage', back_populates='reviews')
    
    
    
class CarImage(db.Model, SerializerMixin):
    __tablename__='carimages'
    
    id=db.Column(db.Integer, primary_key=True)
    image_url=db.Column(db.String, nullable=False)
    car_id=db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    
    car=db.relationship('Car', back_populates='images')
    
    

class SpareImage(db.Model, SerializerMixin):
    __tablename__='spareimages'
    
    id=db.Column(db.Integer, primary_key=True)
    image_url=db.Column(db.String, nullable=False)
    sparepart_id=db.Column(db.Integer, db.ForeignKey('spareparts.id'), nullable=False)
    
    sparepart=db.relationship('Sparepart', back_populates='images')