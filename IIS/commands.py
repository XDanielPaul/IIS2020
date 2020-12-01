import click
from flask.cli import with_appcontext
from .models import User,Festival,Reservation,Ticket,Stage,Interpret, Schedule, Performance, perfs
from .extensions import db

@click.command(name='create_tables')
@with_appcontext
def create_tables():
    db.create_all()

@click.command(name='destroy_tables')
@with_appcontext
def destroy_tables():
    db.drop_all()

@click.command(name='restart_tables')
@with_appcontext
def restart_tables():
    db.drop_all()
    db.create_all()

@click.command(name='fill_database')
@with_appcontext
def fill_database():
    db.session.add(User(name = "aN", surname = "aS", login = "admin", email="admin@gmail.com", unhashed_password= "admin", priviliges = 3))
    db.session.add(User(name = "User's_Name", surname = "User's_Surname", email="user@gmail.com", login = "user", unhashed_password= "user", priviliges = 0))
    db.session.commit()
    f_pohoda = Festival(name="Pohoda", description="Je to super festival",genre="rock", paid_on_spot = 1, date_start="2020-12-03",date_end="2020-12-04",location="Trenčín",price="30",max_capacity="500",remaining_capacity="500")
    db.session.add(f_pohoda)
    f_grape = Festival(name="Grape", description="Je to tiez super festival",genre="metal", paid_on_spot = 0, date_start="2020-12-06",date_end="2020-12-09",location="Piešťany",price="25",max_capacity="1000",remaining_capacity="1000")
    db.session.add(f_grape)
    db.session.commit()
    s_O2 = Stage(name="O2_stage", festival=f_pohoda, create_schedules=[f_pohoda.date_start, f_pohoda.date_end])
    db.session.add(s_O2)
    s_Orange = Stage(name="Orange_stage", festival=f_pohoda, create_schedules=[f_pohoda.date_start, f_pohoda.date_end])
    db.session.add(s_Orange)
    s_Levy = Stage(name="Levy_stage", festival=f_grape, create_schedules=[f_grape.date_start, f_grape.date_end])
    db.session.add(s_Levy)
    eminem = Interpret(name="Eminem",members="Eminem",rating="10",genre="rap")
    db.session.add(eminem)
    abusus = Interpret(name="Abusus",members="Branko Jóbus",rating="10",genre="folk")
    db.session.add(abusus)
    elan = Interpret(name="Elán",members="Jožko Vajda",rating="6",genre="pop")
    db.session.add(elan)
    nohavica = Interpret(name="Jaromír Nohavica",members="Jaromír Nohavica",rating="10",genre="folk")
    db.session.add(nohavica)
    db.session.commit()
    s_O2.performers.append(eminem)
    s_O2.performers.append(elan)
    s_Levy.performers.append(nohavica)
    s_Levy.performers.append(elan)
    s_Orange.performers.append(nohavica)
    s_Orange.performers.append(abusus)
    db.session.commit()
