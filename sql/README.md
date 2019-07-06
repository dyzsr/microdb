# SQL Parser

## 说明

将输入的SQL语句解析为语法树（嵌套的Python字典）。

## 结构

``` Python
{
  'query': <query type>,
  'content': {...},
}
```

**注**：我们用「」来表示可选的项。

## Select语句

``` SQL
SELECT ... FROM ... [ WHERE ... ];
```

``` Python
{
  'query': 'select',
  'content': {
    'tables': (),
    'columns': (),
    「 'filters': {}, 」
  }
}
```

`columns`、`tables`均为元组。

`columns`的结构如下：

``` py
(
  {
    'name': <column name>, 
    「 'table': <table name> 」
  },
  ...
)
```

如果不指定`table`（形如table.column），则无`'table'`字段。

`tables`的结构如下：

``` py
(
  {
    'name': <table name>
    「
      'expr': {
        'query': <query type>,
        'content': {...}
      } 
    」
  }
)
```

如果不嵌套查询，则无`'expr'`字段。


### 普通查询

``` sql
SELECT c1, b.c2 FROM a, b;
```

``` py
{
  'query': 'select', 
  'content': {
    'tables': ({'name': 'a'}, {'name': 'b'}), 
    'columns': (
      {'name': 'c1'}, 
      {'table': 'b', 'name': 'c2'}
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
  'query': 'select',
  'content': {
    'tables': ({'name': 'a'}, {'name': 'b'}),
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
  'query': 'select', 
  'content': {
    'tables': ({'name': 'a'}, {'name': 'b'}), 
    'columns': ({'name': 'c1'},), 
    'filters': {
      'operator': 'and', 
      'operands': (
        {
          'operator': '==', 
          'operands': (
            {'table': 'a', 'name': 'c2'}, 
            {'table': 'b', 'name': 'c3'}
          )
        }, 
        {
          'operator': '>', 
          'operands': (
            {'table': 'b', 'name': 'c3'}, 
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
  'query': 'select', 
  'content': {
    'tables': (
      {
        'name': 't', 
        'expr': {
          'query': 'select', 
          'content': {
            'tables': ({'name': 'a'},), 
            'columns': ('*',), 
            'filters': {
              'operator': '>', 
              'operands': (
                {
                  'operator': '+', 
                  'operands': (
                    {'name': 'c1'}, 
                    {'name': 'c2'}
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
      {'name': 'c1'}, 
      {'name': 'c2'}
    )
  }
}
```