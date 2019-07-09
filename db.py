from sql.sqlparser import parser
import json

if __name__ == '__main__':
    while True:
        try:
            s = input('> ')
        except EOFError:
            break
        res = parser.parse(s)
        print(json.dumps(res, indent = 2))
        print(type(res))
