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

## 3. Select语句

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
WHERE a.c2 == b.c3 AND b.c3 > 100;
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
          'operator': '==', 
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