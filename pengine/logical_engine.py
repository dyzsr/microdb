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
        self.name = ""
        return

    # 计算的过程
    def calc_data(self, data=None):
        if glo.GlobalVar.Debug == 1:
            glo.Log.write_log('[Debug] [calc_data] [input:', self.type, glo.Log.ttstr(self.lson), glo.Log.ttstr(self.rson),
                              glo.Log.ttstr(data), ']')
        if re.search(r'value', self.type):
            return self.lson
        if re.search(r'column', self.type):
            glo.Log.write_log('[Debug] [calc_data] [column', op.eq(self.lson, '*'),']')
            if op.eq(self.lson, '*'):
                for (k, v) in data.items():
                    glo.Log.write_log('[Debug] [calc_data] [get<key,value>:', k,v, ']')
                    if self.rson in v.keys():
                        if glo.GlobalVar.Debug == 1:
                            glo.Log.write_log('[Debug] [calc_data] [output columns:', v[self.rson], ']')
                        return v[self.rson]
            return data[self.lson][self.rson]
        # 一元运算符,二元运算符
        # 更新，直接用字符串
        # 逻辑运算符: And, or, not
        # 算数运算符：+,-,*,/
        # 关系运算符：>,<,=,(<>? !=)
        # todo: 计算表达式过程的合法性检验
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
        return self.calc_data(data) != False

    #
    def debug_calc_tree(self):
        glo.Log.write_log('[Debug] [Calc Tree] [', self.type, 'lson', glo.Log.ttstr(self.lson), 'rson', glo.Log.ttstr(self.rson) ,']');
        if op.eq(self.type, 'value'):
            glo.Log.write_log('[Debug] [Calc Tree] [Value]', glo.Log.ttstr(self.lson))
        elif op.eq(self.type, 'column'):
            glo.Log.write_log('[Debug] [Calc Tree] [Column]', glo.Log.ttstr(self.lson), glo.Log.ttstr(self.rson))
        elif re.match(r'\+|-|\*|\|and|or|>|<|=|!=', self.type):
            self.lson.debug_calc_tree()
            self.rson.debug_calc_tree()
        else:
            self.lson.debug_calc_tree()

    # 建树的过程
    @classmethod
    def make_calc_tree(cls, grammar_node):
        if glo.GlobalVar.Debug == 1:
            glo.Log.write_log('[Debug] [make_check_tree] [input:', glo.Log.ttstr(grammar_node),']')
        now_node = ExpTreeNode()
        if isinstance(grammar_node, dict):
            if op.eq(grammar_node['type'], 'opexpr'):
                oper = grammar_node['operator']
                now_node.type = oper
                if re.match(r'\+|-|\*|\|and|or|>|<|=|!=|<=|>=', oper):
                    if glo.GlobalVar.Debug == 1:
                        glo.Log.write_log('[Debug] [make_check_tree] [re1]:', oper, ']')
                    now_node.lson = cls.make_calc_tree(grammar_node['operands'][0])
                    now_node.rson = cls.make_calc_tree(grammar_node['operands'][1])
                    now_node.name = '(' + now_node.lson.name+')'+oper+'('+ now_node.rson.name + ')'
                elif re.match(r'not|uminus', oper):
                    if glo.GlobalVar.Debug == 1:
                        glo.Log.write_log('[Debug] [make_check_tree] [re2]:', oper, ']')
                    now_node.lson = cls.make_calc_tree(grammar_node['operands'][0])
                    now_node.name = oper + '(' +now_node.lson.name + ')'
                return now_node
            oper = grammar_node['type']
            now_node.type = oper
            if op.eq(oper, 'column'):
                if 'table' in grammar_node.keys():
                    now_node.lson = grammar_node['table']
                    now_node.name = now_node.lson+'.' + grammar_node['name']
                else:
                    now_node.lson = '*'
                    now_node.name = grammar_node['name']
                now_node.rson = grammar_node['name']
        else:
            now_node.type = 'value'
            now_node.lson = grammar_node
            now_node.name = str(grammar_node)
        return now_node


