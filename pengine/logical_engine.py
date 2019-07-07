#
# -*- coding:utf-8 -*-
# 作者：Macaulish
# 创建：2019-07-05
# 作用：逻辑计划执行
# 主要涉及： 将表达式树转换为关系表达树
#
# 代码结构设计：语法树，
#
import operator as op
import re
import glo.glovar as glo


# node['type']
# ------ all
#               = 'table'
#               =
# ------ select
#               = 'map'
#               = 'join'
#               = 'limit'
#               = 'table'
# ------ create
#               = 'ct' create table
#               = 'cd' create database
# ------ insert
#               = 'iv' insert
# ------ update
#               = 'up'
# ------ delete
#               = 'del'
#

# 不知道算逻辑还是物理
class ExpTreeNode:
    # 默认申请的节点为真值
    def __init__(self, otype='value'):
        # 逻辑运算符: And, or, not
        # 算数运算符：+,-,*,/
        # 关系运算符：>,<,=,(<>? !=)
        # columns,value
        # columns= <lson:表名> , <rson:列名>
        self.type = otype
        self.lson = None
        self.rson = None
        return

    # 计算的过程
    def calc_data(self, data=None):
        if re.search(r'value', self.type):
            return self.lson
        if re.search(r'columns', self.type):
            if op.eq(self.lson, '*'):
                for (k, v) in data:
                    if self.rson in v.keys():
                        return v[self.rson]
            return data[self.lson][self.rson]
        # 一元运算符,二元运算符
        # 更新，直接用字符串
        # 逻辑运算符: And, or, not
        # 算数运算符：+,-,*,/
        # 关系运算符：>,<,=,(<>? !=)
        # todo: 合法性检验
        # And
        if re.search(r"and", self.type):
            return self.lson.calc_data(data) and self.rson.calc_data(data)
        # Or
        elif re.search(r"or", self.type):
            return self.lson.calc_data(data) or self.rson.calc_data(data)
        # Not
        elif re.search(r"not", self.type):
            return not self.lson.calc_data(data)
        # +
        elif re.search(r"\+", self.type):
            return self.lson.calc_data(data) + self.rson.calc_data(data)
        # -
        elif re.search(r"-", self.type):
            return self.lson.calc_data(data) - self.rson.calc_data(data)
        # *
        elif re.search(r"\*", self.type):
            return self.lson.calc_data(data) * self.rson.calc_data(data)
        # /
        elif re.search(r"/", self.type):
            return self.lson.calc_data(data) / self.rson.calc_data(data)
        elif re.search(r">", self.type):
            return self.lson.calc_data(data) > self.rson.calc_data(data)
        elif re.search(r"<", self.type):
            return self.lson.calc_data(data) < self.rson.calc_data(data)
        elif re.search(r"=", self.type):
            return self.lson.calc_data(data) == self.rson.calc_data(data)
        elif re.search(r"!=", self.type):
            return self.lson.calc_data(data) != self.rson.calc_data(data)
        elif re.search(r"uminus", self.type):
            return -self.lson.calc_data(data)

    def check_data_main(self, data):
        return self.calc_data(data) != 0

    #
    def debug_calc_tree(self):
        print('[Debug] [Calc Tree] [', self.type, 'lson', type(self.lson), 'rson', type(self.rson) ,']');
        if op.eq(self.type, 'value'):
            print('[Debug] [Calc Tree] [Value]', self.lson)
        elif op.eq(self.type, 'column'):
            print('[Debug] [Calc Tree] [Column]', self.lson, self.rson)
        elif re.match(r'\+|-|\*|\|and|or|>|<|=|!=', self.type):
            self.lson.debug_calc_tree()
            self.rson.debug_calc_tree()
        else:
            self.lson.debug_calc_tree()

    # 建树的过程
    @classmethod
    def make_calc_tree(cls, grammar_node):
        if glo.Debug == 1:
            print('[Debug] [make_check_tree] [input:', grammar_node,']')
        now_node = ExpTreeNode()
        if isinstance(grammar_node, dict):
            if op.eq(grammar_node['type'], 'opexpr'):
                oper = grammar_node['operator']
                now_node.type = oper
                if re.match(r'\+|-|\*|\|and|or|>|<|=|!=', oper):
                    if glo.Debug == 1:
                        print('[Debug] [make_check_tree] [re1]:', oper, ']')
                    now_node.lson = cls.make_calc_tree(grammar_node['operands'][0])
                    now_node.rson = cls.make_calc_tree(grammar_node['operands'][1])
                elif re.match(r'not|uminus', oper):
                    if glo.Debug == 1:
                        print('[Debug] [make_check_tree] [re2]:', oper, ']')
                    now_node.lson = cls.make_calc_tree(grammar_node['operands'][0])
                return now_node
            oper = grammar_node['type']
            now_node.type = oper
            if op.eq(oper, 'column'):
                if 'table' in grammar_node.keys():
                    now_node.lson = grammar_node['table']
                else:
                    now_node.lson = '*'
                now_node.rson = grammar_node['name']
        else:
            now_node.type = 'value'
            now_node.lson = grammar_node
        return now_node


