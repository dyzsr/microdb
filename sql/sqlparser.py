from collections import defaultdict

# micro SQL parser

RESERVED = {
        'create'    : 'CREATE',
        'database'  : 'DATABASE',
        'table'     : 'TABLE',

        'boolean'   : 'BOOLTYPE',
        'int'       : 'INTTYPE',
        'float'     : 'FLOATTYPE',
        'varchar'   : 'VARCHAR',
        'nvarchar'  : 'NVARCHAR',

        'primary'   : 'PRIMARY',
        'key'       : 'KEY',
        
        'insert'    : 'INSERT',
        'into'      : 'INTO',
        'values'    : 'VALUES',
        'select'    : 'SELECT',
        'from'      : 'FROM',
        'where'     : 'WHERE',
        'groupby'   : 'GROUPBY',
        'having'    : 'HAVING',
        'as'        : 'AS',
        'in'        : 'IN',

        'and'       : 'AND',
        'or'        : 'OR',
        'not'       : 'NOT',
        'if'        : 'IF',
        'exists'    : 'EXISTS',
        'null'      : 'NULL',
        }


# ============= tokens ===============

tokens = tuple(RESERVED.values()) + (
        'BOOL',
        'FLOAT',
        'INT',
        'STRING',
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
t_EQ = r'='
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

def t_BOOL(t):
    r'(?i)(true|false)\b'
    t.value = True if t.value == 'true' else False
    return t

def t_FLOAT(t):
    r'(\d+\.\d*)|(\d*\.\d+)'
    t.value = float(t.value)
    return t

def t_INT(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_STRING(t):
    r"'([^\\']+|\\'|\\\\)*'"
    return t

t_ignore = ' \t\r\v'

def t_newline(t):
    r'\n'

def t_error(t):
    print('Unidentified symbol "%s"' % t.value)
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

# Select statement

def p_statement_select(p):
    'statement : selectexpr SEMICOLON' 
    p[0] = p[1]
    print(p[0])
    


# select expression

def p_selectexpr_nofilter(p):
    'selectexpr : SELECT columnlist FROM tablelist'
    p[0] = {
            'type': 'query',
            'name': 'select',
            'content': {'tables': p[4], 'columns': p[2]}
            }

def p_selectexpr_where(p):
    'selectexpr : SELECT columnlist FROM tablelist WHERE filterlist'
    p[0] = {
            'type': 'query',
            'name': 'select',
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
    p[0] = {
            'type': 'column', 
            'name': p[1]
            }

def p_column_tablename(p):
    'column : ID DOT ID'
    p[0] = {
            'type': 'column', 
            'name': p[3], 
            'table': p[1]
            }


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
    p[0] = {
            'type': 'table', 
            'name': p[1]
            }

def p_table_expr(p):
    'table : LPAR selectexpr RPAR AS ID'
    p[0] = {
            'type': 'table', 
            'name': p[5], 
            'source': p[2]
            }


## generate expressions combination

def make_expr(operator, *operands):
    return {'type': 'opexpr', 
            'operator': operator, 
            'operands': operands}

#_opmap = {'ADD': '+', 'SUB': '-', 'MUL': '*', 'DIV': '/'}

def opname(operator):
#    if operator in _opmap:
#        return _opmap[operator]
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
              | BOOL
              | INT
              | FLOAT
              | STRING
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


# Create statement ********************

def p_statement_create(p):
    'statement : createexpr SEMICOLON'
    p[0] = p[1]
    print(p[0])

def p_createexpr_database(p):
    'createexpr : CREATE DATABASE ID'
    p[0] = {
            'type': 'query',
            'name': 'create',
            'content': {
                'type': 'database',
                'name': p[3],
                },
            }

def p_createexpr_table(p):
    '''
    createexpr : CREATE TABLE ID \
                 LPAR coldeflist RPAR
    '''
    p[0] = {
            'type': 'query',
            'name': 'create',
            'content': {
                'type': 'table',
                'name': p[3],
                'columns': p[5]['columns'],
                'constraints': p[5]['constraints'],
                },
            }

# column defination list

def merge_constraints(c1, c2):
    res = {}
    res['primary key'] = c1['primary key'] + c2['primary key']
    return res


def p_coldeflist_columns(p):
    '''
    coldeflist : columndef
               | columndef COMMA coldeflist
    '''
    columndef = {
            'type': p[1]['type'],
            'name': p[1]['name'],
            'datatype': p[1]['datatype'],
            }
    if len(p) == 2:
        p[0] = {
                'columns': (columndef,),
                'constraints': p[1]['constraints'],
                }
    else:
        new_constraints = merge_constraints(p[1]['constraints'], p[3]['constraints'])
        p[0] = {
                'columns': (columndef,) + p[3]['columns'],
                'constraints': new_constraints
                }

def p_coldeflist_constraints(p):
    'coldeflist : constraints'
    p[0] = {'columns': tuple(), 'constraints': p[1]}


# column defination

def p_columndef(p):
    '''
    columndef : ID datatype
              | ID datatype PRIMARY KEY
    '''
    p[0] = {
            'type': 'column',
            'name': p[1],
            'datatype': p[2],
            'constraints': defaultdict(tuple),
            }
    if len(p) > 3 and p[3] == 'primary':
        p[0]['constraints']['primary key'] = tuple(p[1])


# table constraints

def p_constraints_primary_key(p):
    '''
    constraints : PRIMARY KEY LPAR pklist RPAR
    '''
    p[0] = defaultdict(tuple, {'primary key': tuple(p[4])})

# primary keys
def p_pklist(p):
    '''
    pklist : ID
           | ID COMMA pklist
    '''
    if len(p) == 2:
        p[0] = tuple(p[1])
    else:
        p[0] = tuple(p[1]) + p[3]

# datatypes

def p_datatype(p):
    '''
    datatype : BOOLTYPE 
             | INTTYPE 
             | FLOATTYPE 
             | VARCHAR LPAR INT RPAR
             | NVARCHAR LPAR INT RPAR
    '''
    if p[1] == 'boolean':
        p[0] = {'typename': 'bool'}
    elif p[1] == 'int':
        p[0] = {'typename': 'int'}
    elif p[1] == 'float':
        p[0] = {'typename': 'float'}
    elif p[1] == 'varchar':
        p[0] = {'typename': 'varchar', 'length': p[3]}
    elif p[1] == 'nvarchar':
        p[0] = {'typename': 'nvarchar', 'length': p[3]}



# parsing error

def p_error(p):
    print('Syntax error at "%s"' % p.value)

# build the parser
from ply import yacc
parser = yacc.yacc()

