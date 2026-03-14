from models import db,User,Mechanic,Garage,Car,Review,Service,Sparepart
from flask_migrate import Migrate
from flask import Flask, request, make_response,jsonify
from flask_restful import Api, Resource
from flask_jwt_extended import JWTManager,create_access_token, create_refresh_token,jwt_required,get_jwt_identity
import secrets,datetime,os
from datetime import timedelta
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash,generate_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")
   
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static')
ALLOWED_EXTENSIONS=set(['png','jpeg','jpg'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit(".",1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] =secrets.token_hex(32)
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=30)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER


migrate = Migrate(app, db)

db.init_app(app)
api=Api(app)
jwt=JWTManager(app)


class Home(Resource):
    def get(self):
        return make_response({"msg":"Cars Homepage here"},200)

api.add_resource(Home,'/')

class Signup(Resource):
    def post(self):
        data=request.get_json()
        email=data.get("email")
        first_name=data.get("first_name")
        last_name=data.get("last_name")
        created_at=datetime.datetime.now()
        password=generate_password_hash(data.get("password"))
        phone=data.get("phone")
        role=data.get("role")
        location=data.get('location')
        if "@" in email and first_name and first_name!=" " and last_name and last_name!=" "and phone and phone!=" " and location and location!=" " and role and role!=" " and data.get("password") and data.get("password")!=" ":
            user=User.query.filter_by(email=email).first()
            if user:
                return make_response({"msg":f"{email} is already registered"},400)
            new_user=User(first_name=first_name,last_name=last_name,email=email,phone=phone,location=location,password=password,created_at=created_at,role=role)
            db.session.add(new_user)
            db.session.commit()
            return make_response(new_user.to_dict(),201)
        return make_response({"msg":"Invalid data entries"},400)
api.add_resource(Signup,'/signup')

class Login(Resource):
    def post(self):
        data=request.get_json()
        email=data.get("email")
        password=data.get("password")
        if "@" in email and password:
            user=User.query.filter_by(email=email).first()
            if user:
                if check_password_hash(user.password,password):
                    access_token=create_access_token(identity=user.id)
                    refresh_token=create_refresh_token(identity=user.id)
                    return make_response({"user":user.to_dict(),"access_token":access_token,"refresh_token":refresh_token},200)
                return make_response({"msg":"Incorrect password"},400)
            return make_response({"msg":"email not registered"},404)
        return make_response({"msg":"Invalid data"})
api.add_resource(Login,'/login')

class GetUsers(Resource):
    def get(self):
        users=User.query.all()
        if users:
            return make_response([user.to_dict() for user in users],200)
        return make_response({"msg","No user found"})
    
api.add_resource(GetUsers,'/users')

class User_by_id(Resource):
    def get(self,id):
        user=User.query.filter_by(id=id).first()
        if user:
            return make_response(user.to_dict(),200)
        return make_response({"msg":"User does not exist"},404)
    
    def patch(self,id):
        user=User.query.filter_by(id=id).first()
        if user:
            data=request.get_json()
            for attr in data:
                if attr in ['first_name','last_name','email','phone','role','location','is_verified']:
                    setattr(user,attr,data.get(attr))
                if "password" in data:
                    user.password=generate_password_hash(data['password'])
            db.session.add(user)
            db.session.commit()
            return make_response(user.to_dict(),200)
        return make_response({"msg":"user not found"})
    
    def delete(self,id):
        user=User.query.filter_by(id=id).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            return make_response({"msg":"user deleted successfully"})
        return make_response({"msg":"user not found"})
    
api.add_resource(User_by_id,'/user/<int:id>')

class Mechanics(Resource):
    def get(self):
        mechanics=Mechanic.query.all()
        if mechanics:
            return make_response([mechanic.to_dict() for mechanic in mechanics],200)
        return make_response({'msg':"no mechanics found"})
    
    def post(self):
        data=request.get_json()
        user_id=data.get('user_id')
        specialization=data.get('specialization')
        hourly_rate=data.get("hourly_rate")
        garage_id=data.get("garage_id")
        
        user=User.query.get(user_id)
        if not user:
            return make_response({"msg":"A mechanic must be a registered user"})
        mechanic=Mechanic(specialization=specialization,hourly_rate=hourly_rate,garage_id=garage_id,user_id=user_id)
        db.session.add(mechanic)
        db.session.commit()
        return make_response(mechanic.to_dict(),201)
    
api.add_resource(Mechanics,'/mechanics')

class Mechanic_by_id(Resource):
    def get(self,id):
        mechanic=Mechanic.query.filter_by(id=id).first()
        if mechanic:
            return make_response(mechanic.to_dict(),200)
        return make_response({"msg":"Mechanic entered not Found"}) 
    
    def patch(self,id):
        mechanic=Mechanic.query.filter_by(id=id).first()
        if mechanic:
            data=request.get_json()
            for attr in data:
                if attr in['specialization','hourly_rate','rating','user_id','garage_id']:
                    setattr(mechanic,attr,data.get(attr))
            db.session.add(mechanic)
            db.session.commit()
            return make_response(mechanic.to_dict(),200)
        return make_response({"msg":"mechanic does not exist"},404)
    
    def delete(self,id):
        mechanic=Mechanic.query.filter_by(id=id).first()
        if mechanic:
            db.session.delete(mechanic)
            db.session.commit()
            return make_response({"msg":"Mechanic deleted successfully"},200)
        return make_response({"msg":"No such mechanic found"},404)
api.add_resource(Mechanic_by_id,'/mechanic/<int:id>')

class Get_services(Resource):
    def get(self):
        services=Service.query.all()
        if services:
            return make_response([service.to_dict() for service in services],200)
        return make_response({"msg":"No services available"})
    
    def post(self):
        data=request.get_json()
        name=data.get("name")
        description=data.get("description")
        price=data.get("price")
        mechanic_id=data.get("mechanic_id")
        garage_id=data.get("garage_id")
        
        if mechanic_id:
            mechanic=Mechanic.query.get(mechanic_id)
            if not mechanic:
                return make_response({"msg":"Mechanic entered not found"})
        if garage_id:
            garage=Garage.query.get(garage_id)
            if not garage:
                return make_response({"msg":"Garage entered not found"})
        if not mechanic and not garage:
            return make_response({"msg":"A service must belong to either a garage or a mechanic"})
        service=Service(name=name, description=description, price=price, mechanic_id=mechanic_id, garage_id=garage_id)
        db.session.add(service)
        db.session.commit()
        return make_response(service.to_dict(),201)
api.add_resource(Get_services,'/services')

class Service_by_id(Resource):
    def get(self,id):
        service=Service.query.filter_by(id=id).first()
        if service:
            return make_response(service.to_dict(),200)
        return make_response({"msg":"Service does not exist"},404)
    
    def patch(self,id):
        service=Service.query.filter_by(id=id).first()
        if service:
            data=request.get_json()
            for attr in data:
                if attr in['name','description','price','garage_id','mechanic_id']:
                    setattr(service,attr,data.get(attr))
            db.session.add(service)
            db.session.commit()
            return make_response(service.to_dict(),201)
        return make_response({"msg":"Service does not exist"},404)
    
    def delete(self,id):
        service=Service.query.filter_by(id=id).first()
        if service:
            db.session.delete(service)
            db.session.commit()
            return make_response({"msg":"Service deleted succesfully"},200)
        return make_response({"msg":"Service does not exist"},404)
api.add_resource(Service_by_id,'/service/<int:id>')

class Get_garages(Resource):
    def get(self):
        garages=Garage.query.all()
        if garages:
            return make_response([garage.to_dict() for garage in garages],200)
        return make_response({"msg":"No garage Found"},404)
    
    def post(self):
        data=request.get_json()
        name=data.get('name')
        location=data.get('location')
        owner_id=data.get("owner_id")
        
        owner=User.query.get(owner_id)
        if not owner:
            return make_response({"msg":"Owner does not exist as a User"},404)
        garage=Garage(name=name,location=location,owner_id=owner_id)
        db.session.add(garage)
        db.session.commit()
        return make_response(garage.to_dict(),201)
api.add_resource(Get_garages,'/garages')


if __name__=="__main__":
    app.run(debug=True)