# Import MySQL Connector Driver
import mysql.connector as mysql

# Load the credentials from the secured .env file
import os
import datetime
from dotenv import load_dotenv

load_dotenv('credentials.env')

db_user = os.environ['MYSQL_USER']
db_pass = os.environ['MYSQL_PASSWORD']
# db_name = os.environ['MYSQL_DATABASE']
# db_host = os.environ['MYSQL_HOST']  # must 'localhost' when running this script outside of Docker

# Connect to the database
db = mysql.connect(user=db_user, password=db_pass)#, host=db_host, database=db_name)
cursor = db.cursor()

# # CAUTION!!! CAUTION!!! CAUTION!!! CAUTION!!! CAUTION!!! CAUTION!!! CAUTION!!!
# cursor.execute("drop table if exists Users;")

cursor.execute("""
    CREATE Database GroceryTracker;
    """)

cursor.execute("""
    Use GroceryTracker;
    """)


try:
    cursor.execute("""
    CREATE TABLE Users (
      id          integer  AUTO_INCREMENT PRIMARY KEY,
      username    VARCHAR(30) NOT NULL,
      created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  """)
except:
    print("Users table already exists. Not recreating it.")


try:
    cursor.execute("""
    CREATE TABLE Cameras (
      id                integer  AUTO_INCREMENT PRIMARY KEY,
      camera_id         VARCHAR(10) NOT NULL,
      user              Varchar(30) NOT NULL,
      location_name     Varchar(30) NOT NULL,
      created_at        TIMESTAMP
    );
  """)
except:
    print("Cameras table already exists. Not recreating it.")

try:
    cursor.execute("""
    CREATE TABLE Items (
      id                   integer  AUTO_INCREMENT PRIMARY KEY,
      camera_id            VARCHAR(10) NOT NULL,
      item_name            VARCHAR(30) NOT NULL, 
      item_count           Integer NOT NULL, 
      tags                 VARCHAR(100),  
      update_last          TIMESTAMP
    );
  """)
except:
    print("Items table already exists. Not recreating it.")


# cursor.execute("SELECT * \
#                 FROM Users \
#                 INNER JOIN Cameras ON Users.username=Cameras.user \
#                 INNER JOIN Items ON Cameras.camera_id=Items.camera_id \
#                 WHERE user LIKE '%{}%';".format(id_user))
