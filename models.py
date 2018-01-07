from werkzeug.security import generate_password_hash, check_password_hash
from parking import db
import datetime

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fullname = db.Column(db.String(30))
    email = db.Column(db.String(100),unique=True,index=True)
    password_hash = db.Column(db.String(100))
    phoneno = db.Column(db.String(14),unique=True)

    def __init__(self,fullname,email,password,phoneno):
        self.fullname = fullname
        self.email = email
        self.password = password
        self.phoneno = phoneno

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def password(self):
        raise AttributeError("password is write-only")

    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

    def get_id(self):
        return self.email

class Parking(db.Model):
    __tablename__ = "parking"
    id = db.Column(db.Integer,primary_key=True, autoincrement=True)
    sectorid = db.Column(db.Integer,db.ForeignKey('sector.id'))
    loclat = db.Column(db.String(30))
    loclong = db.Column(db.String(30))
    available = db.Column(db.Integer)
    disability = db.Column(db.Integer)

class Sector(db.Model):
    __tablename__ = "sector"
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)

class Notification(db.Model):
    __tablename__ = 'notification'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    userid=db.Column(db.Integer,db.ForeignKey('user.id'))
    message = db.Column(db.String(100))
    ntime = db.Column(db.DateTime(),default=datetime.datetime.now())

class Booking(db.Model):
    __tablename__ = "booking"
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    parkingid = db.Column(db.Integer,db.ForeignKey('parking.id'))
    userid = db.Column(db.Integer,db.ForeignKey('user.id'))
    bookingfrom = db.Column(db.DateTime())
    bookingto = db.Column(db.DateTime())
    checkin = db.Column(db.DateTime())

def correctLogin(user,password):
    return user is not None and user.verify_password(password)

