from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash
from commands import create_tables, destroy_tables, restart_tables
from extensions import db,login_manager
from settings import *
from datetime import timedelta

#from models import *
import pymysql


app = Flask(__name__)
app.config['SECRET_KEY'] = "SECRET_KEY"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://cgewkxohwrzbqz:791eb1445e7861448b11c5f17bb7fc7b0041d97958e425c9dc577a002c2c05ee@ec2-3-220-98-137.compute-1.amazonaws.com:5432/d5m38slqf76vdr'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=5)
db.init_app(app)
login_manager.init_app(app)
app.cli.add_command(create_tables)
app.cli.add_command(destroy_tables)
app.cli.add_command(restart_tables)

from models import User,Festival,Reservation,Ticket,Stage,Interpret,perfs
#fill_database()


login_manager.login_view = 'app.login'
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('home'))

def invalid_priviliges_check(p):
    if(current_user.priviliges < p ):
        return redirect(url_for('home'))

def fill_database():
    db.session.add(User(name = "aN", surname = "aS", login = "admin", unhashed_password= "admin", priviliges = 3))
    db.session.add(User(name = "User's_Name", surname = "User's_Surname", login = "user", unhashed_password= "user", priviliges = 0))
    db.session.commit()
    f_pohoda = Festival(name="Pohoda", description="Je to super festival",genre="rock",date_start="2020-12-03",date_end="2020-12-04",location="Trenčín",price="30",max_capacity="500",remaining_capacity="500")
    db.session.add(f_pohoda)
    f_grape = Festival(name="Grape", description="Je to tiez super festival",genre="metal",date_start="2020-12-06",date_end="2020-12-09",location="Piešťany",price="25",max_capacity="1000",remaining_capacity="1000")
    db.session.add(f_grape)
    db.session.commit()
    s_O2 = Stage(name="O2_stage", festival=f_pohoda)
    db.session.add(s_O2)
    s_Orange = Stage(name="Orange_stage", festival=f_pohoda)
    db.session.add(s_Orange)
    s_Levy = Stage(name="Levy_stage", festival=f_grape)
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

''' HOME '''

@app.route("/")
def home():
    #fill_database()
    #print(perfs)
    festivals = Festival.query.all()
    stages = Stage.query.all()
    return render_template("home.html", isHome=True, current_user = current_user, festivals=festivals, stages=stages)

''' TICKETS '''
@app.route('/cashier')
@login_required
def cashier():
    invalid_priviliges_check(1)
    reservations = Reservation.query.all()
    return render_template("cashier.html", reservations=reservations, isCashier=True)

@app.route('/buy_tickets/<name>', methods=['GET','POST'])
#Zatial login required
@login_required
def buy_tickets(name):
    festival = Festival.query.filter_by(name=name).first()
    if request.method == "POST":
        num = int(request.form["num"])
        # TODO Not enough capacity
        if num > festival.remaining_capacity:
            pass
        reservation = Reservation(owner = current_user, paid=False)
        db.session.add(reservation)
        db.session.commit()
        for _ in range(0,num):
            ticket = Ticket(festival = festival, reservation = reservation)
            db.session.add(ticket)

        festival.remaining_capacity = festival.remaining_capacity - num
        db.session.commit()
        return redirect(url_for('reservations'))
    return render_template("buy_tickets.html", festival = festival)

@app.route('/remove_reservation/<id>')
@login_required
def remove_reservation(id):
    invalid_priviliges_check(1)
    reservation = Reservation.query.filter_by(id = int(id)).first()
    reservation.tickets_R[0].festival.remaining_capacity += len(reservation.tickets_R)
    for ticket in reservation.tickets_R:
        db.session.delete(ticket)

    db.session.delete(reservation)
    db.session.commit()
    return redirect(url_for('cashier'))


@app.route('/reservations')
#Zatial login required
@login_required
def reservations():
    reservations = current_user.reservations
    return render_template("reservations.html", reservations=reservations, isReservations=True)
    


''' AUTHENTIFICATION '''

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == "POST":
        #Register -> Add to database -> Login page
        login = request.form["login"]
        password = request.form["password"]
        name = request.form["name"]
        surname = request.form["surname"]
        if (login == "" or password == ""):
            return render_template("register.html", isReg= True)
        user = User(name = name, surname = surname, login = login, unhashed_password= password, priviliges = 0)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    else:
        #Render register.html
        return render_template("register.html", isReg=True)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == "POST":
        login = request.form["login"]
        password = request.form["password"]
        user = User.query.filter_by(login=login).first()
        error_message=''
        #Hash
        if not user or not check_password_hash(user.password, password):
            error_message = "Wrong username or password"
        if not error_message:
            login_user(user)
            session.permanent = True
            return redirect(url_for('home'))
        
    return render_template("login.html", isLogin= True)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

''' PROFILE '''

@app.route('/profile/<login>', methods=['GET','POST'])
@login_required
def profile(login):
    user = User.query.filter_by(login=login).first()
    if request.method == "POST":
         return redirect(url_for('edit_profile'))
    return render_template("profile.html", isProfile=True, current_user = current_user, viewed_user = user)

