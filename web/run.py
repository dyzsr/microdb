import tornado.ioloop
import tornado.web

import sys
import os

if __name__ == '__main__':
    sys.path.insert(0, os.path.abspath('../'))

from sql.sqlparser import parser
from pengine.logical_engine import *
from pengine.physical_engine import *
from iod.io_cache_manager import *
import json
import glo.glovar

print(glo.glovar.GlobalVar.dirPath)
glo.glovar.GlobalVar.dirPath = os.environ['HOME'] + '/micro_db_store'
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

            res = {
                    'type': 'error',
                    'info': str(err),
                    }
            results.append(res)
            parsingTrees = tuple()
            err = 'parsing error'
        finally:
       #     print('Parsing tree:')
       #     print(parsingTrees)
            pass

        def get_name(tree, data):
            if not data:
                return 'none'
            if tree['type'] == 'query' and tree['name'] == 'show' and tree['content']['type'] == 'database':
                return 'show databases'
            if tree['type'] == 'query' and tree['name'] == 'show' and tree['content']['type'] == 'table':
                return 'show tables'
            if tree['type'] == 'query' and tree['name'] == 'show' and tree['content']['type'] == 'columns':
                return 'show columns'
            return list(data[0].keys())[0]

        def get_meta(tree, data):
            if not data:
                return []
            if tree['type'] == 'query' and tree['name'] == 'show' and tree['content']['type'] == 'database':
                return ['databases']
            if tree['type'] == 'query' and tree['name'] == 'show' and tree['content']['type'] == 'table':
                return ['tables']
            new_data = list()
            num = len(list(data[0].values()))
            for i in range(num):
                new_data.extend(data[i].values())
            return list(list(data[0].values())[0].keys())

        def get_values(tree, data):
            if not data:
                return []
            if tree['type'] == 'query' and tree['name'] == 'show' and tree['content']['type'] == 'database':
                return list(map(lambda x:[x], data))
            if tree['type'] == 'query' and tree['name'] == 'show' and tree['content']['type'] == 'table':
                return list(map(lambda x:[x], data))
            values = [ list(list(x.values())[0].values()) for x in data ]
            return values

        # Do queries
        for tree in parsingTrees:
            print('Parsing tree:')
            print(json.dumps(tree, indent=2), end='\n\n')
            if not tree:
                continue

            logres = LogicalEngine.run_logical_main(tree)
            phyres = PhysicalBlock.dfs_plan_tree(logres)

            #print(json.dumps(phyres.data, indent=2))

            res = {}
            if phyres.flag == True:
                res['type'] = 'error'
                res['info'] = phyres.result
            else:
                if len(phyres.result) > 0 and len(phyres.data) == 0:
                    res['type'] = 'info'
                    res['info'] = phyres.result
                else:
                    res['type'] = 'table'
                    res['name'] = get_name(tree, phyres.data)
                    print(json.dumps(res['name'], indent=2))
                    res['meta'] = get_meta(tree, phyres.data)
                    print(json.dumps(res['meta'], indent=2))
                    res['values'] = get_values(tree, phyres.data)
                    print(json.dumps(res['values'], indent=2))

            results.append(res)
            print(json.dumps(res, indent=2), end='\n\n')

        result = {'results': results}
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
        print('Saving data...')
        IoCacheManager.quit_main()
        print('Finished.')
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
    print('Exit DB.')

if __name__ == '__main__':
    main()
