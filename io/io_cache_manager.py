#
# -*- coding:utf-8 -*-
# 作者：Macaulish
# 创建：2019-07-05
# 作用：1. 作为缓存区管理器，接受上层请求(增,删,改,查),
#      2. 然后对缓存区进行操作
#       3. 向下传递给存储管理器
# 关于查询！！！需要自己看看物理计划的执行
#
# 管理器实例化一些cache块
# ========================================================
# import
# ----1. pickle
# ----

from io.io_cache import *
from io.io_in_out import *

import operator as op
import os


dirPath = "D:\\dbms\\store"


class IoCacheManager:
    cache_block_Limit = 3000
    # 时间戳
    total_timestamp = 0
    #
    list_cache_block = []
    # 表名
    list_cache_block_name = []
    # 是否失效
    list_cache_block_flag = []
    # 是否时间
    list_cache_block_timestamp = []

    # 实例化对象
    def __init__(self):
        return

    # 替换策略,待实现
    @classmethod
    def LRU(cls):
        now_cache = CacheBlock()
        cls.list_cache_block.append(now_cache)
        cls.list_cache_block_name.append("")
        return len(cls.list_cache_block)-1

    # 检查是否载入
    @classmethod
    def find_cache_block(cls, table_name):
        list_name = cls.list_cache_block_name
        index = 0
        for block_name in list_name:
            if op.eq(block_name, table_name):
                return index
            else:
                index += 1
        if index == len(list_name):
            return -1

    # 立即表载入
    @classmethod
    def load_right_now(cls, table_name):
        cache_index = IoCacheManager.LRU()
        cls.list_cache_block_name[cache_index] = table_name
        cls.list_cache_block[cache_index].\
            all_table_write(StoreManager.read_table(table_name))
        return

    # 立即表载出
    @classmethod
    def store_right_now(cls):
        return

    # 是否需要载入，如果有则不执行，如有没有则载入
    @classmethod
    def check_table_load(cls, table_name):
        table_index = cls.find_cache_block(table_name)
        if table_index == -1:
            cls.load_right_now(table_name)
        return

    # 增
    @classmethod
    def insert_table_entry(cls, table_name, entry):
        cls.check_table_load(table_name)
        table_index = cls.find_cache_block(table_name)
        IoCacheManager.list_cache_block[table_index]\
            .insert_table_entry(entry)
        return

    # 删
    @classmethod
    def delete_table_entry(cls, table_name, entry):
        cls.check_table_load(table_name)
        table_index = cls.find_cache_block(table_name)
        IoCacheManager.list_cache_block[table_index] \
            .delete_table_entry(entry)
        return

    # 改
    @classmethod
    def update_table_entry(cls, table_name, oldentry, newentry):
        cls.check_table_load(table_name)
        table_index = cls.find_cache_block(table_name)
        IoCacheManager.list_cache_block[table_index] \
            .update_table_entry(oldentry, newentry)
        return

    # 输出整体表
    @classmethod
    def select_table_entry(cls, table_name):
        cls.check_table_load(table_name)
        table_index = cls.find_cache_block(table_name)
        return IoCacheManager.list_cache_block[table_index] \
            .all_table_read()

    # 创表
    @classmethod
    def create_table(cls, table_name):
        try:
            fp = open(dirPath+table_name, "r")
            fp.close()
            print("[Error],[IO,Table_name is exited!]\n")
        except IOError:
            fp = open(dirPath+table_name, "w")
            fp.close()
            return
        return

    # 删表
    @classmethod
    def delete_table(cls, table_name):
        try:
            fp = open(dirPath+table_name, "r")
            fp.close()
            os.remove(dirPath+table_name)
            print("[Info],[Table_", table_name, " is exited!]\n")
        except IOError:
            fp = open(dirPath+table_name, "w")
            fp.close()
            return
        return


