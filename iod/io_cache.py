#
# -*- coding:utf-8 -*-
# 作者：Macaulish
# 创建：2019-07-05
# 作用：作为缓存区，接受缓存区管理器的管理，读/写数据
# 主要涉及： 增,删,改,查,整体写入,整体写出
# 数据存储 dict

import operator as op


class CacheBlock:

    def __init__(self):
        self.data = []

    # 增
    def insert_table_entry(self, entry):
        self.data.append(entry)
        return

    # 删
    def delete_table_entry(self, entry):
        self.data.remove(entry)
        return

    # 改
    def update_table_entry(self, oldentry, newentry):
        index = 0
        for words in self.data:
            if op.eq(words, oldentry):
                self.data[index] = newentry
                break
            else:
                index += 1
        return

    # all_read
    def all_table_read(self):
        return self.data

    # all_write
    # get data and write in memory
    def all_table_write(self, list_object):
        self.data = []
        for data_object in list_object:
            self.data.append(data_object)

