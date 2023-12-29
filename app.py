import werkzeug.security
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect
from flask_login import UserMixin, LoginManager, login_required
from flask_sqlalchemy import SQLAlchemy
from datetime import date

app = Flask(__name__)
load_dotenv()

app.config['SECRET_KEY'] = os.getenv('FLASK_KEY')

# Connects to the EquineSocial Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
db = SQLAlchemy()
db.init_app(app)

# Configures a flask login manager
login_manager = LoginManager()
login_manager.init_app(app)


# Creates a user_loader callback
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


# Creates the User table in the EquineSocial Database
class User(UserMixin, db.Model):
    email = db.Column(db.String(100), unique=True)
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(100))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    country = db.Column(db.String(50))
    birthday = db.Column(db.String(50))
    profile_image = db.Column(db.String(50))
    page_image = db.Column(db.String(50))
    award1 = db.Column(db.String(50))
    award2 = db.Column(db.String(50))
    award3 = db.Column(db.String(50))
    award4 = db.Column(db.String(50))
    award5 = db.Column(db.String(50))
    award6 = db.Column(db.String(50))
    award7 = db.Column(db.String(50))
    award8 = db.Column(db.String(50))


class Posts(UserMixin, db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    replies_to_post = db.Column(db.Integer)
    post_from = db.Column(db.Integer)
    post_to = db.Column(db.Integer)
    title = db.Column(db.String(50))
    date = db.Column(db.String(50))
    text = db.Column(db.String(100))


class Images(UserMixin, db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    image_owner = db.Column(db.Integer)
    image_location = db.Column(db.String(50))
    date = db.Column(db.String(50))
    title = db.Column(db.String(100))


class Horses(UserMixin, db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    owner_id = db.Column(db.Integer)
    name = db.Column(db.String(50))
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    country = db.Column(db.String(50))
    birthday = db.Column(db.String(50))
    profile_image = db.Column(db.String(50))
    page_image = db.Column(db.String(50))
    award1 = db.Column(db.String(50))
    award2 = db.Column(db.String(50))
    award3 = db.Column(db.String(50))
    award4 = db.Column(db.String(50))
    award5 = db.Column(db.String(50))
    award6 = db.Column(db.String(50))
    award7 = db.Column(db.String(50))
    award8 = db.Column(db.String(50))

# Creates the tables in the EquineSocial Database
with app.app_context():
    db.create_all()

@app.route('/')
def home_page():
    print("User accessing home page.")
    return render_template('index.html', user_file=None)

@app.route("/adduser", methods=["POST"])
def add_user():
    if request.method == "POST":
        print("User adding user file.")
        with app.app_context():
            new_user = User(email=request.form['input_email'],
                            password=werkzeug.security.generate_password_hash(request.form['input_password'],
                                                                              method='pbkdf2:sha256', salt_length=16),
                            first_name=request.form['input_first_name'],
                            last_name=request.form['input_last_name'])
            #db.session.add(new_user)
            #db.session.commit()
    return render_template('index.html', user_file=None)

@app.route("/login", methods=["POST"])
def login_user():
    if request.method == "POST":
        email = request.form['input_email']
        password = request.form['input_password']
        print(email)
        return render_template('index.html', user_file=None)

if __name__ == '__main__':
    app.run(host='0.0.0.0')