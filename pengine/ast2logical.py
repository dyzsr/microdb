from sql.sqlparser import parser
from pengine.logical_engine import *
import json
import glo.glovar

if __name__ == '__main__':
    while True:
        try:
            s = input('> ')
        except EOFError:
            break
        ans = LogicalEngine.run_logical_main(parser.parse(s))
        print('[Info] [finish ast2log]', ans)
