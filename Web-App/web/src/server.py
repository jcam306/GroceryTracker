from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.renderers import render_to_response
from pyramid.response import Response, FileResponse

import mysql.connector as mysql
import datetime
import os
from dotenv import load_dotenv


load_dotenv('credentials.env')
db_user = os.environ['MYSQL_USER']
db_pass = os.environ['MYSQL_PASSWORD']
db_name = os.environ['MYSQL_DATABASE']
db_host = os.environ['MYSQL_HOST']  # must 'localhost' when running this script outside of Docker

# Connect to the database
db = mysql.connect(user=db_user, password=db_pass, host=db_host, database=db_name)
cursor = db.cursor()

"""---------------------Helper-Functions-------------------------"""


def get_items_count(camera, item):
    cursor.execute("SELECT * FROM Items WHERE user LIKE '%{}%' AND item_name LIKE '%{}%';".format(camera, item))
    record = cursor.fetchone()
    if record is None:
        return 0
    return record[4]


def get_user_helper(user, item):
    pass


"""---------------------Home-Page---------------------------------"""


def get_home(req):
    return FileResponse('home.html')


"""---------------------User-Routes-------------------------------"""


def add_user(req):  # /add_user/{user_id}
    id_user = req.matchdict['user_id']

    query = "INSERT INTO Users (username, created_at) VALUES (%s, %s)"
    values = [
        (id_user, datetime.datetime.now()),
    ]
    cursor.executemany(query, values)
    db.commit()


def drop_user(req): # FIXME: needs a route
    id_user = req.matchdict['user_id']
    query = "DROP {} FROM Users".format(id_user)  # FIXME : drop from cameras and items
    cursor.executeone(query)
    db.commit()


"""---------------------Camera-Routes-----------------------------"""


def add_camera(req):  #/add_camera/{camera_id}/{user_id'/'{location_id}
    id_camera = req.matchdict['camera_id']
    id_user = req.matchdict['user_id']
    id_location = req.matchdict['location_id']


    query = "INSERT INTO Cameras (camera_id, user, location, created_at) VALUES (%s, %s, %s %s)"
    values = [
        (id_camera, id_user, id_location, datetime.datetime.now()),
    ]
    cursor.executeone(query, values)
    db.commit()


def drop_camera(req): # FIXME: write function
    pass


"""---------------------Items-Routes------------------------------"""


def add_item(req):  # /add_item/{camera_id}/{item_name}/{item_count}/{item_tags}
    id_camera = req.matchdict['camera_id']
    id_item = req.matchdict['item_name']
    id_count = req.matchdict['item_count']
    id_tags = req.matchdict['item_tags']

    the_count = get_items_count(id_camera, id_item)
    if the_count > 0:  # Update Item
        query = "UPDATE Items SET item_count = {} AND updated_last = {} WHERE item_name = {} AND camera_id = {}".format(the_count+id_count, datetime.datetime.now(),  id_item, id_camera)
        cursor.executeone(query)
        db.commit()
    else:  # Insert Item
        query = "insert into Items (user, item_name, location, item_count, tags,  updated_last) values (%s, %s,  %s, %s, %s)"
        values = [
            ('{}'.format(id_camera), '{}'.format(id_item), '{}'.format(id_count), '{}'.format(id_tags), datetime.datetime.now())
        ]
        cursor.executeone(query, values)
        db.commit()


def get_items(req):  # TODO: test when tables are joined.  # /get/{username}
    id_user = req.matchdict['username']
    cursor.execute("SELECT item_name, item_count, location, tags \
                    FROM Users \
                    INNER JOIN Cameras ON Users.username=Cameras.user \
                    INNER JOIN Items ON Cameras.camera_id=Items.camera_id \
                    WHERE user LIKE '%{}%';".format(id_user))
    # cursor.execute("SELECT * FROM user WHERE user LIKE '%{}%';".format(id_user))
    records = cursor.fetchmany()
    responses = []
    for record in records:
        time_data = record[5].strftime("%d-%b-%Y (%H:%M:S.%f)")
        response = {
            'item_name': record[2],
            'location': record[3],
            'item_count': record[4],
            'updated_last': time_data
        }
        responses.append(response)
    return responses


def remove_item(req):  # do I need this? FIXME /remove_item/{camera_id}/{item_name}/{item_count}
    id_user = req.matchdict['username']
    id_item = req.matchdict['item_name']
    id_location = req.matchdict['location']
    id_count = req.matchdict['item_count']

    the_count = get_items_count(id_user, id_item)
    if the_count > id_count:  # Delete Item
        query = "DELETE FROM Items WHERE item_name = {} AND user = {}".format(id_item, id_user);
        cursor.executeone(query)
        db.commit()
    else:  # Update Item
        query = "UPDATE Items SET item_count = {} AND created_at = {} WHERE item_name = {} AND user = {}".format(the_count-id_count, datetime.datetime.now(),  id_item, id_user)
        cursor.executeone(query)
        db.commit()


''' Route Configurations '''
if __name__ == '__main__':
    print("Starting web server...")
    config = Configurator()

    # config.include('pyramid_jinja2')
    # config.add_jinja2_renderer('.html')

    config.add_route('get_home', '/')
    config.add_view(get_home, route_name='get_home')

    config.add_route('add_user', '/add_user/{user_id}')
    config.add_view(add_item, route_name='add_user')

    config.add_route('add_camera', '/add_camera/{camera_id}/{user_id}/{location_id}')
    config.add_view(add_camera, route_name='add_camera')

    config.add_route('add_item', '/add_item/{camera_id}/{item_name}/{item_count}/{item_tags}')
    config.add_view(add_item, route_name='add_item')

    config.add_route('get_items', '/get/{username}/')
    config.add_view(get_items, route_name='get_items')

    config.add_route('remove_item', '/remove_item/{camera_id}/{item_name}/{item_count}')
    config.add_view(remove_item, route_name='remove_item')

    config.add_static_view(name='/', path='./public', cache_max_age=3600)

    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 6000, app)
    print('Web server started on: http://0.0.0.0:6000')
    server.serve_forever()
