from flask_login import UserMixin
from werkzeug.security import generate_password_hash
from extensions import db
import pandas as pd


perfs= db.Table('perfs',
    db.Column('interpret_id', db.Integer, db.ForeignKey('interpret.id')),
    db.Column('stage_id', db.Integer, db.ForeignKey('stage.id'))
)



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(60))
    surname = db.Column(db.String(60))
    # New
    email = db.Column(db.String(40), unique = True)
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
    code = db.Column(db.String(8))
    paid = db.Column(db.Integer)
    #NEW
    date_created = db.Column(db.String(10))
    approved = db.Column(db.Integer)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tickets_R = db.relationship('Ticket', backref='reservation')

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    code = db.Column(db.String(8))
    reservation_id = db.Column(db.Integer, db.ForeignKey('reservation.id'))
    festival_id = db.Column(db.Integer, db.ForeignKey('festival.id'))


class Festival(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(60), unique = True)
    description = db.Column(db.String(150))
    genre = db.Column(db.String(30))
    paid_on_spot = db.Column(db.Integer)
    date_start = db.Column(db.String(10))
    date_end = db.Column(db.String(10))
    #Rozpis
    location = db.Column(db.String(40))
    price = db.Column(db.Integer)
    max_capacity = db.Column(db.Integer)
    remaining_capacity = db.Column(db.Integer)
    tickets_F = db.relationship('Ticket', backref='festival')
    stages = db.relationship('Stage', backref='festival')

    def recalculate_remaining_capacity(self):
        self.remaining_capacity = int(self.max_capacity)-len(self.tickets_F)


class Stage(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(60))
    festival_id = db.Column(db.Integer, db.ForeignKey('festival.id'))
    #NEW
    schedules = db.relationship('Schedule', backref='stage')

    @property
    def create_schedules(self):
        raise AttributeError("Cannot view.")

    @create_schedules.setter
    def create_schedules(self, dates):

        # If there were created schedules with different festival, they need to be removed
        if len(self.schedules) > 0:
            for schedule in self.schedules:
                for performance in schedule.performances:
                    db.session.delete(performance)
                db.session.delete(schedule)
            db.session.commit()

        # Creating schedules for stage
        dates = pd.date_range(dates[0],dates[1])
        for date in dates:
            db.session.add(Schedule(day = str(date)[:10], stage = self))
        db.session.commit()



class Interpret(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(60), unique = True)
    members = db.Column(db.String(200))
    rating = db.Column(db.Integer)
    genre = db.Column(db.String(30))
    stages = db.relationship('Stage', secondary=perfs, backref=db.backref('performers', lazy='dynamic'))
    #NEW
    performances = db.relationship('Performance', backref='interpret')

#NEW
class Schedule(db.Model):
   id = db.Column(db.Integer, primary_key = True)
   day = db.Column(db.String(10))
   performances = db.relationship('Performance', backref='schedule')
   stage_id = db.Column(db.Integer, db.ForeignKey('stage.id'))
#NEW
class Performance(db.Model):
   id = db.Column(db.Integer, primary_key = True)
   start = db.Column(db.String(5))
   end = db.Column(db.String(5))
   schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'))
   performer_id = db.Column(db.Integer, db.ForeignKey('interpret.id'))
   #interpret = <Interpret>.