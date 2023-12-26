import werkzeug.security
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect
from flask_login import UserMixin, LoginManager, login_required
from flask_sqlalchemy import SQLAlchemy
from datetime import date

app = Flask(__name__)

@app.route('/')
def home_page():
    print("Hello to log")
    return render_template('index.html', user_file=None)

if __name__ == '__main__':
    app.run(host='0.0.0.0')