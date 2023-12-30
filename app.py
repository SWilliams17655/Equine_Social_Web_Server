import flask_login
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
    email = db.Column(db.String(100), unique=True, nullable=False)
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(50), nullable=True)
    state = db.Column(db.String(50), nullable=True)
    country = db.Column(db.String(50), nullable=True)
    birthday = db.Column(db.String(50), nullable=True)
    profile_image = db.Column(db.String(50), nullable=True)
    page_image = db.Column(db.String(50), nullable=True)
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


@app.route('/')
def home_page():
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
            print(new_user)
            db.session.add(new_user)
            db.session.commit()
    return render_template('index.html', user_file=None)


@app.route("/login", methods=["POST"])
def login_user():
    if request.method == "POST":
        email = request.form['input_email']
        password = request.form['input_password']
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()

        if user is None:
            return "<h1>Incorrect id was used</h1>"

        if werkzeug.security.check_password_hash(user.password, password):
            flask_login.login_user(user)
            return redirect(f'/my_page/{user.id}')
        else:
            return "<h1>Incorrect id or password was used</h1>"


@app.route('/my_page/<user_id>')
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
    return render_template('user_page.html', user_file=user_file, horse_file=horse_file, post_file=post_file,
                           image_file=image_file)


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
    return redirect(f'/my_page/{user_id}')


@app.route("/updateuser/<user_id>", methods=["POST"])
def update_user(user_id):
    if request.method == "POST":
        print("In Update")
        city_value = request.form['input_city']
        if city_value != "":
            db.session.execute(db.update(User)
                               .where(User.id == user_id)
                               .values(city=city_value)
                               )

        state_value = request.form['input_state']
        print(state_value)
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

        db.session.commit()

        return redirect(f'/my_page/{user_id}')


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
            photo = request.form['postPhoto']
            print(photo)

            db.session.add(new_post)
            db.session.commit()
    return redirect(f'/my_page/{user_id}')


if __name__ == '__main__':
    app.run(host='0.0.0.0')
