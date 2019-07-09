import sys
import os
if __name__ == '__main__':
    sys.path.insert(0, os.path.abspath('../'))

from sql.sqlparser import parser
import json

if __name__ == '__main__':
    while True:
        try:
            s = input('> ')
            res = parser.parse(s)
            print(json.dumps(res, indent = 2))
            print(type(res))
        except EOFError:
            break
        except Exception as err:
            print(err)
