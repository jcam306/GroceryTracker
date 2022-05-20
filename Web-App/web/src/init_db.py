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
db = mysql.connect(user=db_user, password=db_pass, host=db_host, database=db_name, port=3306)
cursor = db.cursor()

# # CAUTION!!! CAUTION!!! CAUTION!!! CAUTION!!! CAUTION!!! CAUTION!!! CAUTION!!!
# cursor.execute("drop database if exists GroceryTracker;")
#cursor.execute("drop table if exists Users;")
#cursor.execute("drop table if exists Cameras;")
#cursor.execute("drop table if exists Items;")

#cursor.execute("""
#    CREATE Database GroceryTracker;
#    """)

#cursor.execute("""
#    Use GroceryTracker;
#    """)


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
      location          Varchar(30) NOT NULL,
      created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
      update_last          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  """)
except:
    print("Items table already exists. Not recreating it.")



# ------------------------------------Populate-DB-with-dummy-data-----------------------------

# users table
cursor.execute("""
    INSERT INTO Users (username) VALUES ('Joshua')
""")
db.commit()
cursor.execute("""
    INSERT INTO Users (username) VALUES ('Max')
""")
db.commit()
cursor.execute("""
    INSERT INTO Users (username) VALUES ('David')
""")
db.commit()
cursor.execute("""
    INSERT INTO Users (username) VALUES ('Ihlyun')
""")
db.commit()
cursor.execute("""
    INSERT INTO Users (username) VALUES ('Jacob')
""")
db.commit()
# cursor.execute("""
#     Delete FROM Users where Users.username='Joshua'
# """)
# db.commit()
# cursor.execute("""
#     INSERT INTO Users (username) VALUES ('Joshua')
# """)
# db.commit()

# Cameras table

cursor.execute("""
    INSERT INTO Cameras (camera_id, user, location) VALUES ('0000000000', 'Joshua', 'fridge')
""")
db.commit()


# items
cursor.execute("""
    insert into Items (camera_id, item_name, item_count, tags) values ('0000000000', 'apple', 1, 'fruit red')
""")
db.commit()
cursor.execute("""
    insert into Items (camera_id, item_name, item_count) values ('0000000000', 'Orange', 1)
""")
db.commit()
cursor.execute("""
    insert into Items (camera_id, item_name, item_count) values ('0000000000', 'milk', 1)
""")
db.commit()
cursor.execute("""
    insert into Items (camera_id, item_name, item_count, tags) values ('0000000000', 'beer', 6, 'tags')
""")
db.commit()
cursor.execute("""
    UPDATE Items SET item_count = 4 WHERE (item_name = 'apple' AND camera_id = '0000000000');
""")
db.commit()

# # helpers
cursor.execute("""
     SELECT * FROM Items ;
 """)
records = cursor.fetchall()
responses = []
for record in records:  # Fix this stuff probably
    time_data = record[5].strftime("%d-%b-%Y (%H:%M:S.%f)")
    response = {
     'item_name': record[2],
     'location': record[3],
     'item_count': record[4],
     'updated_last': time_data
    }
    responses.append(response)
print(responses)
db.close()
#
# #get items
# cursor.execute("""
#     SELECT item_name, item_count, location, tags \
#         FROM Users \
#         INNER JOIN Cameras ON Users.username=Cameras.user \
#         INNER JOIN Items ON Cameras.camera_id=Items.camera_id \
#         WHERE user='Joshua';
# """)
#
# #Delete item
# cursor.execute("""
#     DELETE FROM Items WHERE (item_name = 'Orange' AND camera_id = '0000000000')
# """)
# db.commit()