class LogicalEngine:
    node_total = 0

    def __init__(self):
        return

    # 直接对应一个表
    @staticmethod
    def table_transform(grammar_node):
        if glo.GlobalVar.Debug == 1:
            glo.Log.write_log('[Debug] [LogicalEngine] [table_transform] [input:', glo.Log.ttstr(grammar_node), ']')
        now_node = dict()
        now_node['type'] = 'table'
        now_node['name'] = grammar_node['name']
        return now_node

    # 处理select中的from
    @staticmethod
    def join_transform(grammar_node):
        if glo.GlobalVar.Debug == 1:
            glo.Log.write_log('[Debug] [LogicalEngine] [join_transform] [input:', glo.Log.ttstr(grammar_node), ']')
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
        if glo.GlobalVar.Debug == 1:
            glo.Log.write_log('[Debug] [LogicalEngine] [limit_transform] [input:', glo.Log.ttstr(grammar_node), ']')
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
    # updata column can be exp
    @staticmethod
    def map_transform(columns):
        if glo.GlobalVar.Debug == 1:
            glo.Log.write_log('[Debug] [map_transform] [input:', glo.Log.ttstr(columns))
        now_node = dict()
        now_node['type'] = "map"
        now_node['son'] = []
        if columns[0] == '*':
            now_node['columns'] = '*'
        else:
            now_node['columns'] = []
            for column in columns:
                now_node['columns'].append(ExpTreeNode().make_calc_tree(column))
        return now_node

    # 处理选择select
    @staticmethod
    def select_transform(grammar_node):
        glo.Log.write_log("[Running Log] [select_transform] [", glo.Log.ttstr(grammar_node), ']\n')
        # exp_node.op
        # columns -> where -> from
        # columns
        col_node = LogicalEngine.map_transform(grammar_node['columns'])
        # where
        glo.Log.write_log('[Debug] ', 'filters' in grammar_node.keys(),'\n')
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
        if glo.GlobalVar.Debug == 1:
            glo.Log.write_log('[Debug] [create_transform] [input:', glo.Log.ttstr(grammar_node), ']')
        if op.eq(grammar_node['type'], 'database'):
            return LogicalEngine.create_database_transform(grammar_node)
        return LogicalEngine.create_table_transform(grammar_node)

    # 创建数据库的表
    # 实际处理放在物理执行计划阶段
    @staticmethod
    def create_table_transform(grammar_node):
        if glo.GlobalVar.Debug == 1:
            glo.Log.write_log('[Debug] [create_table_transform] [input:', glo.Log.ttstr(grammar_node), ']')
        now_node = dict()
        now_node['type'] = "ct"
        now_node['table'] = grammar_node['name']
        now_node['columns'] =grammar_node['columns']
        now_node['constraints'] = grammar_node['constraints']
        return now_node

    @staticmethod
    def create_database_transform(grammar_node):
        if glo.GlobalVar.Debug == 1:
            glo.Log.write_log('[Debug] [create_database_transform] [input:', glo.Log.ttstr(grammar_node), ']')
        now_node = dict()
        now_node['type'] = "cd"
        now_node['name'] = grammar_node['name']
        return now_node

    # 增加条目
    # insert的嵌入表达式已完成
    @staticmethod
    def insert_transform(grammar_node):
        if glo.GlobalVar.Debug == 1:
            glo.Log.write_log('[Debug] [insert_transform] [input:', glo.Log.ttstr(grammar_node))
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
        if glo.GlobalVar.Debug == 1:
            glo.Log.write_log('[Debug] [update_transform] [input:', glo.Log.ttstr(grammar_node))
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
        if glo.GlobalVar.Debug == 1:
            glo.Log.write_log('[Debug] [delete_transform] [input:', glo.Log.ttstr(grammar_node))
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

    # use
    @staticmethod
    def use_transform(grammar_node):
        now_node = dict()
        now_node['type'] = 'use'
        now_node['name'] = grammar_node['database']
        return now_node

    # show
    @staticmethod
    def show_transform(grammar_node):
        now_node = dict()
        if op.eq(grammar_node['type'], 'table'):
            now_node['type'] = 'showt'
        elif op.eq(grammar_node['type'], 'database'):
            now_node['type'] = 'showd'
        else:
            now_node['type'] = 'showc'
            now_node['name'] = grammar_node['tablename']
        return now_node

    # 处理all,但不具体，只是转发到具体的操作上
    @staticmethod
    def dfs_grammar_tree(grammar_node):
        if glo.GlobalVar.Debug == 1:
            # print("!!!!!!!! ", glo.Log.ttstr(grammar_node))
            glo.Log.write_log('[Debug] [dfs_grammar_tree] [input:', glo.Log.ttstr(grammar_node), ']')
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
            elif op.eq(grammar_node['name'], 'use'):
                return LogicalEngine.use_transform(grammar_node['content'])
            elif op.eq(grammar_node['name'], 'show'):
                return LogicalEngine.show_transform(grammar_node['content'])
        glo.Log.write_log("[ERROR] [ Query ERROR ] !")
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
