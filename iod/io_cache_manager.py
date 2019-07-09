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

from iod.io_cache import *
from iod.io_in_out import *

import operator as op
import os
from glo.glovar import *


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
        cls.list_cache_block[cache_index].\
            get_metadata(StoreManager.get_table_metadata(table_name))
        if glo.GlobalVar.Debug == 1:
            print('[Debug] [IoCacheManager] [load_right_now] [metadata:', cls.list_cache_block[cache_index].meta, ']')
        return

    # 立即表载出
    @classmethod
    def store_right_now(cls, index):
        StoreManager.write_table(cls.list_cache_block[index], cls.list_cache_block_name[index])
        cls.list_cache_block_name.pop(index)
        cls.list_cache_block.pop(index)
        return

    @classmethod
    def save_table_and_remove(cls, table_name):
        table_index = cls.find_cache_block(table_name)
        if table_index > -1:
            if glo.GlobalVar.Debug == 1:
                print('[GlobalVar.Debug] [IoCacheManager] [check_table_load] [', table_name, ']')
            cls.store_right_now(table_index)
        return

    # 是否需要载入，如果有则不执行，如有没有则载入
    @classmethod
    def check_table_load(cls, table_name):
        table_index = cls.find_cache_block(table_name)
        if table_index == -1:
            if glo.GlobalVar.Debug == 1:
                print('[GlobalVar.Debug] [IoCacheManager] [check_table_load] [', table_name, ']')
            cls.load_right_now(table_name)
        return

    # 增条目
    @classmethod
    def insert_table_entry(cls, table_name, entry):
        if glo.GlobalVar.Debug == 1:
            print('[GlobalVar.Debug] [IoCacheManager] [insert_table_entry] [input:', table_name, '-', entry, ']')
        cls.check_table_load(table_name)
        table_index = cls.find_cache_block(table_name)
        if glo.GlobalVar.Debug == 1:
            print('[GlobalVar.Debug] [IoCacheManager] [insert_table_entry] [table_index:', table_index, ']')
        # todo : 增加数据时的合法性校验放在哪个地方做check data
        #
        IoCacheManager.list_cache_block[table_index]\
            .insert_table_entry(entry)
        if glo.GlobalVar.Debug == 1:
            print('[GlobalVar.Debug] [IoCacheManager] [insert_table_entry] [value:',
                  IoCacheManager.list_cache_block[table_index].data, ']')
        cls.store_right_now(table_index)
        return

    # 增条目时不指定column,则利用元信息list
    @classmethod
    def insert_table_entry_list(cls, table_name, entry_list):
        cls.check_table_load(table_name)
        table_index = cls.find_cache_block(table_name)
        if op.eq(len(entry_list), len(IoCacheManager.list_cache_block[table_index].meta)):
            now_entry = dict()
            now_entry[table_name] = dict()
            index = 0
            for column in IoCacheManager.list_cache_block[table_index].meta:
                now_entry[table_name][column['column']] = entry_list[index]
                index += 1
            IoCacheManager.list_cache_block[table_index] \
                .insert_table_entry(now_entry)

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
        if op.eq(glo.GlobalVar.databasePath, ""):
            print('[Error] [ don\'t use database ]\n')
            return CacheBlock()
        cls.check_table_load(table_name)
        table_index = cls.find_cache_block(table_name)
        return IoCacheManager.list_cache_block[table_index] \
            .all_table_read()

    # 创表
    @classmethod
    def create_table(cls, table_name, columns):
        # if op.eq(databasePath,""):
        #     print("[Error] [Don't use a database or database don't exist]")
        #     return

        tablePath = glo.GlobalVar.dirPath+'/' + glo.GlobalVar.databasePath + '/' + table_name
        if glo.GlobalVar.Debug == 1:
            print('[GlobalVar.Debug] [IoCacheManager] [create_table] [input:', tablePath, table_name, ']')
        #  tablePath = Global.dirPath + '/' + table_name
        if op.eq(os.path.exists(tablePath), False):
            os.makedirs(tablePath)
            cls.insert_table_in_databaselist(table_name)
            fp = open(tablePath +'/'+'meta', "w")
            for column in columns:
                fp.write(json.dumps(column)+"\n")
            fp.close()
            fp = open(tablePath + '/' + 'data', "w")
            fp.close()
        else:
            print("[Error] [Table_name is exited!]\n")
        #   fp = open(Global.dirPath + '/' + table_name, "r")
        #    fp = open(Global.dirPath+'/'+table_name, "r")
        return

    # 创数据库
    # todo : 创建数据库的原信息存储含有的表list
    @classmethod
    def create_database(cls, database_name):
        schemaPath = glo.GlobalVar.dirPath + '/' + database_name
        if op.eq(os.path.exists(schemaPath), False):
            os.makedirs(schemaPath)
            fp = open(schemaPath + '/' + 'meta', "w")
            fp.close()
        else:
            print("[Error] [database is exited!]\n")
        return

    # 删表
    @classmethod
    def drop_table(cls, table_name):
        tablePath = glo.GlobalVar.dirPath + '/' + glo.GlobalVar.databasePath + '/' + table_name
        if glo.GlobalVar.Debug == 1:
            print('[GlobalVar.Debug] [IoCacheManager] [delete_table] [', table_name, ']')
        #  tablePath = Global.dirPath + '/' + table_name
        if op.eq(os.path.exists(tablePath), True):
            StoreManager.remove_dir(tablePath)
        else:
            print("[Error] [Table_name isn't exited!]\n")
        #   fp = open(Global.dirPath + '/' + table_name, "r")
        #    fp = open(Global.dirPath+'/'+table_name, "r")
        return

    # 删数据库
    @classmethod
    def drop_database(cls, database_name):
        schemaPath = glo.GlobalVar.dirPath + '/' + database_name
        # todo database 需要保留数据库元信息
        if glo.GlobalVar.Debug == 1:
            print('[GlobalVar.Debug] [IoCacheManager] [delete_table] [', schemaPath, ']')
        #  tablePath = Global.dirPath + '/' + table_name
        # clear cache
        list_cache_block = []
        list_cache_block_name = []
        if op.eq(os.path.exists(schemaPath), True):
            StoreManager.remove_dir(schemaPath)
            glo.GlobalVar.databasePath = ""
        else:
            print("[Error] [Database isn't exited!]\n")
        #   fp = open(Global.dirPath + '/' + table_name, "r")
        #    fp = open(Global.dirPath+'/'+table_name, "r")
        return

    # 删表：在list中增加表名
    @classmethod
    def delete_table_in_databaselist(cls, table_name):
        if glo.GlobalVar.Debug == 1:
            print('[GlobalVar.Debug] [IoCacheManager] [delete_table_in_databaselist] [', table_name, ']')
        schemaPath = glo.GlobalVar.dirPath + '/' + glo.GlobalVar.databasePath
        fp = open(schemaPath+ '/' + 'meta' , "r")
        list_table = []
        for line in fp.readlines():
            print('[GlobalVar.Debug] [IoCacheManager] [delete_table_in_databaselist2] [', line, ']')
            list_table.append(json.loads(line))
        if glo.GlobalVar.Debug == 1:
            print('[GlobalVar.Debug] [IoCacheManager] [delete_table_in_databaselist2] [', list_table, ']')
        list_table.remove(table_name)
        fp.close()
        fp = open(schemaPath+ '/' + 'meta' , "w")
        for line in list_table:
            fp.write(json.dumps(line)+'\n')
        fp.close()

    # 增表：在list中增加表名
    @classmethod
    def insert_table_in_databaselist(cls, table_name):
        if glo.GlobalVar.Debug == 1:
            print('[GlobalVar.Debug] [IoCacheManager] [insert_table_in_databaselist] [', glo.GlobalVar.dirPath, glo.GlobalVar.databasePath, table_name, ']')
        schemaPath = glo.GlobalVar.dirPath + '/' + glo.GlobalVar.databasePath
        fp = open(schemaPath + '/' + 'meta' , "r")
        list_table = []
        for line in fp.readlines():
            list_table.append(json.loads(line))
        list_table.append(table_name)
        fp.close()
        fp = open(schemaPath+ '/' + 'meta' , "w")
        for line in list_table:
            fp.write(json.dumps(line)+'\n')
        fp.close()



