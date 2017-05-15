
__author__ = 'akash'


import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.gen
import tornado.web
import tornado.concurrent

import os

from tornado.options import define, options

from cluster_it import do_it

import json

define("port", default=8877, help="run on the given port", type=int)

settings = {'debug': True, 
            'static_path': os.getcwd()}

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        print(self.get_argument("name", default="Jadav"))
        self.write("Hello, world")

class MyStaticFileHandler(tornado.web.StaticFileHandler):
    def set_extra_headers(self, path):
        # Disable cache
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')

class TopicHandler(tornado.web.RequestHandler):
    def get(self):
        topic = self.get_argument("topic")
        data2 = do_it(topic)
        self.render("clus_result.html")

def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application([
        (r"/topic", TopicHandler),
        (r'/*/(.*)', MyStaticFileHandler, {'path': os.getcwd(), 'default_filename': 'index.html'})
    ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()