# SQL Parser

## 1. 说明

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

一个列可以是一个字典或者字面量（数值或字符串）。

``` py
{
  'type': 'column' | 'opexpr',
  'name': <column name>,
  「 'table': <table name>, 」
}
```

如果不指定`table`（形如table.column），则无`table`字段。

### 2.4 表达式

构造表达式的函数

``` py
 def make_opexpr(operator, *operands):
     return {'type': 'opexpr',
             'operator': operator,
             'operands': operands}
```

第二个和之后的参数被当作operands的元素传入，返回的opexpr字典中`operands`是一个元组。

``` py
{
  'type': 'opexpr', 
  'operator': <operator>, 
  'operands': (<operand1>, <operand2>, ...),
}
```

### 2.5 运算符的定义

| 操作 | 运算符 |
|---|---|
| 加 | `+` |
| 减 | `-` |
| 乘 | `*` |
| 除 | `/` |
| 取负值 | `uminus` |
| 小于 | `<` |
| 小于等于 | `<=` |
| 大于 | `>` |
| 大于等于 | `>=` |
| 等于 | `=` |
| 不等于 | `!=` |
| 与 | `and` |
| 或 | `or`  |
| 非 | `not` |


## 3. SELECT语句

``` sql
SELECT ... 「 FROM ... 「 WHERE ... 」」;
```

``` py
{
  'type': 'query',
  'name': 'select',
  'content': {
    'columns': (),
    「 'tables': (), 」
    「 'filters': {}, 」
  }
}
```

### 只含有 SELECT

``` sql
SELECT 1 + (-1);
```

``` py
{
  'type': 'query', 
  'name': 'select', 
  'content': {
    'columns': (
      {
        'type': 'opexpr', 
        'operator': '+', 
        'operands': (
          1, 
          {
            'type': 'opexpr', 
            'operator': 'uminus', 
            'operands': (1,)
          }
        )
      },
    )
  }
}
```

### 普通查询 SELECT FROM

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

### CREATE DATABASE

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

### CREATE TABLE

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

### INSERT VALUES

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

### INSERT SET

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

## 6. UPDATE语句

更新一张表中的数据

### 普通更新操作

``` sql
UPDATE tb SET c1 = c2 + c3;
```

``` py
{
  'type': 'query', 
  'name': 'update', 
  'content': {
    'tablename': 'tb', 
    'set': (
      {
        'column': {
          'type': 'column', 
          'name': 'c1'
         }, 
        'opexpr': {
          'type': 'opexpr', 
          'operator': '+', 
          'operands': (
            {'type': 'column', 'name': 'c2'}, 
            {'type': 'column', 'name': 'c3'}
          )
        }
      },
    )
  }
}
```

### 含有WHERE的更新

``` sql
UPDATE tb SET c1 = -2.4 WHERE c2 = TRUE;
```

``` py
{
  'type': 'query', 
  'name': 'update', 
  'content': {
    'tablename': 'tb', 
    'set': (
      {
        'column': {'type': 'column', 'name': 'c1'}, 
        'opexpr': {
          'type': 'opexpr', 
          'operator': 'uminus', 
          'operands': (2.4,)
        }
      },
    ), 
    'filters': {
      'type': 'opexpr', 
      'operator': '=', 
      'operands': (
        {'type': 'column', 'name': 'c2'}, 
        True
      )
    }
  }
}
```

## 7. DELETE语句

从一张表中删除数据

### 普通删除

``` sql
DELETE FROM tb;
```

``` py
{
  'type': 'query', 
  'name': 'delete', 
  'content': {
    'tablename': 'tb'
  }
}
```

### 含有WHERE的删除

``` sql
DELETE FROM tb WHERE c1 > 50000;
```

``` py
{
  'type': 'query', 
  'name': 'delete', 
  'content': {
    'tablename': 'tb', 
    'filters': {
      'type': 'opexpr', 
      'operator': '>', 
      'operands': (
        {'type': 'column', 'name': 'c1'}, 
        50000
      )
    }
  }
}
```


## 8. DROP语句

### DROP DATABASE

删除数据库

``` sql
DROP DATABASE abc;
```

``` py
{
  'type': 'query', 
  'name': 'drop', 
  'content': {
    'type': 'database', 
    'name': 'abc'
  }
}
```

### DROP TABLE

删除一张表

``` sql
DROP TABLE tb1, tb2;
```

``` py
{
  'type': 'query', 
  'name': 'drop', 
  'content': {
    'type': 'table', 
    'names': ('tb1', 'tb2')
  }
}
```