# SQL Parser

## 1.说明

将输入的SQL语句解析为语法树（嵌套的Python字典）。

## 2.语法树结构

### 2.1 查询

``` py
{
  'type': 'query',
  'name': <query name>,
  'content': {...},
}
```

**注**：我们用「」来表示可选的项。

### 2.2 表

``` py
{
  'type': 'table',
  'name': <table name>,
  「 'source': {...}, 」
}
```

`source`的内容可以是一个查询。
如果不嵌套查询，则无`source`字段。

### 2.3 列

``` py
{
  'type': 'column',
  'name': <column name>,
  「 'table': <table name>, 」
}
```

如果不指定`table`（形如table.column），则无`table`字段。

## 3. SELECT语句

``` sql
SELECT ... FROM ... 「 WHERE ... 」;
```

``` py
{
  'type': 'query',
  'name': 'select',
  'content': {
    'tables': (),
    'columns': (),
    「 'filters': {}, 」
  }
}
```

### 普通查询

``` sql
SELECT c1, b.c2 FROM a, b;
```

``` py
{
  'type': 'query', 
  'name': 'select', 
  'content': {
    'tables': (
      {'type': 'table', 'name': 'a'}, 
      {'type': 'table', 'name': 'b'}
    ), 
    'columns': (
      {'type': 'column', 'name': 'c1'}, 
      {'type': 'column', 'name': 'c2', 'table': 'b'}
    )
  }
}
```

### 含有*的查询（查询所有列）

``` sql
SELECT * FROM a, b;
```

``` python
{
  'type': 'query', 
  'name': 'select', 
  'content': {
    'tables': (
      {'type': 'table', 'name': 'a'}, 
      {'type': 'table', 'name': 'b'}
    ), 
    'columns': ('*',)
  }
}
```

### 含有WHERE的查询

``` sql
SELECT c1 
FROM a, b 
WHERE a.c2 = b.c3 AND b.c3 > 100;
```

``` py
{
  'type': 'query', 
  'name': 'select', 
  'content': {
    'tables': (
      {'type': 'table', 'name': 'a'}, 
      {'type': 'table', 'name': 'b'}
    ), 
    'columns': (
      {'type': 'column', 'name': 'c1'},
    ), 
    'filters': {
      'type': 'opexpr', 
      'operator': 'and', 
      'operands': (
        {
          'type': 'opexpr', 
          'operator': '=', 
          'operands': (
            {'type': 'column', 'name': 'c2', 'table': 'a'}, 
            {'type': 'column', 'name': 'c3', 'table': 'b'}
          )
        }, 
        {
          'type': 'opexpr', 
          'operator': '>', 
          'operands': (
            {'type': 'column', 'name': 'c3', 'table': 'b'}, 
            100
          )
        }
      )
    }
  }
}
```

### 含有嵌套的查询

``` sql
SELECT c1, c2 
FROM (SELECT * FROM a WHERE c1 + c2 > 1000) AS t;
```

``` py
{
  'type': 'query', 
  'name': 'select', 
  'content': {
    'tables': (
      {
        'type': 'table', 
        'name': 't', 
        'source': {
          'type': 'query', 
          'name': 'select', 
          'content': {
            'tables': (
              {'type': 'table', 'name': 'a'},
            ), 
            'columns': ('*',), 
            'filters': {
              'type': 'opexpr', 
              'operator': '>', 
              'operands': (
                {
                  'type': 'opexpr', 
                  'operator': '+', 
                  'operands': (
                    {'type': 'column', 'name': 'c1'}, 
                    {'type': 'column', 'name': 'c2'}
                  )
                }, 
                1000
              )
            }
          }
        }
      },
    ), 
    'columns': (
      {'type': 'column', 'name': 'c1'}, 
      {'type': 'column', 'name': 'c2'}
    )
  }
}
```

## 4. CREATE语句

``` sql
CREATE DATABASE <database-name>;
```

``` py
{
  'type': 'query',
  'name': 'create',
  'content': {
    'type': 'database',
    'name': <database-name>
  }
}
```