@app.route('/profile/<login>/edit', methods=['GET','POST'])
@login_required
def edit_profile(login):
    if(login != current_user.login):
        return redirect(url_for('profile', login = login))
    if request.method == "POST":
        user = User.query.filter_by(login = login).first()
        if (request.form["name"] != ""):
            user.name = request.form["name"]
        if (request.form["surname"] != ""):
            user.surname = request.form["surname"]
        if (request.form["login"] != ""):
            user.login = request.form["login"]
        db.session.commit()
        return redirect(url_for('profile', login = current_user.login))
    return render_template("profile.html", isProfile=True, current_user = current_user, isEdit=True)

'''ROLES'''

''' Admin '''

@app.route('/admin')
@login_required
def admin():
    invalid_priviliges_check(3)
    users = User.query.all()
    return render_template("admin.html", users = users, isAdmin=True)

@app.route('/remove_user/<id>')
@login_required
def remove_user(id):
    invalid_priviliges_check(3)
    user = User.query.filter_by(id=int(id)).first()
    if user.priviliges < 3:
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for('admin'))

''' Organizer '''

@app.route('/organizer')
@login_required
def organizer():
    invalid_priviliges_check(2)
    festivals = Festival.query.all()
    interprets = Interpret.query.all()
    stages = Stage.query.all()

    return render_template("organizer.html", festivals=festivals, interprets = interprets, stages=stages, isOrganizer=True)

@app.route('/add_festival', methods=['GET','POST'])
@login_required
def add_festival():
    invalid_priviliges_check(2)
    description = ""

    if request.method == "POST":
        if (request.form["name"] != ""):
            name = request.form["name"]
        if (request.form["description"] != ""):
            description = request.form["description"]
        if (request.form["genre"] != ""):
            genre = request.form["genre"]
        if (request.form["date_start"] != ""):
            date_start = request.form["date_start"]
        if (request.form["date_end"] != ""):
            date_end = request.form["date_end"]
        if (request.form["location"] != ""):
            location = request.form["location"]
        if (request.form["price"] != ""):
            price = request.form["price"]
        if (request.form["max_capacity"] != ""):
            max_capacity = request.form["max_capacity"]
        
        festival = Festival(name=name, description=description,genre=genre, date_start=date_start,date_end=date_end,location=location,price=price,max_capacity=max_capacity,remaining_capacity=max_capacity)
        db.session.add(festival)
        db.session.commit()
        return redirect(url_for('organizer'))
    return render_template("add_festival.html")

@app.route('/remove_festival/<id>')
@login_required
def remove_festival(id):
    invalid_priviliges_check(2)
    festival = Festival.query.filter_by(id=int(id)).first()
    db.session.delete(festival)
    db.session.commit()
    return redirect(url_for('organizer'))


@app.route('/add_stage', methods=['GET','POST'])
@login_required
def add_stage():
    invalid_priviliges_check(2)
    festivals = Festival.query.all()
    if request.method == "POST":
        if (request.form["name"] != ""):
            name = request.form["name"]
        if (request.form["festival"] != ""):
            festival_id = request.form["festival"]
        fest = Festival.query.filter_by(id = int(festival_id)).first()
        stage = Stage(name=name, festival=fest)
        db.session.add(stage)
        db.session.commit()
        redirect(url_for('organizer'))
    return render_template("add_stage.html", festivals=festivals)

@app.route('/remove_stage/<id>')
@login_required
def remove_stage(id):
    invalid_priviliges_check(2)
    stage = Stage.query.filter_by(id=int(id)).first()
    db.session.delete(stage)
    db.session.commit()
    return redirect(url_for('organizer'))


@app.route('/add_interpret', methods=['GET','POST'])
@login_required
def add_interpret():
    invalid_priviliges_check(2)
    members = ""

    if request.method == "POST":
        if (request.form["name"] != ""):
            name = request.form["name"]
        if (request.form["members"] != ""):
            members = request.form["members"]
        if (request.form["rating"] != ""):
            rating = request.form["rating"]
        if (request.form["genre"] != ""):
            genre = request.form["genre"]
   
        interpret = Interpret(name=name, members=members, rating=rating, genre=genre)
        db.session.add(interpret)
        db.session.commit()
    return render_template("add_interpret.html")

@app.route('/remove_interpret/<id>')
@login_required
def remove_interpret(id):
    invalid_priviliges_check(2)
    interpret = Interpret.query.filter_by(id=int(id)).first()
    db.session.delete(interpret)
    db.session.commit()
    return redirect(url_for('organizer'))

@app.route('/add_interpret_to_stage',  methods=['GET','POST'])
@login_required
def add_interpret_to_stage():
    invalid_priviliges_check(2)
    stages = Stage.query.all()
    interprets = Interpret.query.all()
    if request.method == "POST":
        if (request.form["stage"] != ""):
            stage_id = request.form["stage"]
        if (request.form["interpret"] != ""):
            interpret_id = request.form["interpret"]
        stg = Stage.query.filter_by(id = int(stage_id)).first()
        interp = Interpret.query.filter_by(id = int(interpret_id)).first()
        if(interp not in stg.performers):
            stg.performers.append(interp)
            db.session.commit()
        else:
            return render_template("add_interpret_to_stage.html", stages=stages, interprets=interprets, contains=True )
    return render_template("add_interpret_to_stage.html", stages=stages, interprets=interprets )

        


if __name__ == "__main__":
    app.run(debug=True)
