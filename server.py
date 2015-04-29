# -*- coding: utf-8 -*-

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from blog import blog

http_server = HTTPServer(WSGIContainer(blog))
http_server.listen(80)
IOLoop.instance().start()
