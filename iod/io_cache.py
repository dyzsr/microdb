#
# -*- coding:utf-8 -*-
# 作者：Macaulish
# 创建：2019-07-05
# 作用：作为缓存区，接受缓存区管理器的管理，读/写数据
# 主要涉及： 增,删,改,查,整体写入,整体写出
# 数据存储 dict

import operator as op
import glo.glovar as glo
from pengine.query_result import *


class CacheBlock:

    def __init__(self):
        self.data = []
        self.meta = dict()

    def is_exist_entry(self, entry):
        if entry in self.data:
            return True
        return False

    # 增
    def insert_table_entry(self, entry):
        if glo.GlobalVar.Debug == 1:
            print('[Debug] [CacheBlock] [insert_table_entry] [input:', entry, ']')
        self.data.append(entry)
        return

    # 删
    def delete_table_entry(self, entry):
        result = Result()
        if op.eq(self.is_exist_entry(entry), True):
            self.data.remove(entry)
        else:
            result.flag = True
            result.result = []
            result.result.append(str('[Error] [ don\'t exist item in table'))
        return result

    # 改
    def update_table_entry(self, oldentry, newentry):
        result = Result()
        if op.eq(self.is_exist_entry(oldentry), True):
            index = 0
            for words in self.data:
                if op.eq(words, oldentry):
                    self.data[index] = newentry
                    break
                else:
                    index += 1
        else:
            result.flag = True
            result.result = []
            result.result.append(str('[Error] [ don\'t exist item in table'))
        return result

    # all_read
    def all_table_read(self):
        if glo.GlobalVar.Debug == 1:
            print('[Debug] [CacheBlock] [all_table_read] [', self.data, ']')
        return self.data

    # all_write
    # get data and write in memory
    def all_table_write(self, list_object):
        if op.eq(list_object, None):
            return
        self.data = []
        for data_object in list_object:
            self.data.append(data_object)

    def get_metadata(self, obj):
        self.meta = obj
        return


