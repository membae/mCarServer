from models import db,User,Mechanic,Garage,Car,Review,Service,Sparepart,CarImage,SpareImage
from flask_migrate import Migrate
from flask import Flask, request, make_response,jsonify
from flask_restful import Api, Resource
from flask_jwt_extended import JWTManager,create_access_token, create_refresh_token,jwt_required,get_jwt_identity
import secrets,datetime,os
from datetime import timedelta
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash,generate_password_hash
import cloudinary
import cloudinary.uploader
import cloudinary.api

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

cloudinary.config(
    cloud_name="dia2le5vz",
    api_key="716219668214133",
    api_secret="12Wn1cP9Wc_cZb6gFWMe2tdvHWQ"
)


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

class Garage_by_id(Resource):
    def get(self,id):
        garage=Garage.query.filter_by(id=id).first()
        if garage:
            return make_response(garage.to_dict(),200)
        return make_response({"msg":"garage entered does not exist"},404)
    
    def patch(self,id):
        garage=Garage.query.filter_by(id=id).first()
        if garage:
            data=request.get_json()
            for attr in data:
                if attr in['name','location','rating','owner_id']:
                    setattr(garage,attr,data.get(attr))
            db.session.add(garage)
            db.session.commit()
            return make_response(garage.to_dict(),200)
        return make_response({"msg":"Garage entered does not exist"},404)
    
    def delete(self,id):
        garage=Garage.query.filter_by(id=id).first()
        if garage:
            db.session.delete(garage)
            db.session.commit()
            return make_response({"msg":"Garage deleted successfully"},200)
        return make_response({"msg":"Garage does not exist"},404)   
            
api.add_resource(Garage_by_id,'/garage/<int:id>')

class Get_cars(Resource):
    def get(self):
        cars=Car.query.all()
        if cars:
            return make_response([car.to_dict() for car in cars],200)
        return make_response({"msg":"No cars exist at the moment"},404)
    
    def post(self):
        data=request.get_json()
        make=data.get('make')
        model=data.get('model')
        year_of_manufacture=data.get('year_of_manufacture')
        color=data.get('color')
        engine_capacity=data.get('engine_capacity')
        fuel_type=data.get('fuel_type')
        transmission=data.get('transmission')
        mileage=data.get("mileage")
        price=data.get('price')
        description=data.get('description')
        location=data.get('location')
        owner_id=data.get('owner_id')
        registration_number=data.get('registration_number')
        owner=User.query.get(owner_id)
        if not owner:
            return make_response({"msg":"Owner does not exist as a registered user"},404)
        car=Car.query.filter_by(registration_number=registration_number).first()
        if car:
            return make_response({"msg":"Car entered already exist"},409)
        new_car=Car(make=make,model=model,year_of_manufacture=year_of_manufacture,color=color, engine_capacity=engine_capacity,fuel_type=fuel_type,transmission=transmission,mileage=mileage,registration_number=registration_number,price=price,description=description,location=location,owner_id=owner_id)
        db.session.add(new_car)
        db.session.commit()
        return make_response(new_car.to_dict(),201)
    
        
    
api.add_resource(Get_cars,'/cars')

class Car_by_id(Resource):
    def get(self,id):
        car=Car.query.filter_by(id=id).first()
        if car:
            return make_response(car.to_dict(),200)
        return make_response({"msg":"Car does not exist"},404)
    
    def patch(self,id):
        car=Car.query.filter_by(id=id).first()
        if car:
            data=request.get_json()
            if "registration_number" in data:
                existing=Car.query.filter_by(registration_number=data['registration_number']).first()
                if existing and existing.id !=id:
                    return make_response({"msg":"Car with the registration number already exists"},409)
            for attr in data:
                if attr in['make','model','year_of_manufacture','color','engine_capacity','fuel_type','transmission','mileage','registration_number','price','description','location','owner_id']:
                    setattr(car,attr,data.get(attr))
            db.session.add(car)
            db.session.commit()
            return make_response(car.to_dict(),200)
        return make_response({"msg":"Car does not exist"},404)
    
    def delete(self,id):
        car=Car.query.filter_by(id=id).first()
        if car:
            db.session.delete(car)
            db.session.commit()
            return make_response({"msg":"Car deleted successfully"},200)
        return make_response({"msg":"Car entered does not exist"},404)
    
api.add_resource(Car_by_id,'/car/<int:id>')

