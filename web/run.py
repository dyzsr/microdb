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

        def get_name(data):
            if not data:
                return 'none'
            if isinstance(data[0], str):
                return 'show'
            return data[0].items()[0][0]

        def get_meta(data):
            if not data:
                return []
            if isinstance(data[0], str):
                return ['tables']
            return list(map(lambda *x: x[0], data[0].items()[0][1]))

        def get_values(data):
            if not data:
                return []
            if isinstance(data[0], str):
                return list(map(lambda x: [x], data[:]))
            values = [ list(map(lambda *y: y[1], x.items()[0][1])) for x in data ]
            return values

        # Do queries
        for tree in parsingTrees:
            print('Parsing tree:')
            print(json.dumps(tree, indent=2), end='\n\n')

            logres = LogicalEngine.run_logical_main(tree)
            phyres = PhysicalBlock.dfs_plan_tree(logres)

            #print(json.dumps(phyres.data, indent=2))

            res = {}
            if phyres.flag == True:
                res['type'] = 'error'
                res['info'] = phyres.result
            else:
                if len(phyres.data) == 0:
                    res['type'] = 'info'
                    res['info'] = phyres.result
                else:
                    res['type'] = 'table'
                    print(json.dumps(get_name(phyres.data), indent=2))
                    print(json.dumps(get_meta(phyres.data), indent=2))
                    print(json.dumps(get_values(phyres.data), indent=2))

            print(json.dumps(res, indent=2))

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
