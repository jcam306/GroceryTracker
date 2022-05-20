import json
from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.renderers import render_to_response
from pyramid.response import Response, FileResponse

import mysql.connector as mysql
import datetime
import os
from dotenv import load_dotenv
import shutil
import gt_local


load_dotenv('credentials.env')
db_user = os.environ['MYSQL_USER']
db_pass = os.environ['MYSQL_PASSWORD']
db_name = os.environ['MYSQL_DATABASE']
db_host = os.environ['MYSQL_HOST']  # must 'localhost' when running this script outside of Docker



"""---------------------Helper-Functions-------------------------"""

def add_item_local(id_camera,id_item,id_count,id_tags):
    # Connect to the database
    db = mysql.connect(user=db_user, password=db_pass, host=db_host, database=db_name)
    cursor = db.cursor()
    the_count = get_items_count(id_camera, id_item)
    if the_count > 0:  # Update Item
        cursor.execute("UPDATE Items SET item_count = {} WHERE (item_name = '{}' AND camera_id = '{}')".format(the_count+id_count, id_item, id_count))
        db.commit()
    else:  # Insert Item
        cursor.execute("INSERT INTO Items (camera_id, item_name, item_count, tags) VALUES ('{}', '{}', {}, '{}')".format(id_camera, id_item, id_count, id_tags))
        db.commit()
    db.close()
    return Response('add {}'.format(id_item))


def get_items_count(camera, item):
    # Connect to the database
    db = mysql.connect(user=db_user, password=db_pass, host=db_host, database=db_name)
    cursor = db.cursor()
    cursor.execute("SELECT item_count FROM Items WHERE (Items.camera_id = '{}' AND Items.item_name='{}')".format(camera, item))
    record = cursor.fetchone()
    if record is None:
        return 0
    for item in record:
        print(item)
    db.close()
    return record[0] #  Is this right?


"""---------------------Home-Page---------------------------------"""


def get_home(req):
    return FileResponse('home.html')
    # return Response('Hello World!')


"""---------------------User-Routes-------------------------------"""


def add_user(req):  # /add_user/{user_id}
    # Connect to the database
    db = mysql.connect(user=db_user, password=db_pass, host=db_host, database=db_name)
    cursor = db.cursor()
    id_user = req.matchdict['user_id']
    cursor.execute("INSERT INTO Users (username) VALUES ('{}')".format(id_user))
    db.commit()
    db.close()
    return Response('added {}'.format(id_user))


def drop_user(req): # FIXME: needs a route
    # Connect to the database
    db = mysql.connect(user=db_user, password=db_pass, host=db_host, database=db_name)
    cursor = db.cursor()
    id_user = req.matchdict['user_id']
    cursor.execute("Delete FROM Users where Users.username='{}'".format(id_user))
    db.commit()
    db.close()


"""---------------------Camera-Routes-----------------------------"""


def add_camera(req):  #/add_camera/{camera_id}/{user_id'/'{location_id}
    # Connect to the database
    db = mysql.connect(user=db_user, password=db_pass, host=db_host, database=db_name, port=3307)
    cursor = db.cursor()
    id_camera = req.matchdict['camera_id']
    id_user = req.matchdict['user_id']
    id_location = req.matchdict['location_id']

    cursor.execute("INSERT INTO Cameras (camera_id, user, location) VALUES ('{}', '{}', '{}')".format(id_camera, id_user, id_location))
    db.commit()
    db.close()
    return Response('add {}'.format(id_camera))


def drop_camera(req): # FIXME: write function
    pass


"""---------------------Items-Routes------------------------------"""

# add_item/{camera_id}/{item_name}/{item_count}/{item_tags}
def add_item(req):  # /add_item/{camera_id}/{item_name}/{item_count}/{item_tags}
    # Connect to the database
    db = mysql.connect(user=db_user, password=db_pass, host=db_host, database=db_name)
    cursor = db.cursor()
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
    db.close()
    return Response('add {}'.format(id_item))


def get_items(req):  # /get/{username}
    # Connect to the database
    db = mysql.connect(user=db_user, password=db_pass, host=db_host, database=db_name)
    cursor = db.cursor()
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
            'item_count': record[1],
            'location': record[2],
            'tags': record[3]
        }
        print(response)
        responses.append(response)
    # print(responses)
    return Response(json.dumps(responses))



def remove_item(req):  # /remove_item/{camera_id}/{item_name}/{item_count}
    # Connect to the database
    db = mysql.connect(user=db_user, password=db_pass, host=db_host, database=db_name)
    cursor = db.cursor()
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
    db.close()
    return Response('removed {}'.format(id_item))

"""
File transfer functions

"""
# add_item/{camera_id}/{item_name}/{item_count}/{item_tags}
def receive_file(request):
    print('This is a post request')
    if request.method == "POST":
        images = request.POST.getall('images')
        for im in images:
            name = im.filename
            print(name)
            f = im.file
            file_path = os.path.join('/app/public/images/received', name)
            folder_loc = '/app/public/images/processed_images'
            if not os.path.exists(folder_loc):
                os.mkdir(folder_loc)
            temp_file_path = file_path + '~'
            f.seek(0)
            with open(temp_file_path, 'wb') as output_file:
                shutil.copyfileobj(f, output_file)
            os.rename(temp_file_path, file_path)
            #todo: preprocessing
            x=gt_local.img_pro(file_path,name, folder_loc)
            file_path = os.path.join('/app/public/images/processed_images', name)
            d = gt_local.tracking(file_path)
            print(d)
            tags = ''
            for tag in d:
                temp = tag.name + ': '+tag.value+', '
                tags = tags+temp
            add_item_local('0000000000',d[0].name,1,tags)

    #Todo:store results in db
    return {'error':'none'}

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

        config.add_route('file_transfer', '/transfer')
        config.add_view(receive_file,route_name = 'file_transfer',renderer='json')

        config.add_static_view(name='/', path='./public', cache_max_age=3600)



        app = config.make_wsgi_app()

    server = make_server('0.0.0.0', 6000, app)
    print('Web server started on: http://0.0.0.0:6000/')
    server.serve_forever()
