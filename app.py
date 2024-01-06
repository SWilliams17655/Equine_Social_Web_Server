import flask_login
import werkzeug.security
import os
import boto3
import string
import random
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for
from flask_login import UserMixin, LoginManager, login_required
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import date

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "uploads"

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
    email = db.Column(db.String(100), unique=True, nullable=False)
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(50), nullable=True)
    state = db.Column(db.String(50), nullable=True)
    country = db.Column(db.String(50), nullable=True)
    birthday = db.Column(db.String(50), nullable=True)
    profile_image = db.Column(db.String(250), nullable=True)
    page_image = db.Column(db.String(250), nullable=True)
    award1 = db.Column(db.String(50), nullable=True)
    award2 = db.Column(db.String(50), nullable=True)
    award3 = db.Column(db.String(50), nullable=True)
    award4 = db.Column(db.String(50), nullable=True)
    award5 = db.Column(db.String(50), nullable=True)
    award6 = db.Column(db.String(50), nullable=True)
    award7 = db.Column(db.String(50), nullable=True)
    award8 = db.Column(db.String(50), nullable=True)


class Posts(UserMixin, db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
    replies_to_post = db.Column(db.Integer)
    post_from = db.Column(db.Integer)
    post_to = db.Column(db.Integer)
    title = db.Column(db.String(50))
    date = db.Column(db.String(50))
    text = db.Column(db.String(500))


class Images(UserMixin, db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
    image_owner = db.Column(db.Integer)
    image_location = db.Column(db.String(50))
    date = db.Column(db.String(50))
    title = db.Column(db.String(100))


class Horses(UserMixin, db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
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

def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

@app.route('/')
def home_page():
    return render_template('index.html', message="", user_file=None)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload/<user_id>', methods=["POST"])
def upload(user_id):
    if request.method == 'POST':
        file = request.files['file']
        print(file.filename)
        f = secure_filename(file.filename)
        basedir = os.path.abspath(os.path.dirname(__file__))
        file.save(os.path.join(basedir, app.config['UPLOAD_FOLDER'], f))

        s3 = boto3.client('s3',
                          aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
                          aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS')
                          )
        result = db.session.execute(db.select(User).where(User.id == user_id))
        user_file = result.scalar()
        try:
            s3.delete_object(
                        Bucket=os.getenv('BUCKET_NAME'),
                        Key=user_file.page_image,
            )
        except:
            print("Error: An error occurred while deleting the file. Most common cause is file did not exist.")
        finally:
            print("The deleting operation is complete.")
        random_string = get_random_string(12)
        upload_filename = f"{user_id}_{random_string}_{f}"
        print(f"Uploading new image: {upload_filename}")
        s3.upload_file(
                      Bucket=os.getenv('BUCKET_NAME'),
                      Filename=os.path.join(basedir, app.config['UPLOAD_FOLDER'], f),
                      Key=upload_filename
                  )
        db.session.execute(db.update(User)
                           .where(User.id == user_id)
                           .values(page_image=upload_filename)
                           )
        db.session.commit()
        return redirect(f'/user_page/{user_id}')

@app.route("/adduser", methods=["POST"])
def add_user():
    if request.method == "POST":
        with app.app_context():
            new_user = User(email=request.form['input_email'],
                            password=werkzeug.security.generate_password_hash(request.form['input_password'],
                                                                              method='pbkdf2:sha256', salt_length=16),
                            first_name=request.form['input_first_name'],
                            last_name=request.form['input_last_name'],
                            city = "",
                            state = "",
                            country = "",
                            birthday = "",
                            profile_image = "",
                            page_image = "",
                            award1 = "",
                            award2 = "",
                            award3 = "",
                            award4 = "",
                            award5 = "",
                            award6 = "",
                            award7 = "",
                            award8 = ""
                            )
            db.session.add(new_user)
            db.session.commit()
            return render_template('index.html', user_file=None, message="New account created. Welcome to EquineSocial, please log in to set up your account.")


@app.route("/login", methods=["POST"])
def login_user():
    if request.method == "POST":
        email = request.form['input_email']
        password = request.form['input_password']
        result = db.session.execute(db.select(User).where(func.lower(User.email) == func.lower(email)))
        user = result.scalar()

        if user is None:
            return render_template('index.html', user_file=None, message="Account does not exist, would you like to create an account?")

        if werkzeug.security.check_password_hash(user.password, password):
            flask_login.login_user(user)
            return redirect(f'/user_page/{user.id}')
        else:
            return render_template('index.html', user_file=None, message="Incorrect email or password, please try again.")



@app.route('/user_page/<user_id>')
@login_required
def user_page(user_id):
    result = db.session.execute(db.select(User).where(User.id == user_id))
    user_file = result.scalar()
    result = db.session.execute(db.select(Posts).where(Posts.post_to == user_id))
    post_file = result.scalars()
    result = db.session.execute(db.select(Horses).where(Horses.owner_id == user_id))
    horse_file = result.scalars()
    result = db.session.execute(db.select(Images).where(Images.image_owner == user_id))
    image_file = result.scalars()
    return render_template('user_page.html', logged_in_user_file=flask_login.current_user, user_file=user_file, horse_file=horse_file, post_file=post_file,
                           image_file=image_file)

@app.route('/my_connections/<user_id>')
@login_required
def user_connections(user_id):
    result = db.session.execute(db.select(User).where(User.id == user_id))
    user_file = result.scalar()
    connections_file = db.session.query(User).all()
    return render_template("connections_page.html", logged_in_user_file=flask_login.current_user, user_file=user_file, connections_file=connections_file)

@app.route("/logout")
def logout_user():
    flask_login.logout_user()
    return redirect('/')


@app.route("/addhorse/<user_id>", methods=["POST"])
@login_required
def add_horse(user_id):
    if request.method == "POST":
        with app.app_context():
            new_horse = Horses(name=request.form['input_horse_name'],
                               owner_id=user_id
                               )
            db.session.add(new_horse)
            db.session.commit()
    return redirect(f'/user_page/{user_id}')


@app.route("/updateuser/<user_id>", methods=["POST"])
def update_user(user_id):
    if request.method == "POST":
        first_name_value = request.form['input_first_name']
        if first_name_value != "":
            db.session.execute(db.update(User)
                               .where(User.id == user_id)
                               .values(first_name=first_name_value)
                               )
        last_name_value = request.form['input_last_name']
        if last_name_value != "":
            db.session.execute(db.update(User)
                               .where(User.id == user_id)
                               .values(last_name=last_name_value)
                               )
        city_value = request.form['input_city']
        if city_value != "":
            db.session.execute(db.update(User)
                               .where(User.id == user_id)
                               .values(city=city_value)
                               )

        state_value = request.form['input_state']

        if state_value != "":
            db.session.execute(db.update(User)
                               .where(User.id == user_id)
                               .values(state=state_value)
                               )

        country_value = request.form['input_country']
        if country_value != "":
            db.session.execute(db.update(User)
                               .where(User.id == user_id)
                               .values(country=country_value)
                               )

        award_1 = request.form['input_award_1']
        if award_1 != "":
            db.session.execute(db.update(User)
                               .where(User.id == user_id)
                               .values(award1=award_1)
                               )
        award_2 = request.form['input_award_2']
        if award_2 != "":
            db.session.execute(db.update(User)
                               .where(User.id == user_id)
                               .values(award2=award_2)
                               )
        award_3 = request.form['input_award_3']
        if award_3 != "":
            db.session.execute(db.update(User)
                               .where(User.id == user_id)
                               .values(award3=award_3)
                               )
        award_4 = request.form['input_award_4']
        if award_4 != "":
            db.session.execute(db.update(User)
                               .where(User.id == user_id)
                               .values(award4=award_4)
                               )

        award_5 = request.form['input_award_5']
        if award_5 != "":
            db.session.execute(db.update(User)
                               .where(User.id == user_id)
                               .values(award5=award_5)
                               )
        award_6 = request.form['input_award_6']
        if award_6 != "":
            db.session.execute(db.update(User)
                               .where(User.id == user_id)
                               .values(award6=award_6)
                               )
        award_7 = request.form['input_award_7']
        if award_7 != "":
            db.session.execute(db.update(User)
                               .where(User.id == user_id)
                               .values(award7=award_7)
                               )
        award_8 = request.form['input_award_8']
        if award_8 != "":
            db.session.execute(db.update(User)
                               .where(User.id == user_id)
                               .values(award8=award_8)
                               )

        db.session.commit()

        return redirect(f'/user_page/{user_id}')


@app.route("/adduserpost/<user_id>/<submit_id>", methods=["POST"])
def add_user_post(user_id, submit_id):
    if request.method == "POST":
        with app.app_context():
            new_post = Posts(replies_to_post=0,
                             post_from=submit_id,
                             post_to=user_id,
                             title=request.form['input_title'],
                             date=date.today(),
                             text=request.form['input_post'])

            db.session.add(new_post)
            db.session.commit()
    return redirect(f'/user_page/{user_id}')


if __name__ == '__main__':
    app.run(host='0.0.0.0')
