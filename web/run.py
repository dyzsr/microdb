import tornado.ioloop
import tornado.web

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        #self.write('Hi GET')
        self.render('index.html', title='microdb')

    def post(self):
        self.write('Hi POST')


def make_app():
    return tornado.web.Application([
        (r'/', MainHandler),
    ])

if __name__ == '__main__':
    app = make_app()
    app.listen(30000)
    tornado.ioloop.IOLoop.current().start()
