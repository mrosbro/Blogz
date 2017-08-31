from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import desc
from sqlalchemy.sql import func 


app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://blogz:helloworld69@localhost:8889/blogz"
db = SQLAlchemy(app)
app.secret_key = "y337kGcys&zP3C4"