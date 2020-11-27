from flask_login import UserMixin
from werkzeug.security import generate_password_hash
from extensions import db

perfs= db.Table('perfs',
    db.Column('interpret_id', db.Integer, db.ForeignKey('interpret.id')),
    db.Column('stage_id', db.Integer, db.ForeignKey('stage.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(60))
    surname = db.Column(db.String(60))
    login = db.Column(db.String(20), unique = True)
    password = db.Column(db.String(100))
    # 0 - user, 1 - Cashier, 2 - Organizer, 3 - Admin
    priviliges = db.Column(db.Integer)
    reservations = db.relationship('Reservation', backref='owner')

    @property
    def unhashed_password(self):
        raise AttributeError("Cannot view unhashed password.")

    @unhashed_password.setter
    def unhashed_password(self, unhashed_password):
        self.password = generate_password_hash(unhashed_password)
    
class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tickets_R = db.relationship('Ticket', backref='reservation')

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    reservation_id = db.Column(db.Integer, db.ForeignKey('reservation.id'))
    festival_id = db.Column(db.Integer, db.ForeignKey('festival.id'))


class Festival(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(60), unique = True)
    description = db.Column(db.String(150))
    genre = db.Column(db.String(30))
    date_start = db.Column(db.String(10))
    date_end = db.Column(db.String(10))
    #Rozpis
    location = db.Column(db.String(40))
    price = db.Column(db.Integer)
    max_capacity = db.Column(db.Integer)
    remaining_capacity = db.Column(db.Integer)
    tickets_F = db.relationship('Ticket', backref='festival')
    stages = db.relationship('Stage', backref='festival')


class Stage(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(60))
    festival_id = db.Column(db.Integer, db.ForeignKey('festival.id'))

class Interpret(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(60), unique = True)
    #Logo
    members = db.Column(db.String(200))
    rating = db.Column(db.Integer)
    genre = db.Column(db.String(30))
    stages = db.relationship('Stage', secondary=perfs, backref=db.backref('performers', lazy='dynamic'))

