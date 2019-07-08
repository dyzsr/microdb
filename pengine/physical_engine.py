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


class PhysicalBlock:

    def __init__(self):
        self.data = []
        self.index = 0

    def get_next(self):
        if self.index == len(self.data):
            return None
        data = self.data[self.index]
        self.index += 1
        return data

    def table_operator(self, logical_tree):
        if glo.Debug == 1:
            print('[Debug] [physical] [table_operator] [input:', logical_tree, ']')
        self.data = IoCacheManager.select_table_entry(logical_tree['name'])
        return self

    def map_operator(self, logical_tree):
        if glo.Debug == 1:
            print('[Debug] [physical] [map_operator] [input:', logical_tree, ']')
        son = self.dfs_plan_tree(logical_tree['son'][0])
        while True:
            now_data = son.get_next()
            if op.eq(now_data, None):
                break
            if logical_tree['columns'] == '*':
                self.data.append(now_data)
            else:
                more_data = dict()
                for column in logical_tree['columns']:
                    more_data[column.name] = column.calc_data(now_data)
                self.data.append(more_data)
        return self

    def join_operator(self, logical_tree):
        if glo.Debug == 1:
            print('[Debug] [physical] [join_operator] [input:', logical_tree, ']')
        for son_node in logical_tree['son']:
            son = self.dfs_plan_tree(son_node)
            pre_data_set = copy.deepcopy(self.data)
            while True:
                now_data = son.get_next()
                if glo.Debug == 1:
                    print('[Debug] [physical] [join_operator2] [', now_data, ']',
                          '[', pre_data_set, ']', '[', len(pre_data_set), ']')
                if op.eq(now_data, None):
                    break
                if len(pre_data_set) == 0:
                    self.data.append(now_data)
                else:
                    for data in pre_data_set:
                        self.data.append(dict(data, **now_data))
        return self

    def limit_operator(self, logical_tree):
        if glo.Debug == 1:
            print('[Debug] [physical] [limit_operator] [input:', logical_tree, ']')
        son = self.dfs_plan_tree(logical_tree['son'][0])
        while True:
            now_data = son.get_next()
            if op.eq(now_data, None):
                break
            if op.eq(logical_tree['check'].check_data_main(now_data),True):
                self.data.append(now_data)
        return self

    def delete_operator(self, logical_tree):
        if glo.Debug == 1:
            print('[Debug] [physical] [delete_operator] [input:', logical_tree, ']')
        son = self.dfs_plan_tree(logical_tree['son'][0])
        while True:
            now_data = son.get_next()
            if op.eq(now_data, None):
                break
            IoCacheManager.delete_table_entry(logical_tree['table'], now_data)
        return

    def update_operator(self, logical_tree):
        if glo.Debug == 1:
            print('[Debug] [physical] [update_operator] [input:', logical_tree, ']')
        son = self.dfs_plan_tree(logical_tree['son'][0])
        while True:
            now_data = son.get_next()
            if op.eq(now_data, None):
                break
            new_data = copy.deepcopy(now_data)
            for trans in logical_tree['trans']:
                new_data[logical_tree['table']][trans['column']] = trans['calc'].calc_data(now_data)
            IoCacheManager.update_table_entry(logical_tree['table'],now_data ,new_data)
        return

    # todo: 创建数据库
    def create_database_operator(self, logical_tree):
        return

    # todo： 创建表
    def create_table_operator(self, logical_tree):
        if glo.Debug == 1:
            print('[Debug] [physical] [create_table_operator] [input:', logical_tree, ']')
        IoCacheManager.create_table(logical_tree['table'])
        return

    def insert_operator(self, logical_tree):
        if glo.Debug == 1:
            print('[Debug] [physical] [insert_operator] [input:', logical_tree, ']')
        if isinstance(logical_tree['columns'], tuple):
            for now_data in logical_tree['values']:
                if glo.Debug == 1:
                    print('[Debug] [physical] [insert_operator2] [', now_data, ']')
                more_data = dict()
                index = 0
                for column in logical_tree['columns']:
                    more_data[column] = now_data[index].calc_data()
                    index += 1
                add_data = dict()
                add_data[logical_tree['table']] = more_data
                IoCacheManager.insert_table_entry(logical_tree['table'], add_data)
        else:
            for now_data in logical_tree['values']:
                more_data = []
                for values in now_data:
                    more_data.append(values.calc_data())
                add_data = dict()
                add_data[logical_tree['table']] = more_data
                IoCacheManager.insert_table_entry_list(logical_tree['table'], add_data)
        return

    @classmethod
    def dfs_plan_tree(cls, logical_tree):
        if glo.Debug == 1:
            print('[Debug] [physical] [dfs_plan_tree] [', logical_tree, ']')
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
        return now_block

