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