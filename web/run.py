import tornado.ioloop
import tornado.web

import sys
import os

if __name__ == '__main__':
    sys.path.insert(0, os.path.abspath('../'))

from sql.sqlparser import parser
from pengine.logical_engine import *
from pengine.physical_engine import *
import json
import glo.glovar

print(glo.glovar.GlobalVar.dirPath)
glo.glovar.GlobalVar.dirPath = os.environ['HOME'] + '/workspace/db_store'
print('DB store path: ', glo.glovar.GlobalVar.dirPath)


class MainHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "*")
        self.set_header('Access-Control-Allow-Methods', 'POST, OPTIONS')

    def post(self):
        data = json.loads(self.request.body)['data']
        #print(data)

        results = []

        # Parse queries
        try:
            parsingTrees = parser.parse(data)
            err = None
        except Exception as err:
            print(err)
            parsingTrees = tuple()
            err = 'parsing error'
        finally:
       #     print('Parsing tree:')
       #     print(parsingTrees)
            pass

        # Do queries
        for tree in parsingTrees:
            print('Parsing tree:')
            print(json.dumps(tree, indent=2), end='\n\n')

            '''
            logres = LogicalEngine.run_logical_main(tree)
            phyres = PhysicalBlock.dfs_plan_tree(logres)
            print('Result:')
            print(phyres, end='\n\n')

            res = {}
            if phyres.flag == True:
                res['type'] = 'error'
            elif isinstance(phyres.result, str):
                res['type'] = 'info'
            else:
                res['type'] = 'values'
            '''

        # Write back result
        result = {
                'results': [
                    {
                        'type': 'table',
                        'name': 'tb',
                        'meta': ('a', 'b', 'c'),
                        'values': (
                            (1, -2., 'c3'),
                            (4, 5.5, 'c6'),
                            )
                        },
                    {
                        'type': 'error',
                        'info': '$*@Y#&*#&**#()!*#',
                        },
                    {
                        'type': 'info',
                        'info': 'good',
                        },
                    {
                        'type': 'table',
                        'name': 'tb',
                        'meta': ('a', 'b', 'c'),
                        'values': (
                            (1, -2., 'c3'),
                            (4, 5.5, 'c6'),
                            )
                        },
                    {
                        'type': 'table',
                        'name': 'tb',
                        'meta': ('a', 'b', 'c'),
                        'values': (
                            (1, -2., 'c3'),
                            (4, 5.5, 'c6'),
                            )
                        },
                    ]
                }
        self.write(result)

    def options(self):
        # no body
        self.set_status(204)
        self.finish()


class ExitHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "*")
        self.set_header('Access-Control-Allow-Methods', 'GET, OPTIONS')

    def get(self):
        self.write('ok')
        tornado.ioloop.IOLoop.current().stop()

    def options(self):
        # no body
        self.set_status(204)
        self.finish()


def make_app():
    return tornado.web.Application([
        (r'/', MainHandler),
        (r'/exit', ExitHandler),
    ])

def main():
    app = make_app()
    app.listen(30000)
    tornado.ioloop.IOLoop.current().start()

if __name__ == '__main__':
    main()
