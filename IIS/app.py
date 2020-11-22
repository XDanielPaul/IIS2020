from flask import Flask, render_template, request, redirect, url_for
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash
from commands import create_tables, destroy_tables
from extensions import db,login_manager
from settings import *

#from models import *
import pymysql


app = Flask(__name__)
app.config['SECRET_KEY'] = "SECRET_KEY"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://cgewkxohwrzbqz:791eb1445e7861448b11c5f17bb7fc7b0041d97958e425c9dc577a002c2c05ee@ec2-3-220-98-137.compute-1.amazonaws.com:5432/d5m38slqf76vdr'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
db.init_app(app)
login_manager.init_app(app)
app.cli.add_command(create_tables)
app.cli.add_command(destroy_tables)
from models import User



login_manager.login_view = 'app.login'
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route("/")
def home():
    #all_u = User.query.all()
    return render_template("base.html")

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == "POST":
        # Login click -> Login page
        if request.form.get("loginbutton"):
            return redirect(url_for('login'))
        #Register -> Add to database -> Login page
        login = request.form["login"]
        password = request.form["password"]
        name = request.form["name"]
        surname = request.form["surname"]
        user = User(name = name, surname = surname, login = login, unhashed_password= password, priviliges = 0)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    else:
        #Render register.html
        return render_template("register.html")

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == "POST":
        # Register click -> Register page
        if request.form.get("regbutton"):
            return redirect(url_for('register'))

        login = request.form["login"]
        password = request.form["password"]
        user = User.query.filter_by(login=login).first()
        error_message=''
        #Hash
        if not user or not check_password_hash(user.password, password):
            error_message = "Wrong username or password"
        if not error_message:
            login_user(user)
            return redirect(url_for('home'))
        
    return render_template("login.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/admin')
@login_required
def admin():
    if(current_user.priviliges != 1):
        return redirect(url_for('home'))
    return render_template("admin.html")



if __name__ == "__main__":
    app.run(debug=True)
