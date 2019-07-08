import tornado.ioloop
import tornado.web

class MainHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "*")
        self.set_header('Access-Control-Allow-Methods', 'POST, OPTIONS')

    def post(self):
        data = self.get_argument('data', '')
        print(data)

        result = {
                'results': ({
                    'meta': ('a', 'b', 'c'),
                    'values': (
                        (1, -2., 'c3'),
                        (4, 5.5, 'c6'),
                        )
                    },)
                }
        self.write(result)

    def options(self):
        # no body
        self.set_status(204)
        self.finish()


def make_app():
    return tornado.web.Application([
        (r'/', MainHandler),
    ])

if __name__ == '__main__':
    app = make_app()
    app.listen(30000)
    tornado.ioloop.IOLoop.current().start()