class Get_spareparts(Resource):
    def get(self):
        spareparts=Sparepart.query.all()
        if spareparts:
            return make_response([sparepart.to_dict() for sparepart in spareparts],200)
        return make_response({"msg":"No spareparts exists at the moment"},404)
    
    def post(self):
        data=request.get_json()
        name=data.get("name")
        description=data.get('description')
        part_number=data.get('part_number')
        brand=data.get('brand')
        condition=data.get('condition')
        price=data.get('price')
        quantity=data.get('quantity')
        seller_id=data.get('seller_id')
        garage_id=data.get("garage_id")
        
        seller=None
        garage=None
        
        if seller_id:
            seller=User.query.get(seller_id)
            if not seller:
                return make_response({"msg":"Seller must be a registered user"},404)
        if garage_id:
            garage=Garage.query.get(garage_id)
            if not garage:
                return make_response({"msg":"Garage entered does not exist"},404)
        if not seller and not garage:
            return make_response({"msg":"A sparepart must belong to either a seller or a garage"},409)
        existing=Sparepart.query.filter_by(part_number=part_number).first()
        if existing:
            return make_response({"msg":"Sparepart with this part number already exist"},409)
        sparepart=Sparepart(name=name,description=description,part_number=part_number,brand=brand,condition=condition,price=price,quantity=quantity,seller_id=seller_id,garage_id=garage_id)
        db.session.add(sparepart)
        db.session.commit()
        return make_response(sparepart.to_dict(),201)
api.add_resource(Get_spareparts,'/spareparts')

class Sparepart_by_id(Resource):
    def get(self,id):
        sparepart=Sparepart.query.filter_by(id=id).first()
        if sparepart:
            return make_response(sparepart.to_dict(),200)
        return make_response({"msg":"sparepart entered does not exist"},404)
    
    def patch(self,id):
        sparepart=Sparepart.query.filter_by(id=id).first()
        if sparepart:
            data=request.get_json()
            if 'part_number' in data:
                existing=Sparepart.query.filter_by(part_number=data['part_number']).first()
                if existing and existing.id !=id:
                    return make_response({"msg":"Sparepart with the entered sparepart number already exist"},409)
            for attr in data:
                if attr in['name','description','part_number','brand','condition','price','quantity','seller_id','garage_id']:
                    setattr(sparepart,attr,data.get(attr))
            db.session.add(sparepart)
            db.session.commit()
            return make_response(sparepart.to_dict(),200)
        return make_response({"msg":"Sparepart entered does not exist"},404)
    
    def delete(self,id):
        sparepart=Sparepart.query.filter_by(id=id).first()
        if sparepart:
            db.session.delete(sparepart)
            db.session.commit()
            return make_response({"msg":"Sparepart entered deleted successfully"},200)
        return make_response({"msg":"Sparepart entered does not exist"})        
api.add_resource(Sparepart_by_id,'/sparepart/<int:id>')

# class Get_reviews(Resource):
#     def get(self):
#         reviews=Review.query.all()
#         if reviews:
#             return make_response([review.to_dict() for review in reviews],200)
#         return make_response({"msg":"No reviews at this time"},404)
    
#     def post(self):
#         data=request.get_json()
        
    
# api.add_resource(Get_reviews,'/reviews')

class Get_car_images(Resource):
    def get(self):
        images=CarImage.query.all()
        if images:
            return make_response([image.to_dict() for image in images],200)
        return make_response({"msg":"No images at this time"},404)
    
    def post(self):
        files=request.files.getlist('images')
        car_id=request.form.get('car_id')
        car=Car.query.get(car_id)
        if not car:
            return make_response({"msg":"Car id entered does not exist"},404)
        if not files or len(files)==0:
            return make_response({"msg":"No image provided"},400)
        uploaded_images=[]
        for file in files:
            if not allowed_file(file.filename):
                return make_response({"msg":"Invalid file format"},400)
            upload_result=cloudinary.uploader.upload(file)
            image_url=upload_result.get('secure_url')
            public_id=upload_result.get('public_id')
            new_image=CarImage(image_url=image_url,car_id=car.id)
            
            db.session.add(new_image)
            uploaded_images.append(new_image)
        db.session.commit()
        return make_response([img.to_dict() for img in uploaded_images],201)
    
api.add_resource(Get_car_images,'/carimg')

class Car_image_by_id(Resource):
    def get(self,id):
        image=CarImage.query.filter_by(id=id).first()
        if image:
            return make_response(image.to_dict(),200)
        return make_response({"msg":"No image found"},404)
    
    def patch(self,id):
        image=CarImage.query.filter_by(id=id).first()
        if not image:
            return make_response({"msg":"No image found"},404)
        file=request.files.get('images')
        if not file:
            return make_response({"msg":"No image provided"},404)
        if not allowed_file(file.filename):
            return make_response({"msg":"Invalid file format"},400)
        upload_result=cloudinary.uploader.upload(file)
        image.image_url=upload_result.get('secure_url')
        db.session.commit()
        return make_response(image.to_dict(),200)
    
api.add_resource(Car_image_by_id,'/carimg/<int:id>')
            

if __name__=="__main__":
    app.run(debug=True)