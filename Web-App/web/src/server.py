from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import FileResponse

def get_home(req):
  return FileResponse("home.html")

def receive_file(request):
    if request.method == "POST":
        images = request.POST.getall('images')
        for im in images:
            name = im.filename
            f = im.file
            print(name)
            
    #extract images from request
    #pass to classifier
    #store results in db
    return ['hi']

''' Route Configurations '''
if __name__ == '__main__':
  config = Configurator()

  config.add_route('get_home', '/')
  config.add_view(get_home, route_name='get_home')

  config.add_route('file_transfer', '/transfer')
  config.add_view(receive_file,route_name = 'file_transfer',renderer='json')

  config.add_static_view(name='/', path='./public', cache_max_age=3600)

  app = config.make_wsgi_app()
  server = make_server('0.0.0.0', 6000, app)
  server.serve_forever()
