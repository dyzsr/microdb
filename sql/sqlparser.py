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
        'set'       : 'SET',

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
        'LPAR',
        'RPAR',
        'LT',
        'LTE',
        'GT',
        'GTE',
        'EQ',
        'NE',
        'PLUS',
        'MINUS',
        'MUL',
        'DIV',
        'UMINUS',
        )


t_SEMICOLON = r';'
t_DOT = r'\.'
t_COMMA = r','
t_LPAR = r'\('
t_RPAR = r'\)'
t_LT = r'<'
t_LTE = r'<='
t_GT = r'>'
t_GTE = r'>='
t_EQ = r'='
t_NE = r'!='
t_PLUS = r'\+'
t_MINUS = r'-'
t_MUL = r'\*'
t_DIV = r'/'

def t_ID(t):
    r'[a-zA-Z_]\w*'
    t.value = t.value.lower()
    t.type = RESERVED.get(t.value, 'ID')

    if t.value == 'true':
        t.value = True
        t.type = 'BOOL'
    elif t.value == 'false':
        t.value = False
        t.type = 'BOOL'

    return t


# def t_BOOL(t):
#     r'((?i)(true))|((?i)(false))'
#     t.value = True if t.value.lower() == 'true' else False
#     return t

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
    t.value = t.value.strip("'")
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
        ('left', 'PLUS', 'MINUS'),
        ('left', 'MUL', 'DIV'),
        ('right', 'UMINUS'),
        )

# dictionary of IDifiers
IDs = {}

#============ rules ==================

# Select statement

def p_statement_select(p):
    'statement : selectexpr SEMICOLON' 
    p[0] = p[1]
    print(p[0])
    return p[0]
    


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
    columnlist : MUL
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

def make_opexpr(operator, *operands):
    return {'type': 'opexpr', 
            'operator': operator, 
            'operands': operands}

#_opmap = {'PLUS': '+', 'MINUS': '-', 'MUL': '*', 'DIV': '/'}

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
    p[0] = make_opexpr(opname(p[2]), p[1], p[3])

def p_filterlist_not(p):
    'filterlist : NOT filterlist'
    p[0] = make_opexpr('not', p[2])


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
    p[0] = make_opexpr(opname(p[2]), p[1], p[3])



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

def p_colopexpr_uminus(p):
    '''
    colopexpr : MINUS colopexpr %prec UMINUS
    '''
    p[0] = make_opexpr('uminus', p[2])

def p_colopexpr_parthesis(p):
    'colopexpr : LPAR colopexpr RPAR'
    p[0] = p[2]

def p_colopexpr_binop(p):
    '''
    colopexpr : colopexpr PLUS colopexpr
              | colopexpr MINUS colopexpr
              | colopexpr MUL colopexpr
              | colopexpr DIV colopexpr
    '''
    p[0] = make_opexpr(opname(p[2]), p[1], p[3])


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
    res['not null'] = c1['not null'] + c2['not null']
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
              | ID datatype colconstraintlist
    '''
    p[0] = {
            'type': 'column',
            'name': p[1],
            'datatype': p[2],
            'constraints': defaultdict(tuple),
            }
    #if len(p) > 3 and p[3] == 'primary':
    #    p[0]['constraints']['primary key'] = (p[1],)
    if len(p) == 4:
        for key in p[3]:
            p[0]['constraints'][key] = (p[1],)


def p_colconstraintlist(p):
    '''
    colconstraintlist : colconstraint
                      | colconstraint colconstraintlist
    '''
    if len(p) == 2:
        p[0] = (p[1],)
    else:
        p[0] = (p[1],) + p[2]

def p_colconstraint(p):
    '''
    colconstraint : PRIMARY KEY
               | NOT NULL
    '''
    if p[1] == 'primary' and p[2] == 'key':
        p[0] = 'primary key'
    elif p[1] == 'not' and p[2] == 'null':
        p[0] = 'not null'


# table constraints

def p_constraints_primary_key(p):
    '''
    constraints : PRIMARY KEY LPAR pklist RPAR
    '''
    p[0] = defaultdict(tuple, {'primary key': p[4]})

# primary keys
def p_pklist(p):
    '''
    pklist : ID
           | ID COMMA pklist
    '''
    if len(p) == 2:
        p[0] = (p[1],)
    else:
        p[0] = (p[1],) + p[3]

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


# INSERT statement

def p_statement_insert(p):
    'statement : insertexpr SEMICOLON'
    p[0] = p[1]
    print(p[0])
    return p[0]

# INSERT expressions

# insert into table values
def p_insertexpr_values_all(p):
    '''
    insertexpr : INSERT INTO ID VALUES \
            valuelist
    '''
    p[0] = {
            'type': 'query',
            'name': 'insert',
            'content': {
                'type': 'values',
                'tablename': p[3],
                'values': p[5],
                }
            }

def p_insertexpr_values_some(p):
    '''
    insertexpr : INSERT INTO ID \
            LPAR colnamelist RPAR \
            VALUES valuelist
    '''
    p[0] = {
            'type': 'query',
            'name': 'insert',
            'content': {
                'type': 'values',
                'tablename': p[3],
                'columns': p[5],
                'values': p[8],
                }
            }

def p_colnamelist(p):
    '''
    colnamelist : ID
                | ID COMMA colnamelist
    '''
    if len(p) == 2:
        p[0] = (p[1],)
    else:
        p[0] = (p[1],) + p[3]


def p_valuelist(p):
    '''
    valuelist : LPAR values RPAR
              | LPAR values RPAR COMMA valuelist
    '''
    if len(p) == 4:
        p[0] = (p[2],)
    else:
        p[0] = (p[2],) + p[5]

def p_values(p):
    '''
    values : value
           | value COMMA values
    '''
    if len(p) == 2:
        p[0] = (p[1],)
    else:
        p[0] = (p[1],) + p[3]
        

def p_value(p):
    '''
    value : BOOL
          | INT 
          | FLOAT 
          | STRING
    '''
    p[0] = p[1]

def p_value_parenthesis(p):
    '''
    value : LPAR value RPAR
    '''
    p[0] = p[1]

def p_value_opexpr(p):
    '''
    value : value PLUS value
          | value MINUS value
          | value MUL value
          | value DIV value
    '''
    p[0] = make_opexpr(p[2], p[1], p[3])

def p_value_uminus(p):
    '''
    value : MINUS value %prec UMINUS
    '''
    p[0] = make_opexpr('uminus', p[2])


# insert into table set
def p_insertexpr_set(p):
    '''
    insertexpr : INSERT INTO ID \
            SET colsetlist
    '''
    p[0] = {
            'type': 'query',
            'name': 'insert',
            'content': {
                'type': 'set',
                'set': p[5],
                }
            }

def p_colsetlist(p):
    '''
    colsetlist : colset
               | colset COMMA colsetlist
    '''
    if len(p) == 2:
        p[0] = (p[1],)
    else:
        p[0] = (p[1],) + p[3]

def p_colset(p):
    '''
    colset : column EQ colopexpr
    '''
    p[0] = {
            'column': p[1],
            'opexpr': p[3]
            }


# parsing error

def p_error(p):
    print('Syntax error at "{}" of type "{}"'.format(p.value, p.type))


# build the parser
from ply import yacc
parser = yacc.yacc()

