from parser import parser

if __name__ == '__main__':
    while True:
        try:
            s = input('> ')
        except EOFError:
            break
        parser.parse(s)