``` sql
CREATE TABLE <table-name> (
  <column1> <column_type> 「 <constraint1>, ... 」,
  ...,
  「 <constraint1>, ... 」
);
```

``` py
{
  'type': 'query',
  'name': 'create',
  'content': {
    'type': 'table',
    'name': <table-name>
    'columns': (),
    'constraints': {},
  }
} 
```

### 4.1 CREATE DATABASE

``` sql
CREATE DATABASE db1;
```

``` py
{
  'type': 'query', 
  'name': 'create', 
  'content': {
    'type': 'database', 
    'name': 'db1'
  }
}
```

### 4.2 CREATE TABLE

``` sql
CREATE TABLE hehe (
  a INT NOT NULL, 
  b VARCHAR(10), 
  c BOOLEAN, 
  PRIMARY KEY(a, c)
);
```

``` py
{
  'type': 'query', 
  'name': 'create', 
  'content': {
    'type': 'table', 
    'name': 'hehe', 
    'columns': (
      {'type': 'column', 'name': 'a', 'datatype': {'typename': 'int'}}, 
      {'type': 'column', 'name': 'b', 'datatype': {'typename': 'varchar', 'length': 10}}, 
      {'type': 'column', 'name': 'c', 'datatype': {'typename': 'bool'}}
    ), 
    'constraints': {
      'primary key': ('a', 'c'), 
      'not null': ('a',)
    }
  }
}
```

## 5. INSERT语句

``` sql
INSERT INTO <table-name> 
「 (col1, col2, ...) 」
VALUES
(val1, val2, ...)
「 , (...), ... 」
;
```

``` py
{
  'type': 'query', 
  'name': 'insert', 
  'content': {
    'type': 'values', 
    'tablename': <table-name>, 
    「 'columns': (<col1>, ...), 」
    'values': (<val1>, ...),
  }
}
```

``` sql
INSERT INTO <table-name>
SET <col1-name> = <expression>
「 ，<col2-name> = <expression> 」;
```

``` py
{
  'type': 'query', 
  'name': 'insert', 
  'content': {
    'type': 'set', 
    'tablename': <table-name>, 
    「 'columns': (<col1>, ...), 」
    'values': (<val1>, ...),
  }
}
```

### 5.1 INSERT VALUES

``` sql
INSERT INTO tb VALUES
(1, 2.2, TRUE, 'abc'), 
(-1, -.1, FALSE, 'def');
```

``` py
{
  'type': 'query', 
  'name': 'insert', 
  'content': {
    'type': 'values', 
    'tablename': 'tb', 
    'values': (
      (1, 2.2, True, 'abc'), 
      (
        {
          'type': 'opexpr', 
          'operator': 'uminus', 
          'operands': (1,)
        }, 
        {
          'type': 'opexpr', 
          'operator': 'uminus', 
          'operands': (0.1,)
        }, 
        False, 
        'def'
      )
    )
  }
}
```

``` sql
INSERT INTO tb (c1, c2) VALUES (1, 3);
```

``` py
{
  'type': 'query', 
  'name': 'insert', 
  'content': {
    'type': 'values', 
    'tablename': 'tb', 
    'columns': ('c1', 'c2'), 
    'values': ((1, 3),)
  }
}
```

### 5.2 INSERT SET

``` sql
INSERT INTO tb 
SET c1 = 1, c2 = c3 * (c5 + c6);
```

``` py
{
  'type': 'query', 
  'name': 'insert', 
  'content': {
    'type': 'set', 
    'set': (
      {
        'column': {'type': 'column', 'name': 'c1'}, 
        'opexpr': 1
      }, 
      {
        'column': {'type': 'column', 'name': 'c2'}, 
        'opexpr': {
          'type': 'opexpr', 
          'operator': '*', 
          'operands': (
            {
              'type': 'column', 
              'name': 'c3'
            }, 
            {
              'type': 'opexpr', 
              'operator': '+', 
              'operands': (
                {'type': 'column', 'name': 'c5'}, 
                {'type': 'column', 'name': 'c6'}
              )
            }
          )
        }
      }
    )
  }
}
```