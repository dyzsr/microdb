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

import io.StoreManager
import operator as op


class IoCacheManager:
    cache_block_Limit = 3
    #
    list_cache_block = []
    # 表名
    list_cache_block_name = []
    # 是否失效
    list_cache_block_flag = []

    # 替换策略,待实现
    def LRU(self):
        return

    def find_cache_block(self, table_name):
        list_name = self.list_cache_block_name
        index = 0
        for block_name in list_name:
            if op.eq(block_name, table_name):
                return index
            else:
                index += 1
        if index == len(list_name):
            return -1

    # 立即表载入
    def load_right_now(self, table_name):
        return

    # 立即表载出
    def store_right_now(self):
        return

    # 是否需要载入
    def check_table_load(self):
        return

    # 增
    def insert_table_entry(self):
        return

    # 删
    def delete_table_entry(self):
        return

    # 改
    def update_table_entry(self):
        return

    # 查
    def select_table_entry(self):
        return

    # 创表
    def create_table(self):
        return

    # 删表
    def delete_table(self):
        return


