from sql.sqlparser import parser

if __name__ == '__main__':
    while True:
        try:
            s = input('> ')
        except EOFError:
            break
        print(type(parser.parse(s)))

