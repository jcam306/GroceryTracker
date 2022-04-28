from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.renderers import render_to_response
from pyramid.response import Response, FileResponse

import mysql.connector as mysql
import datetime
import os

db_user = os.environ['MYSQL_USER']
db_pass = os.environ['MYSQL_PASSWORD']
db_name = os.environ['MYSQL_DATABASE']
db_host = os.environ['MYSQL_HOST']  # must 'localhost' when running this script outside of Docker

# Connect to the database
db = mysql.connect(user=db_user, password=db_pass, host=db_host, database=db_name)
cursor = db.cursor()

"""---------------------Helper-Functions-------------------------"""


def get_items_count(user, item):
    cursor.execute("SELECT * FROM Items WHERE user LIKE '%{}%' AND item_name LIKE '%{}%';".format(user, item))
    record = cursor.fetchone()
    if record is None:
        return 0
    return record[4]


def get_user_helper(user, item):
    pass


"""---------------------Home-Page---------------------------------"""


def get_home(req):  # FIXME MAYBE
    return FileResponse('templates/index.html');


"""---------------------User-Routes-------------------------------"""


def add_user(req):
    id_user = req.matchdict['user_id']
    id_count = req.matchdict['count_id']

    query = "insert into Users (username, camera_count, created_at) values (%s, %s, %s)"
    values = [
        (id_user, id_count, datetime.datetime.now()),
    ]
    cursor.executemany(query, values)
    db.commit()


"""---------------------Items-Routes------------------------------"""


def remove_item(req):  # FIXME /remove_item/{username}/{item_name}/{location}/{item_count}
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



def add_item(req):  # /add_item/{username}/{item_name}/{location}/{item_count}
    id_user = req.matchdict['username']
    id_item = req.matchdict['item_name']
    id_location = req.matchdict['location']
    id_count = req.matchdict['item_count']

    the_count = get_items_count(id_user, id_item)
    if the_count > 0:  # Update Item
        query = "UPDATE Items SET item_count = {} AND created_at = {} WHERE item_name = {} AND user = {}".format(the_count+id_count, datetime.datetime.now(),  id_item, id_user)
        cursor.executeone(query)
        db.commit()
    else:  # Insert Item
        query = "insert into Items (user, item_name, location, item_count, created_at) values (%s, %s, %s, %s, %s, %s)"
        values = [
            ('{}'.format(id_user), '{}'.format(id_item), '{}'.format(id_location), '{}'.format(id_count), datetime.datetime.now())
        ]
        cursor.executeone(query, values)
        db.commit()


def get_items(req): # /get/{username}
    id_user = req.matchdict['username']
    cursor.execute("SELECT * FROM Items WHERE user LIKE '%{}%';".format(id_user))
    record = cursor.fetchone()
    time_data = record[5].strftime("%d-%b-%Y (%H:%M:S.%f)")
    response = {
        'item_name': record[2],
        'location': record[3],
        'item_count': record[4],
        'created_at': time_data
    }
    return response


''' Route Configurations '''
if __name__ == '__main__':
    config = Configurator()

    config.include('pyramid_jinja2')
    config.add_jinja2_renderer('.html')

    config.add_route('get_home', '/')
    config.add_view(get_home, route_name='get_home')

    config.add_route('add_user', '/add_user/{user_id}/{count_id}')
    config.add_view(add_item, route_name='add_user')

    config.add_route('add_item', '/add_item/{username}/{item_name}/{location}/{item_count}')
    config.add_view(add_item, route_name='add_item')

    config.add_route('get_items', '/get/{username}/')
    config.add_view(get_items, route_name='get_items')

    config.add_route('remove_item', '/remove_item/{username}/{item_name}/{location}/{item_count}')
    config.add_view(remove_item, route_name='remove_item')

    config.add_static_view(name='/', path='./public', cache_max_age=3600)

    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 6000, app)
    server.serve_forever()