class LogicalEngine:
    node_total = 0

    def __init__(self):
        return

    # 直接对应一个表
    @staticmethod
    def table_transform(grammar_node):
        if glo.Debug == 1:
            print('[Debug] [LogicalEngine] [table_transform] [input:', grammar_node, ']')
        now_node = dict()
        now_node['type'] = 'table'
        now_node['name'] = grammar_node['name']
        return now_node

    # 处理select中的from
    @staticmethod
    def join_transform(grammar_node):
        if glo.Debug == 1:
            print('[Debug] [LogicalEngine] [join_transform] [input:', grammar_node, ']')
        now_node = dict()
        now_node['son'] = []
        now_node['type'] = 'join'
        for table in grammar_node:
            if 'source' in table:
                now_node['son'].append(LogicalEngine.dfs_grammar_tree(table['source']))
            else:
                now_node['son'].append(LogicalEngine.table_transform(table))
        return now_node

    # 处理select中的where
    @staticmethod
    def limit_transform(grammar_node=None):
        if glo.Debug == 1:
            print('[Debug] [LogicalEngine] [limit_transform] [input:', grammar_node, ']')
        now_node = dict()
        now_node['type'] = "limit"
        now_node['son'] = []
        if op.eq(grammar_node, None):
            now_node['check'] = ExpTreeNode()
        else:
            now_node['check'] = ExpTreeNode().make_calc_tree(grammar_node)
            now_node['check'].debug_calc_tree()
        return now_node

    # 处理select中的投影,select
    # todo: column也可以是表达式
    @staticmethod
    def map_transform(columns):
        if glo.Debug == 1:
            print('[Debug] [map_transform] [input:', columns)
        now_node = dict()
        now_node['type'] = "map"
        now_node['son'] = []
        if columns[0] == '*':
            now_node['columns'] = '*'
        else:
            now_node['columns'] = []
            for column in columns:
                now_node['columns'].append(column['name'])
        return now_node

    # 处理选择select
    @staticmethod
    def select_transform(grammar_node):
        print("[Running Log] [select_transform] [", grammar_node, ']\n')
        # exp_node.op
        # columns -> where -> from
        # columns
        col_node = LogicalEngine.map_transform(grammar_node['columns'])
        # where
        print('[Debug] ','filters' in grammar_node.keys(),'\n')
        if 'filters' in grammar_node.keys():
            where_rule = grammar_node['filters']
        else:
            where_rule = None
        where_node = LogicalEngine.limit_transform(where_rule)
        # from
        from_node = LogicalEngine.join_transform(grammar_node['tables'])
        col_node['son'].append(where_node)
        where_node['son'].append(from_node)
        return col_node

    # 对于create请求，做进一步的转发
    @staticmethod
    def create_transform(grammar_node):
        if glo.Debug == 1:
            print('[Debug] [create_transform] [input:', grammar_node)
        if op.eq(grammar_node['type'], 'database'):
            return LogicalEngine.create_database_transform(grammar_node)
        return LogicalEngine.create_table_transform(grammar_node)

    # 创建数据库的表
    # todo:物理计划执行的时候要知道数据库的元信息,这里还没处理columns表
    @staticmethod
    def create_table_transform(grammar_node):
        if glo.Debug == 1:
            print('[Debug] [create_table_transform] [input:', grammar_node, ']')
        now_node = dict()
        now_node['type'] = "ct"
        now_node['table'] = grammar_node['name']
        now_node['columns'] =grammar_node['columns']
        now_node['primary'] = grammar_node['constraints']
        return now_node

    @staticmethod
    def create_database_transform(grammar_node):
        if glo.Debug == 1:
            print('[Debug] [create_database_transform] [input:', grammar_node, ']')
        now_node = dict()
        now_node['type'] = "cd"
        now_node['name'] = grammar_node['name']
        return now_node

    # 增加条目
    # fixme:嵌入表达式
    @staticmethod
    def insert_transform(grammar_node):
        if glo.Debug == 1:
            print('[Debug] [insert_transform] [input:', grammar_node)
        now_node = dict()
        now_node['type'] = 'iv'
        now_node['table'] = grammar_node['tablename']
        if 'columns' in grammar_node:
            now_node['columns'] = grammar_node['columns']
        else:
            now_node['columns'] = '*'
        now_node['values'] = []
        for line in grammar_node['values']:
            now_data = []
            for now_value in line:
                now_data.append(ExpTreeNode.make_calc_tree(now_value))
            now_node['values'].append(now_data)
        return now_node

    @staticmethod
    def update_exp_transform(grammar_node):
        now_node = dict()
        now_node['type'] = 'calc'
        now_node['column'] = grammar_node['column']['name']
        now_node['calc'] = ExpTreeNode().make_calc_tree(grammar_node['opexpr'])
        now_node['calc'].debug_calc_tree()
        return now_node

    # 更新
    # update table set column = exp where limit
    # from table
    # where limit
    # set column = exp
    @staticmethod
    def update_transform(grammar_node):
        if glo.Debug==1:
            print('[Debug] [update_transform] [input:', grammar_node)
        now_node = dict()
        now_node['type'] = 'up'
        now_node['table'] = grammar_node['tablename']
        from_node = dict()
        from_node['type'] = 'table'
        from_node['name'] = grammar_node['tablename']

        if 'filters' in grammar_node.keys():
            where_rule = grammar_node['filters']
        else:
            where_rule = None
        where_node = LogicalEngine.limit_transform(where_rule)
        where_node['son'].append(from_node)
        now_node['son'] = []
        now_node['son'].append(where_node)
        now_node['trans'] = []
        for columns_set in grammar_node['set']:
            now_node['trans'].append(LogicalEngine.update_exp_transform(columns_set))
        return now_node

    # 删除
    @staticmethod
    def delete_transform(grammar_node):
        if glo.Debug == 1:
            print('[Debug] [delete_transform] [input:', grammar_node)
        now_node = dict()
        now_node['type'] = 'del'
        now_node['table'] = grammar_node['tablename']
        from_node = dict()
        from_node['type'] = 'table'
        from_node['name'] = grammar_node['tablename']

        if 'filters' in grammar_node.keys():
            where_rule = grammar_node['filters']
        else:
            where_rule = None
        where_node = LogicalEngine.limit_transform(where_rule)
        where_node['son'].append(from_node)
        now_node['son'] = []
        now_node['son'].append(where_node)
        return now_node

    # drop 数据库 / 表
    @staticmethod
    def drop_transform(grammar_node):
        now_node = dict()
        if op.eq(grammar_node['type'], 'database'):
            now_node['type'] = 'deld'
            now_node['name'] = grammar_node['name']
        else:
            now_node['type'] = 'delt'
            now_node['name'] = grammar_node['names']
        return now_node

    # 处理all,但不具体，只是转发到具体的操作上
    @staticmethod
    def dfs_grammar_tree(grammar_node):
        if op.eq(grammar_node['type'], "query"):
         #   node.son.append(dfs)
            if op.eq(grammar_node['name'], "select"):
                return LogicalEngine.select_transform(grammar_node['content'])
            elif op.eq(grammar_node['name'], "create"):
                return LogicalEngine.create_transform(grammar_node['content'])
            elif op.eq(grammar_node['name'], 'insert'):
                return LogicalEngine.insert_transform(grammar_node['content'])
            elif op.eq(grammar_node['name'], 'update'):
                return LogicalEngine.update_transform(grammar_node['content'])
            elif op.eq(grammar_node['name'], 'delete'):
                return LogicalEngine.delete_transform(grammar_node['content'])
            elif op.eq(grammar_node['name'], 'drop'):
                return LogicalEngine.drop_transform(grammar_node['content'])
        print("[ERROR] [ Query ERROR ] !")
        return None

    # 删除表达式树
    def delete_exp_tree(self, node):
        return

    # 逻辑计划入口
    # 输入：语法分析树的根节点
    # 输出：关系表达式的根节点
    @staticmethod
    def run_logical_main(grammar_tree_root):
        return LogicalEngine.dfs_grammar_tree(grammar_tree_root)
