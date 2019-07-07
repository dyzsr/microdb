

## 关系代数树生成的设计

输入: 语法分析结果，为一个dict,内部可嵌套多个dict

For "query":

| key | value |
| - | - |
| type | 'query' | 
| name | 'select','create','insert' |
| content | 如下定义 |

For "content" :

| key | value | 
| - | - |
| tables | List<table> |
| columns | List<columns> | 
| filters |  | 

For "table" :
| key | value |
| - | - |
| type | 'table' |
| name | table_name |
| *source | query | 


## 关系代数树数据结构

使用dict数据结构
.type
.lson
.rson

### 对于投影

| key | value |
| - | - |
| type | map |
| columns | list<columns_name> |
| 内容 | 对于一个表选择出想要的列 | 

特别的，当columns=*时输出所有的列

### 对于连接

| key | value |
| - | - | 
| type | join |
| tables | list<query> |
| 内容 | 从数据库中选出表 |

### 对于选择
| key | value |
| - | - |
| type | limit |
| value | check_tree_root |
| 内容 | 一棵条件包括判断的树,称为判断树 |

### 关于数据（表）
| key | value |
| - | - |
| type | table |
| value | table_name |
| 内容 | 表 |

#### check_tree判断树数据结构
```
class CheckTreeNode{
    .type = 'and','or','not','=','>','<','leaf','+','-'
    .lson = 如果是and或者or,或者not
    .rson = 如果是and或者or，
    .value = 如果是leaf,那么是个dict，存在两种情况：列和真值
        .value['type']=column,选出列
        .value['type']=value,得到值
    def check_data_main(data)
        return check_data(data)!=0
}
```

```
not (((a = b) or (c >d )) and (d<e))
```

### ast2log结果

```
SELECT c1, b.c2 FROM a, b;

SELECT * FROM a, b;

SELECT c1 FROM a, b WHERE a.c2 = b.c3 AND b.c3 > 100;

SELECT c1, c2 FROM (SELECT * FROM a WHERE c1 + c2 > 1000) AS t;

CREATE DATABASE db1;

CREATE TABLE hehe (a INT NOT NULL, b VARCHAR(10), c BOOLEAN, PRIMARY KEY(a, c));

INSERT INTO tb VALUES (1, 2.2, TRUE, 'abc'), (-1, -.1, FALSE, 'def');

UPDATE tb SET c1 = c2 + c3;

UPDATE tb SET c1 = -2.4 WHERE c2 = TRUE;

DELETE FROM tb;

DELETE FROM tb WHERE c1 > 50000;

DROP DATABASE abc;

DROP TABLE tb1, tb2;
```