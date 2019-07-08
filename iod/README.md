## 数据存储格式说明

简单借助文件存储系统完成数据库的的存储系统
目录的组成: 根目录 + 数据库名 + 表名
其中：
   - 根目录: D:\dbms\store
   
每个表的文件下下存在一个存储表的元信息的文件，名称为metadata。
元信息格式：
```
{
    "column": , 
    "datatype": "int"/"vachar(x)"/, 
    "primary": true/false,
    "null": true/false}
}
```
目前数据库表中数据的存储格式为json,按照*行*区分条目。当前还没有做索引系统。数据统一存储在表目录下的data文件中。
