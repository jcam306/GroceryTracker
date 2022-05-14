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
    cursor.execute("SELECT item_count FROM Items WHERE (Items.camera_id = '{}' AND Items.item_name='{}')".format(camera, item))
    record = cursor.fetchone()
    if record is None:
        return 0
    for item in record:
        print(item)
    return record[0] #  Is this right?


"""---------------------Home-Page---------------------------------"""


def get_home(req):
    # return FileResponse('home.html')
    return Response('Hello World!')


"""---------------------User-Routes-------------------------------"""


def add_user(req):  # /add_user/{user_id}
    id_user = req.matchdict['user_id']
    cursor.execute("INSERT INTO Users (username) VALUES ('{}')".format(id_user))
    db.commit()
    return Response('added {}'.format(id_user))


def drop_user(req): # FIXME: needs a route
    id_user = req.matchdict['user_id']
    cursor.execute("Delete FROM Users where Users.username='{}'".format(id_user))
    db.commit()


"""---------------------Camera-Routes-----------------------------"""


def add_camera(req):  #/add_camera/{camera_id}/{user_id'/'{location_id}
    id_camera = req.matchdict['camera_id']
    id_user = req.matchdict['user_id']
    id_location = req.matchdict['location_id']

    cursor.execute("INSERT INTO Cameras (camera_id, user, location) VALUES ('{}', '{}', '{}')".format(id_camera, id_user, id_location))
    db.commit()
    return Response('add {}'.format(id_camera))


def drop_camera(req): # FIXME: write function
    pass


"""---------------------Items-Routes------------------------------"""

# add_item/{camera_id}/{item_name}/{item_count}/{item_tags}
def add_item(req):  # /add_item/{camera_id}/{item_name}/{item_count}/{item_tags}
    id_camera = req.matchdict['camera_id']
    id_item = req.matchdict['item_name']
    id_count = req.matchdict['item_count']
    id_tags = req.matchdict['item_tags']

    the_count = get_items_count(id_camera, id_item)
    if the_count > 0:  # Update Item
        cursor.execute("UPDATE Items SET item_count = {} WHERE (item_name = '{}' AND camera_id = '{}')".format(the_count+id_count, id_item, id_count))
        db.commit()
    else:  # Insert Item
        cursor.execute("INSERT INTO Items (camera_id, item_name, item_count, tags) VALUES ('{}', '{}', {}, '{}')".format(id_camera, id_item, id_count, id_tags))
        db.commit()
    return Response('add {}'.format(id_item))


def get_items(req):  # /get/{username}
    id_user = req.matchdict['username']
    cursor.execute("SELECT item_name, item_count, location, tags \
                    FROM Users \
                    INNER JOIN Cameras ON Users.username=Cameras.user \
                    INNER JOIN Items ON Cameras.camera_id=Items.camera_id \
                    WHERE user= '{}';".format(id_user))
    records = cursor.fetchall()
    responses = []
    for record in records:  # Fix this stuff probably

        response = {
            'item_name': record[0],
            'location': record[1],
            'item_count': record[2],
            'tags': record[3]
        }
        print(response)
        responses.append(response)
    # print(responses)
    return Response(responses)


def remove_item(req):  # /remove_item/{camera_id}/{item_name}/{item_count}
    id_camera = req.matchdict['camera_id']
    id_item = req.matchdict['item_name']
    id_count = req.matchdict['item_count']

    the_count = get_items_count(id_camera, id_item)
    the_count = the_count - int(id_count)
    print("the count: ", the_count)
    if int(the_count) <= 0:  # Delete Item
        cursor.execute("DELETE FROM Items WHERE (item_name = '{}' AND camera_id = '{}')".format(id_item, id_camera))
        db.commit()
    else:  # Update Item
        cursor.execute("UPDATE Items SET item_count = {} WHERE (item_name = '{}' AND camera_id = '{}')".format(str(the_count), id_item, id_camera))
        db.commit()
    return Response('removed {}'.format(id_item))


''' Route Configurations '''
if __name__ == '__main__':
    print("Starting web server...")
    # config = Configurator()
    with Configurator() as config:
        config.include('pyramid_jinja2')
        config.add_jinja2_renderer('.html')

        config.add_route('get_home', '/')
        config.add_view(get_home, route_name='get_home')

        config.add_route('add_user', '/add_user/{user_id}')
        config.add_view(add_user, route_name='add_user')

        config.add_route('add_camera', '/add_camera/{camera_id}/{user_id}/{location_id}')
        config.add_view(add_camera, route_name='add_camera')

        config.add_route('add_item', '/add_item/{camera_id}/{item_name}/{item_count}/{item_tags}')
        config.add_view(add_item, route_name='add_item')

        config.add_route('get_items', '/get/{username}')
        config.add_view(get_items, route_name='get_items', renderer='json')

        config.add_route('remove_item', '/remove_item/{camera_id}/{item_name}/{item_count}')
        config.add_view(remove_item, route_name='remove_item')

        config.add_static_view(name='/', path='./public', cache_max_age=3600)

        app = config.make_wsgi_app()

    server = make_server('0.0.0.0', 6543, app)
    print('Web server started on: http://0.0.0.0:6000/')
    server.serve_forever()
