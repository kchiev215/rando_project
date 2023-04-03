from flask import Flask
from data_extraction import credentials
from flask_mysqldb import MySQL
import mysql.connector

app = Flask(__name__)
app.secret_key = '123secret'

# Initialize MySQL
mysql_ = MySQL(app)

# configure database connection
app.config['MYSQL_HOST'] = credentials.host
app.config['MYSQL_USER'] = credentials.user
app.config['MYSQL_PASSWORD'] = credentials.password
app.config['MYSQL_DB'] = credentials.database

# create database connection
db = mysql.connector.connect(host=app.config['MYSQL_HOST'],
                             user=app.config['MYSQL_USER'],
                             password=app.config['MYSQL_PASSWORD'],
                             database=app.config['MYSQL_DB'])

# create a cursor
cursor = db.cursor()


from flask_app import routes
