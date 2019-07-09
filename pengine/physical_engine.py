#
# -*- coding:utf-8 -*-
# 作者：Macaulish
# 创建：2019-07-05
# 作用：物理计划执行
# 主要涉及： 得到表内容，当最后涉及表更改时写入缓存区
#           得到表内容后根据树进行集合计算，需要跟语法相关
#           dfs关系代数，输出结果
#
# 物理计划每个块用getnext()迭代访问
#

import operator as op
from iod.io_cache_manager import *
import copy
import glo.glovar as glo
from pengine.query_result import *


class PhysicalBlock(Result):

    def __init__(self):
        Result.__init__(self)
        self.data = []
        self.index = 0

    def get_next(self):
        if self.index == len(self.data):
            return None
        data = self.data[self.index]
        self.index += 1
        return data

    # todo flag
    def table_operator(self, logical_tree):
        if glo.GlobalVar.Debug == 1:
            glo.Log.write_log('[Debug] [physical] [table_operator] [input:', glo.Log.ttstr(logical_tree), ']')
        son = IoCacheManager.select_table_entry(logical_tree['name'])
        if op.eq(son.flag, True):
            self.flag = son.flag
            self.result = son.result
            return self
        self.data = son.result
        return self

    # todo flag
    def map_operator(self, logical_tree):
        if glo.GlobalVar.Debug == 1:
            glo.Log.write_log('[Debug] [physical] [map_operator] [input:', glo.Log.ttstr(logical_tree), ']')
        son = self.dfs_plan_tree(logical_tree['son'][0])
        if op.eq(son.flag, True):
            self.flag = son.flag
            self.result = son.result
            return self
        while True:
            now_data = son.get_next()
            if op.eq(now_data, None):
                break
            if logical_tree['columns'] == '*':
                self.data.append(now_data)
            else:
                more_data = dict()
                add_data = dict()
                for column in logical_tree['columns']:
                    add_data[column.name] = column.calc_data(now_data)
                table_name = list(now_data.keys())[0]
                more_data[table_name] = add_data
                self.data.append(more_data)
        return self

    # todo flag
    def join_operator(self, logical_tree):
        if glo.GlobalVar.Debug == 1:
            glo.Log.write_log('[Debug] [physical] [join_operator] [input:', glo.Log.ttstr(logical_tree), ']')
        for son_node in logical_tree['son']:
            son = self.dfs_plan_tree(son_node)
            if op.eq(son.flag, True):
                self.flag = son.flag
                self.result = son.result
                return self
            pre_data_set = copy.deepcopy(self.data)
            while True:
                now_data = son.get_next()
                if glo.GlobalVar.Debug == 1:
                    glo.Log.write_log('[Debug] [physical] [join_operator2] [', glo.Log.ttstr(now_data), ']',
                          '[', pre_data_set, ']', '[', len(pre_data_set), ']')
                if op.eq(now_data, None):
                    break
                if len(pre_data_set) == 0:
                    self.data.append(now_data)
                else:
                    for data in pre_data_set:
                        self.data.append(dict(data, **now_data))
        return self

    # todo flag
    def limit_operator(self, logical_tree):
        if glo.GlobalVar.Debug == 1:
            glo.Log.write_log('[Debug] [physical] [limit_operator] [input:', glo.Log.ttstr(logical_tree), ']')
        son = self.dfs_plan_tree(logical_tree['son'][0])
        if op.eq(son.flag, True):
            self.flag = son.flag
            self.result = son.result
            return self
        while True:
            now_data = son.get_next()
            if op.eq(now_data, None):
                break
            if op.eq(logical_tree['check'].check_data_main(now_data), True):
                self.data.append(now_data)
        return self

    def delete_operator(self, logical_tree):
        if glo.GlobalVar.Debug == 1:
            glo.Log.write_log('[Debug] [physical] [delete_operator] [input:', glo.Log.ttstr(logical_tree), ']')
        # 子树是否有问题
        son = self.dfs_plan_tree(logical_tree['son'][0])
        if op.eq(son.flag, True):
            self.flag = son.flag
            self.result = son.result
            return self
        while True:
            now_data = son.get_next()
            if op.eq(now_data, None):
                break
            son_result = IoCacheManager.delete_table_entry(logical_tree['table'], now_data)
            # 是否删除成功
            if op.eq(son_result.flag, True):
                if op.eq(self.flag, False):
                    self.flag = True
                    self.result = []
                self.result.append(son_result.result)
        if op.eq(self.flag, False):
            self.result = list()
            self.result.append(str("[Success] [delete_operator]"))
        return self

    def update_operator(self, logical_tree):
        if glo.GlobalVar.Debug == 1:
            glo.Log.write_log('[Debug] [physical] [update_operator] [input:', glo.Log.ttstr(logical_tree), ']')
        son = self.dfs_plan_tree(logical_tree['son'][0])
        if op.eq(son.flag, True):
            self.flag = son.flag
            self.result = son.result
            return self
        while True:
            now_data = son.get_next()
            if op.eq(now_data, None):
                break
            new_data = copy.deepcopy(now_data)
            for trans in logical_tree['trans']:
                new_data[logical_tree['table']][trans['column']] = trans['calc'].calc_data(now_data)
            son_result = IoCacheManager.update_table_entry(logical_tree['table'], now_data, new_data)
            if op.eq(son_result.flag, True):
                if op.eq(self.flag, False):
                    self.flag = True
                self.result.append(son_result.result)
        if op.eq(self.flag, False):
            self.result = list()
            self.result.append(str("[Success] [update_operator]"))
        return self

    # todo: 创建数据库
    # todo
    def create_database_operator(self, logical_tree):
        if glo.GlobalVar.Debug == 1:
            # print("!!!!!!!! ", glo.Log.ttstr(logical_tree))
            glo.Log.write_log('[Debug] [physical] [create_database_operator] [input:', glo.Log.ttstr(logical_tree), ']')
        son = IoCacheManager.create_database(logical_tree['name'])
        if op.eq(son.flag, True):
            self.flag = son.flag
            self.result = son.result
        else:
            self.result = []
            self.result.append(str("[Success] [create database : " + logical_tree['name'] + "]"))
        glo.Log.write_log('[Debug] [physical] [create_database_operator] [output:', self.flag, str(self.result), ']')
        return self

    # 创建表
    def create_table_operator(self, logical_tree):
        if glo.GlobalVar.Debug == 1:
            glo.Log.write_log('[Debug] [physical] [create_table_operator] [input:', str(logical_tree), ']')

        list_column = []
        list_primary = []
        list_null = []
        if 'constraints' in logical_tree.keys():
            if 'primary key' in logical_tree['constraints']:
                for column in logical_tree['constraints']['primary key']:
                    list_primary.append(column)
            if 'not null' in logical_tree['constraints']:
                for column in logical_tree['constraints']['not null']:
                    list_null.append(column)
        if glo.GlobalVar.Debug == 1:
            glo.Log.write_log('[Debug] [physical] [create_table_operator] [list_primary:',
                              glo.Log.ttstr(list_primary), ']')
            glo.Log.write_log('[Debug] [physical] [create_table_operator] [list_null', glo.Log.ttstr(list_null), ']')

        for column in logical_tree['columns']:
            now_column = dict()
            now_column['column'] = column['name']
            if 'length' in column['datatype'].keys():
                now_column['datatype'] = column['datatype']['typename']\
                                           + '(' + str(column['datatype']['length'])+')'
            else:
                now_column['datatype'] = column['datatype']['typename']
            now_column['primary'] = False
            if column['name'] in list_primary:
                now_column['primary'] = True
            now_column['null'] = True
            if column['name'] in list_null:
                now_column['null'] = False
            list_column.append(now_column)
        son = IoCacheManager.create_table(logical_tree['table'], list_column)
        if glo.GlobalVar.Debug == 1:
            glo.Log.write_log('[Debug] [physical] [create_table_operator] [son_result:',
                              son.flag, glo.Log.ttstr(son.result), ']')
        if op.eq(son.flag, True):
            self.result = son.result
            self.flag = son.flag
        else:
            self.result = list()
            self.result.append(str("[Success] [create table : " + logical_tree['table'] + "]"))
        return self

    # 增 , todo 记录错误
    def insert_operator(self, logical_tree):
        if glo.GlobalVar.Debug == 1:
            glo.Log.write_log('[Debug] [physical] [insert_operator] [input:', glo.Log.ttstr(logical_tree), ']')
        if isinstance(logical_tree['columns'], tuple):
            for now_data in logical_tree['values']:
                if glo.GlobalVar.Debug == 1:
                    glo.Log.write_log('[Debug] [physical] [insert_operator2] [', glo.Log.ttstr(now_data), ']')
                more_data = IoCacheManager.insert_table_none_entry(logical_tree['table'])
                index = 0
                for column in logical_tree['columns']:
                    more_data[column] = now_data[index].calc_data()
                    index += 1
                add_data = dict()
                add_data[logical_tree['table']] = more_data
                son = IoCacheManager.insert_table_entry(logical_tree['table'], add_data)
                if op.eq(son.flag, True):
                    if op.eq(self.flag, False):
                        self.flag = True
                        self.result = []
                    self.result.append(son.result)
        else:
            for now_data in logical_tree['values']:
                more_data = []
                for values in now_data:
                    more_data.append(values.calc_data())
                son = IoCacheManager.insert_table_entry_list(logical_tree['table'], more_data)
                if op.eq(son.flag, True):
                    if op.eq(self.flag, False):
                        self.flag = True
                        self.result = []
                    self.result.append(son.result)
        if op.eq(self.flag, False):
            self.result = []
            self.result.append(str("[Success] [insert]"))
        return

    def drop_table_operator(self, logical_tree):
        for table in logical_tree['name']:
            son = IoCacheManager.enable_table(table)
            if op.eq(son.flag, True):
                if op.eq(self.flag, False):
                    self.flag = True
                    self.result = []
                self.result.append(son.result)
                continue
            IoCacheManager.delete_table_in_databaselist(table)
            IoCacheManager.save_table_and_remove(table)
            IoCacheManager.drop_table(table)
            if op.eq(son.flag, True):
                if op.eq(self.flag, False):
                    self.flag = True
                    self.result = []
                self.result.append(son.result)
                continue
        if op.eq(self.flag, False):
            self.result = list()
            self.result.append(str("[Success] [drop_table_operator]"))
        return self

    def drop_database_operator(self, logical_tree):
        son = IoCacheManager.drop_database(logical_tree['name'])
        if op.eq(son.flag, True):
            self.result = son.result
            self.flag = son.flag
        else:
            self.result = []
            self.result.append(str("[Success] [drop_database: " + logical_tree['name'] + ']'))
        return self

    def use_operator(self, logical_tree):
        if op.eq(IoCacheManager.is_exist_database(logical_tree['name']), True):
            glo.GlobalVar.databasePath = logical_tree['name']
            if glo.GlobalVar.Debug == 1:
                glo.Log.write_log('[Debug] [physical] [use_operator] [', glo.GlobalVar.databasePath, ']')
            IoCacheManager.quit_main()
            self.result = []
            self.result.append(str("[Success] [use_database: " + logical_tree['name'] + ']'))
        else:
            self.flag = True
            self.result = []
            self.result.append(str("[Error] [don't exist database:" + logical_tree['name'] + ']'))
        return self

    def show_database_operator(self, logical_tree):
        son = IoCacheManager.show_database()
        if op.eq(son.flag, False):
            self.data = son.result
        self.result = son.result
        self.flag = son.flag
        return self

    def show_table_operator(self, logical_tree):
        son = IoCacheManager.show_table()
        if op.eq(son.flag, False):
            self.data = son.result
        self.result = son.result
        self.flag = son.flag
        return self

    def show_columns_operator(self, logical_tree):
        son = IoCacheManager.show_columns(logical_tree['name'])
        if op.eq(son.flag, False):
            self.data = son.result
        self.result = son.result
        self.flag = son.flag
        return self

    @classmethod
    def dfs_plan_tree(cls, logical_tree):
        if glo.GlobalVar.Debug == 1:
            glo.Log.write_log('[Debug] [physical] [dfs_plan_tree] [', glo.Log.ttstr(logical_tree), ']')
        now_block = PhysicalBlock()
        if op.eq(logical_tree['type'], 'map'):
            now_block.map_operator(logical_tree)
        elif op.eq(logical_tree['type'], 'limit'):
            now_block.limit_operator(logical_tree)
        elif op.eq(logical_tree['type'], 'join'):
            now_block.join_operator(logical_tree)
        elif op.eq(logical_tree['type'], 'table'):
            now_block.table_operator(logical_tree)
        elif op.eq(logical_tree['type'], 'cd'):
            now_block.create_database_operator(logical_tree)
        elif op.eq(logical_tree['type'], 'ct'):
            now_block.create_table_operator(logical_tree)
        elif op.eq(logical_tree['type'], 'iv'):
            now_block.insert_operator(logical_tree)
        elif op.eq(logical_tree['type'], 'up'):
            now_block.update_operator(logical_tree)
        elif op.eq(logical_tree['type'], 'del'):
            now_block.delete_operator(logical_tree)
        elif op.eq(logical_tree['type'], 'delt'):
            now_block.drop_table_operator(logical_tree)
        elif op.eq(logical_tree['type'], 'deld'):
            now_block.drop_database_operator(logical_tree)
        elif op.eq(logical_tree['type'], 'use'):
            now_block.use_operator(logical_tree)
        elif op.eq(logical_tree['type'], 'showt'):
            now_block.show_table_operator(logical_tree)
        elif op.eq(logical_tree['type'], 'showd'):
            now_block.show_database_operator(logical_tree)
        elif op.eq(logical_tree['type'], 'showc'):
            now_block.show_columns_operator(logical_tree)
        return now_block

