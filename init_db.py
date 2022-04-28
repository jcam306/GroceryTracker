# Import MySQL Connector Driver
import mysql.connector as mysql

# Load the credentials from the secured .env file
import os
import datetime
from dotenv import load_dotenv

load_dotenv('credentials.env')

db_user = os.environ['MYSQL_USER']
db_pass = os.environ['MYSQL_PASSWORD']
db_name = os.environ['MYSQL_DATABASE']
db_host = os.environ['MYSQL_HOST']  # must 'localhost' when running this script outside of Docker

# Connect to the database
db = mysql.connect(user=db_user, password=db_pass, host=db_host, database=db_name)
cursor = db.cursor()

# # CAUTION!!! CAUTION!!! CAUTION!!! CAUTION!!! CAUTION!!! CAUTION!!! CAUTION!!!
# cursor.execute("drop table if exists Users;")

try:
    cursor.execute("""
    CREATE TABLE Users (
      id          integer  AUTO_INCREMENT PRIMARY KEY,
      username    VARCHAR(30) NOT NULL,
      camera_count  Integer,
      created_at  TIMESTAMP
    );
  """)
    # first_name  VARCHAR(30) NOT NULL,
    # last_name   VARCHAR(30) NOT NULL,
    # email       VARCHAR(50) NOT NULL,
    # password    VARCHAR(20) NOT NULL,
except:
    print("Users table already exists. Not recreating it.")

try:
    cursor.execute("""
    CREATE TABLE Items (
      id                   integer  AUTO_INCREMENT PRIMARY KEY,
      user                 VARCHAR(30) NOT
      item_name            VARCHAR(30) NOT NULL,
      location             VARCHAR(30) NOT NULL, 
      item_count           Integer 
      created_at           TIMESTAMP
    );
  """)
except:
    print("Items table already exists. Not recreating it.")
