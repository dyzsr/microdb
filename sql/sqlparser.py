# micro SQL parser

RESERVED = {
        'select'  : 'SELECT',
        'from'    : 'FROM',
        'where'   : 'WHERE',
        'groupby' : 'GROUPBY',
        'having'  : 'HAVING',
        'as'      : 'AS',
        'in'      : 'IN',
        'and'     : 'AND',
        'or'      : 'OR',
        'not'     : 'NOT',
        }


# ============= tokens ===============

tokens = tuple(RESERVED.values()) + (
        'INT',
        # 'VARCHAR',
        # 'NVARCHAR',
        'ID',
        'SEMICOLON',
        'DOT',
        'COMMA',
        'STAR',
        'LPAR',
        'RPAR',
        'LT',
        'LTE',
        'GT',
        'GTE',
        'EQ',
        'NE',
        'ADD',
        'SUB',
        'MUL',
        'DIV',
        )


t_SEMICOLON = r';'
t_DOT = r'\.'
t_COMMA = r','
t_STAR = r'\*'
t_LPAR = r'\('
t_RPAR = r'\)'
t_LT = r'<'
t_LTE = r'<='
t_GT = r'>'
t_GTE = r'>='
t_EQ = r'=='
t_NE = r'!='
t_ADD = r'\+'
t_SUB = r'-'
t_MUL = r'\*'
t_DIV = r'/'

def t_ID(t):
    r'[a-zA-Z_]\w*'
    t.value = t.value.lower()
    t.type = RESERVED.get(t.value, 'ID')
    return t

def t_INT(t):
    r'\d+\b'
    t.value = int(t.value)
    return t

t_ignore = ' \t\r\v'

def t_newline(t):
    r'\n'

def t_error(t):
    print('UnIDified symbol "%s"' % t.value)
    t.lexer.skip(len(t.value))

# build the lexer
from ply import lex
lexer = lex.lex()

# Parser
# set precedence rules

precedence = (
        ('left', 'OR'),
        ('left', 'AND'),
        ('right', 'NOT'),
        ('left', 'ADD', 'SUB'),
        ('left', 'MUL', 'DIV'),
        )

# dictionary of IDifiers
IDs = {}

#============ rules ==================

# Query select

def p_statement_select(p):
    'statement : selectexpr SEMICOLON' 
    p[0] = p[1]
    print(p[0])
    

# select expression

def p_selectexpr_nofilter(p):
    'selectexpr : SELECT columnlist FROM tablelist'
    p[0] = {
            'query': 'select',
            'content': {'tables': p[4], 'columns': p[2]}
            }

def p_selectexpr_where(p):
    'selectexpr : SELECT columnlist FROM tablelist WHERE filterlist'
    p[0] = {
            'query': 'select',
            'content': {'tables': p[4], 'columns': p[2], 'filters': p[6]}
            }


# column list

def p_columnlist(p):
    '''
    columnlist : STAR
               | column
               | column COMMA columnlist
    '''
    if len(p) == 2:
        p[0] = (p[1],)
    else:
        p[0] = (p[1],) + p[3]

def p_column(p):
    'column : ID'
    p[0] = {'name': p[1]}

def p_column_tablename(p):
    'column : ID DOT ID'
    p[0] = {'table': p[1], 'name': p[3]}


# table list

def p_tablelist(p):
    '''
    tablelist : table
              | table COMMA tablelist
    '''
    if len(p) == 2:
        p[0] = (p[1],)
    else:
        p[0] = (p[1],) + p[3]

def p_table(p):
    'table : ID'
    p[0] = {'name': p[1]}

def p_table_expr(p):
    'table : LPAR selectexpr RPAR AS ID'
    p[0] = {'name': p[5], 'expr': p[2]}


## generate expressions combination

def make_expr(operator, *operands):
    return {'operator': operator, 'operands': operands}

_opmap = {'ADD': '+', 'SUB': '-', 'MUL': '*', 'DIV': '/'}

def opname(operator):
    if operator in _opmap:
        return _opmap[operator]
    return operator.lower()


# filter list

def p_filterlist_filter(p):
    'filterlist : filter'
    p[0] = p[1]

def p_filterlist_parthesis(p):
    'filterlist : LPAR filterlist RPAR'
    p[0] = p[2]

def p_filterlist_andor(p):
    '''
    filterlist : filterlist AND filterlist
               | filterlist OR  filterlist
    '''
    p[0] = make_expr(opname(p[2]), p[1], p[3])

def p_filterlist_not(p):
    'filterlist : NOT filterlist'
    p[0] = make_expr('not', p[2])


# a single filter

def p_filter(p):
    '''
    filter : colopexpr LT colopexpr
           | colopexpr LTE colopexpr
           | colopexpr GT colopexpr
           | colopexpr GTE colopexpr
           | colopexpr EQ colopexpr
           | colopexpr NE colopexpr
    '''
    p[0] = make_expr(opname(p[2]), p[1], p[3])



# column operation expression

def p_colopexpr_single(p):
    '''
    colopexpr : column
              | INT
    '''
    p[0] = p[1]

def p_colopexpr_parthesis(p):
    'colopexpr : LPAR colopexpr RPAR'
    p[0] = p[2]

def p_colopexpr_binop(p):
    '''
    colopexpr : colopexpr ADD colopexpr
              | colopexpr SUB colopexpr
              | colopexpr MUL colopexpr
              | colopexpr DIV colopexpr
    '''
    p[0] = make_expr(opname(p[2]), p[1], p[3])



# parsing error

def p_error(p):
    print('Syntax error at "%s"' % p.value)

# build the parser
from ply import yacc
parser = yacc.yacc()

