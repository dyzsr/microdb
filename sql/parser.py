# micro SQL parser

from ply import yacc

RESERVED = {
        'select' : 'SELECT',
        'from'   : 'FROM',
        'where'  : 'WHERE',
        'as'     : 'AS',
        }
        


tokens = tuple(RESERVED.values()) + (
        'INT',# 'VARCHAR', 'NVARCHAR',
        'ID',
        'SEMICOLON',
        'DOT',
        'COMMA',
        'STAR',
        'LPAR',
        'RPAR',
        )

# tokens

t_SEMICOLON = r';'
t_DOT = r'\.'
t_COMMA = r','
t_STAR = r'\*'
t_LPAR = r'\('
t_RPAR = r'\)'

def t_ID(t):
    r'[a-zA-Z_]\w*'
    t.value = t.value.lower()
    t.type = RESERVED.get(t.value, 'ID')
    return t

def t_INT(t):
    r'\d+\b'
    t.value = int(t.value)
    return t

t_ignore = ' \n\t\r\v'

def t_error(t):
    print('UnIDified symbol "%s"' % t.value)
    t.lexer.skip(len(t.value))

# build the lexer
from ply import lex
lexer = lex.lex()

# set precedence rules
precedence = ()

# dictionary of IDifiers
IDs = {}

# rules

def p_statement_select(p):
    'statement : exprselect SEMICOLON' 
    p[0] = {'query': 'select', 'content': p[1]}
    print(p[0])
    

# select expression

def p_exprselect_nowhere(p):
    'exprselect : SELECT columnlist FROM tablelist'
    p[0] = {'tables': p[4], 'columns': p[2]}

def p_exprselect_where(p):
    'exprselect : SELECT columnlist FROM tablelist WHERE filterlist'
    p[0] = {'tables': p[4], 'columns': p[2], 'filters': p[6]}


def p_columnlist(p):
    '''
    columnlist : STAR
               | column
               | column COMMA columnlist
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]

def p_column(p):
    'column : ID'
    p[0] = {'name': p[1]}

def p_column_tablename(p):
    'column : ID DOT ID'
    p[0] = {'table': p[1], 'name': p[3]}

def p_tablelist(p):
    '''
    tablelist : table
              | table COMMA tablelist
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]

def p_table(p):
    'table : ID'
    p[0] = {'name': p[1]}

def p_table_expr(p):
    'table : LPAR exprselect RPAR AS ID'
    p[0] = {'name': p[5], 'expr': p[2]}

def p_filterlist(p):
    'filterlist : INT'
    p[0] = 'filters'


def p_error(p):
    print('Syntax error at "%s"' % p.value)

# build the parser
from ply import yacc
parser = yacc.yacc()

