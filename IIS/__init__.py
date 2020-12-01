from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Mail, Message
from werkzeug.security import check_password_hash
from .commands import create_tables, destroy_tables, restart_tables, fill_database
from .extensions import db, login_manager
from .settings import *
from datetime import timedelta, date
import random
import string
import time

# from models import *
import pymysql


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "SECRET_KEY"
    # SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://cgewkxohwrzbqz:791eb1445e7861448b11c5f17bb7fc7b0041d97958e425c9dc577a002c2c05ee@ec2-3-220-98-137.compute-1.amazonaws.com:5432/d5m38slqf76vdr'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = 'iisprojectfestival@gmail.com'
    app.config['MAIL_PASSWORD'] = 'vxowcngqolmtaxzh'
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_SUPPRESS_SEND'] = False
    app.config['MAIL_DEBUG'] = True
    app.config['TESTING'] = False

    mail = Mail()
    mail.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    app.cli.add_command(create_tables)
    app.cli.add_command(destroy_tables)
    app.cli.add_command(restart_tables)
    app.cli.add_command(fill_database)

    def length(list):
        return len(list)
    app.jinja_env.globals.update(length=length)

    def queryempty(q):
        if (type(q) == list):
            return len(q) == 0
        else:
            return q.first() is None
    app.jinja_env.globals.update(queryempty=queryempty)

    def convToStr(element):
        return str(element)
    app.jinja_env.globals.update(convToStr=convToStr)

    from .models import User, Festival, Reservation, Ticket, Stage, Interpret, Schedule, Performance, perfs
    # fill_database()

    login_manager.login_view = 'app.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    @login_manager.unauthorized_handler
    def unauthorized():
        return redirect(url_for('home'))

    def invalid_priviliges_check(p):
        if(current_user.priviliges < p):
            return redirect(url_for('home'))

    def get_random_string():
        letters = string.ascii_lowercase
        result_str = ''.join(random.choice(letters) for i in range(8))
        return result_str

    def is_between(time, time_range):
        if time_range[1] < time_range[0]:
            return time > time_range[0] or time < time_range[1]
        return time_range[0] < time < time_range[1]

    def send_email(m, code):
        msg = Message('IISFestival Reservation code',
                      sender='iisprojectfestival@gmail.com',
                      recipients=[m])
        msg.body = 'Your code is {}'.format(code)
        time.sleep(2)
        mail.send(msg)

    ''' HOME '''

    @app.route("/", methods=['GET', 'POST'])
    def home():
        # fill_database()
        genres = ["blues", "country", "dubstep", "electro", "folk", "jazz",
                  "metal", "party", "pop", "rap", "r&b and soul", "rock", "techno"]
        interprets = Interpret.query.all()
        festivals = Festival.query.all()
        stages = Stage.query.all()
        if request.method == 'POST':
            if request.form.get("filter_festival"):
                if (request.form["name"] != "" and request.form["genre"] != "None"):
                    name = request.form["name"]
                    genre = request.form["genre"]
                    festivals = Festival.query.filter_by(
                        name=name, genre=genre)
                elif (request.form["name"] != "" and request.form["genre"] == "None"):
                    name = request.form["name"]
                    festivals = Festival.query.filter_by(name=name)
                elif (request.form["name"] == "" and request.form["genre"] != "None"):
                    genre = request.form["genre"]
                    festivals = Festival.query.filter_by(genre=genre)
            if request.form.get("filter_interpret"):
                if (request.form["name"] != "" and request.form["genre"] != "None"):
                    name = request.form["name"]
                    genre = request.form["genre"]
                    interprets = Interpret.query.filter_by(
                        name=name, genre=genre)
                elif (request.form["name"] != "" and request.form["genre"] == "None"):
                    name = request.form["name"]
                    interprets = Interpret.query.filter_by(name=name)
                elif (request.form["name"] == "" and request.form["genre"] != "None"):
                    genre = request.form["genre"]
                    interprets = Interpret.query.filter_by(genre=genre)

        context = {
            'current_user': current_user,
            'genres': genres,
            'festivals': festivals,
            'stages': stages,
            'interprets': interprets,
            'isHome': True
        }

        return render_template("home.html", **context)

    ''' TICKETS '''
    @app.route('/cashier')
    @login_required
    def cashier():
        invalid_priviliges_check(1)
        reservations = Reservation.query.all()
        return render_template("cashier.html", reservations=reservations, isCashier=True)

    @app.route('/approve_reservation/<code>')
    @login_required
    def approve_reservation(code):
        invalid_priviliges_check(1)
        reservation = Reservation.query.filter_by(code=code).first()
        reservation.approved = 1
        db.session.commit()
        return redirect(url_for('cashier'))

    @app.route('/remove_reservation/<code>')
    @login_required
    def remove_reservation(code):
        reservation = Reservation.query.filter_by(code=code).first()
        if(current_user.priviliges < 1 and current_user.id != reservation.owner.id):
            return redirect('home')
        reservation.tickets_R[0].festival.remaining_capacity += len(
            reservation.tickets_R)
        for ticket in reservation.tickets_R:
            db.session.delete(ticket)
        db.session.delete(reservation)
        db.session.commit()
        if(current_user.priviliges > 0):
            return redirect(url_for('cashier'))
        else:
            return redirect(url_for('reservations'))

    @app.route('/buy_tickets/<name>', methods=['GET', 'POST'])
    def buy_tickets(name):
        festival = Festival.query.filter_by(name=name).first()
        if request.method == "POST":
            num = int(request.form["num"])
            # TODO Not enough capacity
            if num > festival.remaining_capacity:
                return render_template("buy_tickets.html", festival=festival)
            if not current_user.is_authenticated:
                reservation = Reservation(owner=None, paid=0, date_created=date.today(
                ).strftime("%Y-%m-%d"), code=get_random_string(), approved=0)
                # print(request.form["email"])
                send_email(request.form["email"], reservation.code)
            else:
                reservation = Reservation(owner=current_user, paid=0, date_created=date.today(
                ).strftime("%Y-%m-%d"), code=get_random_string(), approved=0)

            db.session.add(reservation)
            db.session.commit()
            for _ in range(0, num):
                ticket = Ticket(
                    festival=festival, reservation=reservation, code=get_random_string())
                db.session.add(ticket)

            festival.remaining_capacity = festival.remaining_capacity - num
            db.session.commit()
            if not current_user.is_authenticated:
                return redirect(url_for('unauthenticated_reservation', code=reservation.code))
            else:
                return redirect(url_for('reservations'))
        return render_template("buy_tickets.html", festival=festival)

    @app.route('/unauthenticated_reservation/<code>')
    def unauthenticated_reservation(code):
        reservation = Reservation.query.filter_by(code=code).first()
        return render_template("unauthenticated_reservation.html", reservation=reservation)

    @app.route('/pay_reservation/<code>')
    @login_required
    def pay_reservation(code):
        reservation = Reservation.query.filter_by(code=code).first()
        reservation.paid = 1
        if(current_user.priviliges < 1 and current_user.id != reservation.owner.id):
            return redirect('home')
        db.session.commit()
        return redirect(url_for('reservations'))

    @app.route('/reservations', methods=['GET', 'POST'])
    def reservations():
        if (current_user.is_authenticated):
            reservations = current_user.reservations
            return render_template("reservations.html", reservations=reservations, isReservations=True)
        else:
            if request.method == 'POST':
                code = request.form["code"]
                reservation = Reservation.query.filter_by(code=code).first()
                return render_template("reservations.html", reservation=reservation, isReservations=True)
            else:
                return render_template("reservations.html", isReservations=True)

    ''' AUTHENTIFICATION '''

    @app.route('/register/<reservation>', methods=['GET', 'POST'])
    def register(reservation):
        if request.method == "POST":
            # Register -> Add to database -> Login page
            login = request.form["login"]
            password = request.form["password"]
            confirm_password = request.form["confirm_password"]
            name = request.form["name"]
            surname = request.form["surname"]
            email = request.form["email"]

            if bool(User.query.filter_by(login=login).first()):
                context = {
                    'emaill': email,
                    'loginExists': True,
                    'firstname': name,
                    'surnamee': surname,
                    'isReg': True
                }
                return render_template("register.html", **context)

            if bool(User.query.filter_by(email=email).first()):
                context = {
                    'emailExists': True,
                    'firstname': name,
                    'surnamee': surname,
                    'isReg': True
                }
                return render_template("register.html", **context)

            if (password != confirm_password):
                context = {
                    'emaill': email,
                    'passwordsDontMatch': True,
                    'firstname': name,
                    'surnamee': surname,
                    'loginn': login,
                    'isReg': True
                }
                return render_template("register.html", **context)

            user = User(name=name, surname=surname, login=login,
                        email=email, unhashed_password=password, priviliges=0)
            db.session.add(user)
            db.session.commit()
            if(reservation != 'new_user'):
                res = Reservation.query.filter_by(code=reservation).first()
                res.owner = user
                db.session.commit()
            return redirect(url_for('login'))
        else:
            # Render register.html
            return render_template("register.html", isReg=True)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == "POST":
            login = request.form["login"]
            password = request.form["password"]
            user = User.query.filter_by(login=login).first()
            # Hash

            if not user or not check_password_hash(user.password, password):
                context = {
                    'isLogin': True,
                    'wrongLogin': True
                }
                return render_template("login.html", **context)
            else:
                login_user(user)
                session.permanent = True
                return redirect(url_for('home'))

        return render_template("login.html", isLogin=True)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('home'))

    ''' PROFILE '''

    @app.route('/profile/<login>', methods=['GET', 'POST'])
    @login_required
    def profile(login):
        user = User.query.filter_by(login=login).first()
        if request.method == "POST":
            return redirect(url_for('edit_profile'))
        return render_template("profile.html", isProfile=True, current_user=current_user, viewed_user=user)

    @app.route('/profile/<login>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_profile(login):
        if(login != current_user.login):
            return redirect(url_for('profile', login=login))
        if request.method == "POST":
            user = User.query.filter_by(login=login).first()
            if (request.form["name"] != ""):
                user.name = request.form["name"]
            if (request.form["surname"] != ""):
                user.surname = request.form["surname"]
            if (request.form["email"] != ""):
                if not bool(User.query.filter_by(email=request.form["email"]).first()):
                    user.email = request.form["email"]
                else:
                    context = {
                        'isProfile': True,
                        'current_user': current_user,
                        'isEdit': True,
                        'passwordsDontMatch': True,
                        'namee': request.form["name"],
                        'surnamee': request.form["surname"],
                        'loginn': request.form["login"]
                    }
                    return render_template("profile.html", **context)
            if (request.form["password"] != ""):
                if (request.form["password"] == request.form["confirm_password"]):
                    user.unhashed_password = request.form["password"]
                else:
                    context = {
                        'isProfile': True,
                        'emaill': request.form["email"],
                        'current_user': current_user,
                        'isEdit': True,
                        'passwordsDontMatch': True,
                        'namee': request.form["name"],
                        'surnamee': request.form["surname"],
                        'loginn': request.form["login"]
                    }
                    return render_template("profile.html", **context)

            if (request.form["login"] != ""):
                if not bool(User.query.filter_by(login=request.form["login"]).first()):
                    user.login = request.form["login"]
                else:
                    context = {
                        'isProfile': True,
                        'emaill': request.form["email"],
                        'current_user': current_user,
                        'isEdit': True,
                        'loginExists': True,
                        'namee': request.form["name"],
                        'surnamee': request.form["surname"]
                    }
                    return render_template("profile.html", **context)
            db.session.commit()
            return redirect(url_for('profile', login=current_user.login))
        return render_template("profile.html", isProfile=True, current_user=current_user, isEdit=True)

    '''ROLES'''

    ''' Admin '''

    @app.route('/admin', methods=['GET', 'POST'])
    @login_required
    def admin():
        invalid_priviliges_check(3)
        user_to_edit_id = -1
        users = User.query.all()
        if request.method == 'POST':
            if request.form.get("edit_button"):
                user_to_edit_id = request.form['edit_button']
                return render_template("admin.html", user_to_edit_id=user_to_edit_id, users=users, isAdmin=True)
            elif request.form.get("submit_changes"):
                user_to_edit_id = request.form['submit_changes']
                user = User.query.filter_by(id=int(user_to_edit_id)).first()
                if (request.form["name"] != ""):
                    user.name = request.form["name"]
                if (request.form["surname"] != ""):
                    user.surname = request.form["surname"]
                if (request.form["login"] != ""):
                    if not bool(User.query.filter_by(login=request.form["login"]).first()):
                        user.login = request.form["login"]
                if (request.form["email"] != ""):
                    if not bool(User.query.filter_by(email=request.form["email"]).first()):
                        user.email = request.form["email"]
                if (request.form["password"] != ""):
                    user.unhashed_password = request.form["password"]
                if (request.form["priviliges"] != ""):
                    user.priviliges = request.form["priviliges"]
                db.session.commit()
                context = {
                    'user_to_edit_id': -1,
                    'users': users,
                    'isAdmin': True
                }
                return render_template("admin.html", **context)

        else:
            context = {
                'user_to_edit_id': -1,
                'users': users,
                'isAdmin': True
            }
            return render_template("admin.html", **context)

    @app.route('/add_user', methods=['GET', 'POST'])
    @login_required
    def add_user():
        invalid_priviliges_check(3)
        if request.method == 'POST':
            login = request.form["login"]
            password = request.form["password"]
            confirm_password = request.form["confirm_password"]
            name = request.form["name"]
            surname = request.form["surname"]
            email = request.form["email"]
            priviliges = request.form["priviliges"]
            user = User(name=name, surname=surname, login=login,
                        unhashed_password=password, priviliges=int(priviliges))
            if bool(User.query.filter_by(login=login).first()):
                error_message = "The username already exists. Please choose another."
                context = {
                    'loginExists': True,
                    'namee': name,
                    'surnamee': surname,
                    'emaill': email,
                    'priv': priviliges
                }
                return render_template("add_user.html", **context)
            if bool(User.query.filter_by(email=email).first()):
                error_message = "The username with this email already exists."
                context = {
                    'emailExists': True,
                    'namee': name,
                    'surnamee': surname,
                    'loginn': login,
                    'priv': priviliges
                }
                return render_template("add_user.html", **context)
            if (password != confirm_password):
                context = {
                    'passwordsDontMatch': True,
                    'namee': name,
                    'surnamee': surname,
                    'loginn': login,
                    'emaill': email,
                    'priv': priviliges
                }
                return render_template("add_user.html", **context)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('admin'))

        return render_template("add_user.html")

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

    @app.route('/organizer', methods=['GET', 'POST'])
    @login_required
    def organizer():
        invalid_priviliges_check(2)
        festivals = Festival.query.all()
        interprets = Interpret.query.all()
        stages = Stage.query.all()
        festival_to_edit_id = -1
        stage_to_edit_id = -1
        interpret_to_edit_id = -1

        if request.method == "POST":

            # EDIT FESTIVAL
            if request.form.get("edit_festival"):
                festival_to_edit_id = request.form['edit_festival']
                context = {
                    'festival_to_edit_id': festival_to_edit_id,
                    'festivals': festivals,
                    'isOrganizer': True,
                    'stages': stages,
                    'interprets': interprets
                }
                return render_template("organizer.html", **context)

            # SUBMIT FESTIVAL
            elif request.form.get("submit_festival"):
                festival_to_edit_id = request.form['submit_festival']
                festival = Festival.query.filter_by(
                    id=int(festival_to_edit_id)).first()

                if request.form['name'] != "":
                    festival.name = request.form["name"]
                if request.form['description'] != "":
                    festival.description = request.form['description']
                if request.form['genre'] != "":
                    festival.genre = request.form['genre']
                paid_on_spot = request.form.getlist('paid_on_spot')
                if not paid_on_spot:
                    festival.paid_on_spot = 0
                else:
                    festival.paid_on_spot = 1
                if request.form['date_start'] != "":
                    festival.date_start = request.form['date_start']
                if request.form['date_end'] != "":
                    festival.date_end = request.form['date_end']
                if request.form['location'] != "":
                    festival.location = request.form['location']
                if request.form['price'] != "":
                    festival.price = request.form['price']
                if request.form['max_capacity'] != "":
                    festival.max_capacity = request.form['max_capacity']
                    festival.recalculate_remaining_capacity()
                db.session.commit()
                festival_to_edit_id = -1

            # EDIT STAGE
            if request.form.get("edit_stage"):
                stage_to_edit_id = request.form['edit_stage']
                context = {
                    'stage_to_edit_id': stage_to_edit_id,
                    'festivals': festivals,
                    'isOrganizer': True,
                    'stages': stages,
                    'interprets': interprets
                }
                return render_template("organizer.html", **context)
            # SUBMIT STAGE
            elif request.form.get("submit_stage"):
                stage_to_edit_id = request.form['submit_stage']
                stage = Stage.query.filter_by(id=int(stage_to_edit_id)).first()

                if request.form['name'] != "":
                    stage.name = request.form['name']
                if request.form['festival_name'] != "":
                    festival = Festival.query.filter_by(
                        id=int(request.form['festival_name'])).first()
                    stage.festival = festival
                    stage.create_schedules = [
                        festival.date_start, festival.date_end]
                db.session.commit()
                stage_to_edit_id = -1
            # EDIT INTERPRET
            if request.form.get("edit_interpret"):
                interpret_to_edit_id = request.form['edit_interpret']
                context = {
                    'interpret_to_edit_id': interpret_to_edit_id,
                    'festivals': festivals,
                    'isOrganizer': True,
                    'stages': stages,
                    'interprets': interprets
                }
                return render_template("organizer.html", **context)
            # SUBMIT INTERPRET
            elif request.form.get("submit_interpret"):
                interpret_to_edit_id = request.form['submit_interpret']
                interpret = Interpret.query.filter_by(
                    id=int(interpret_to_edit_id)).first()

                if request.form['name'] != "":
                    interpret.name = request.form['name']
                if request.form['members'] != "":
                    interpret.members = request.form['members']
                if request.form['rating'] != "":
                    interpret.rating = request.form['rating']
                if request.form['genre'] != "":
                    interpret.rating = request.form['genre']

                db.session.commit()
                interpret_to_edit_id = -1

        # DRAW TABLES
        context = {
            'interpret_to_edit_id': interpret_to_edit_id,
            'festival_to_edit_id': festival_to_edit_id,
            'stage_to_edit_id': stage_to_edit_id,
            'festivals': festivals,
            'isOrganizer': True,
            'stages': stages,
            'interprets': interprets
        }

        return render_template("organizer.html", **context)

    @app.route('/add_festival', methods=['GET', 'POST'])
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
            paid_on_spot = request.form.getlist('paid_on_spot')
            if not paid_on_spot:
                paid_on_spot = 0
            else:
                paid_on_spot = 1
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

            festival = Festival(name=name, description=description, genre=genre, paid_on_spot=paid_on_spot, date_start=date_start,
                                date_end=date_end, location=location, price=price, max_capacity=max_capacity, remaining_capacity=max_capacity)
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

    @app.route('/add_stage', methods=['GET', 'POST'])
    @login_required
    def add_stage():
        invalid_priviliges_check(2)
        festivals = Festival.query.all()
        if request.method == "POST":
            if (request.form["name"] != ""):
                name = request.form["name"]
            if (request.form["festival"] != ""):
                festival_id = request.form["festival"]
            fest = Festival.query.filter_by(id=int(festival_id)).first()
            stage = Stage(name=name, festival=fest, create_schedules=[
                          fest.date_start, fest.date_end])
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

    @app.route('/add_interpret', methods=['GET', 'POST'])
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

            interpret = Interpret(name=name, members=members,
                                  rating=rating, genre=genre)
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

    @app.route('/add_interpret_to_stage/<name>',  methods=['GET', 'POST'])
    @login_required
    def add_interpret_to_stage(name):
        invalid_priviliges_check(2)
        stage = Stage.query.filter_by(name=name).first()
        interprets = Interpret.query.all()

        if request.method == 'POST':
            if request.form.get("add"):
                if (request.form["interpret_add"] != ""):
                    interpret_id = request.form["interpret_add"]
                interp = Interpret.query.filter_by(
                    id=int(interpret_id)).first()
                stage.performers.append(interp)
                db.session.commit()
            elif request.form.get("remove"):
                if (request.form["interpret_remove"] != ""):
                    interpret_id = request.form["interpret_remove"]
                interp = Interpret.query.filter_by(
                    id=int(interpret_id)).first()
                stage.performers.remove(interp)
                db.session.commit()

        allowed_interprets = []
        included_interprets = []
        for interpret in interprets:
            if interpret not in stage.performers:
                allowed_interprets.append(interpret)
            else:
                included_interprets.append(interpret)

        context = {
            'stage': stage,
            'allowed_interprets': allowed_interprets,
            'included_interprets': included_interprets
        }
        return render_template("add_interpret_to_stage.html", **context)

    @app.route('/manage_schedules/<name>', methods=['GET', 'POST'])
    @login_required
    def manage_schedules(name):
        invalid_priviliges_check(2)
        stage = Stage.query.filter_by(name=name).first()
        if request.method == 'POST':
            print(request.form['edit_schedule'])
            return redirect(url_for('edit_day', name=name, day=request.form['edit_schedule']))

        return render_template('manage_schedules.html', schedules=stage.schedules)

    @app.route('/edit_day/<name>/<day>', methods=['GET', 'POST'])
    @login_required
    def edit_day(name, day):
        invalid_priviliges_check(2)
        stage = Stage.query.filter_by(name=name).first()
        schedule = Schedule.query.filter_by(day=day).first()
        performance_to_edit_id = -1

        if request.method == 'POST':
            # ADD PERFORMANCE
            if request.form.get("add_performance"):
                time_start = request.form['time_start']
                time_end = request.form['time_end']
                interpret_name = request.form['interpret_name']
                if time_start == time_end:
                    context = {
                        'stage': stage,
                        'schedule': schedule,
                        'timeEq': True
                    }
                    return render_template('edit_day.html', **context)
                for performance in schedule.performances:
                    if(is_between(time_start, [performance.start, performance.end]) or is_between(time_end, [performance.start, performance.end])):
                        context = {
                            'stage': stage,
                            'schedule': schedule,
                            'timeCollision': True
                        }
                        return render_template('edit_day.html', **context)

                interpret = Interpret.query.filter_by(
                    name=interpret_name).first()
                db.session.add(Performance(
                    start=time_start, end=time_end, interpret=interpret, schedule=schedule))
                db.session.commit()

            elif request.form.get('edit_performance'):
                performance_to_edit_id = request.form['edit_performance']
                context = {
                    'performance_to_edit_id': performance_to_edit_id,
                    'stage': stage,
                    'schedule': schedule
                }
                return render_template("edit_day.html", **context)

            elif request.form.get('submit_performance'):
                performance_to_edit_id = request.form['submit_performance']
                performance = Performance.query.filter_by(
                    id=int(performance_to_edit_id)).first()

                time_start = request.form['time_start']
                time_end = request.form['time_end']

                if time_start == time_end:
                    context = {
                        'stage': stage,
                        'schedule': schedule,
                        'timeEq': True
                    }
                    return render_template('edit_day.html', **context)
                for performance in schedule.performances:
                    if(is_between(time_start, [performance.start, performance.end]) or is_between(time_end, [performance.start, performance.end])):
                        context = {
                            'stage': stage,
                            'schedule': schedule,
                            'timeCollision': True
                        }
                        return render_template('edit_day.html', **context)

                performance.start = request.form['time_start']
                performance.end = request.form['time_end']

                if request.form['interpret_name'] != "":
                    interpret = Interpret.query.filter_by(
                        name=request.form['interpret_name']).first()
                    performance.interpret = interpret

                db.session.commit()
                context = {
                    'performace_to_edit_id': -1,
                    'performance': performance,
                    'stage': stage,
                    'schedule': schedule
                }

            else:
                context = {
                    'stage': stage,
                    'schedule': schedule
                }
                return render_template('edit_day.html', **context)

        context = {
            'stage': stage,
            'schedule': schedule
        }
        return render_template('edit_day.html', **context)

    @app.route('/remove_performance/<name>/<day>/<id>')
    @login_required
    def remove_performance(name, day, id):
        invalid_priviliges_check(2)
        performance = Performance.query.filter_by(id=int(id)).first()
        db.session.delete(performance)
        db.session.commit()
        return redirect(url_for('edit_day', name=name, day=day))

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
