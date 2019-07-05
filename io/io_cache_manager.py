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


class IoCacheManager:
    # 立即表载入
    def load_right_now(self, table_name):
        return

    # 立即表载出
    def store_right_now(self):
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


