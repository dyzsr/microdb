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
from pengine.query_result import *
import operator as op
import os
from glo.glovar import *


# todo show and load all
class IoCacheManager():
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
        # Result.__init__(self)
        return

    # ===========================================================================
    # 合法性判断：
    # [判断] 是否存在数据库
    @classmethod
    def is_exist_database(cls, database_name):
        schemaPath = glo.GlobalVar.dirPath + '/' + database_name
        if op.eq(os.path.exists(schemaPath), True):
            return True
        return False

    # [判断] databasePath是否被赋值
    @classmethod
    def is_use_database(cls):
        if op.eq(glo.GlobalVar.databasePath, ""):
            return False
        return True

    # [判断] database.table是否存在
    @classmethod
    def is_exist_table(cls, table_name):
        tablePath = glo.GlobalVar.dirPath + '/' + glo.GlobalVar.databasePath + '/' + table_name
        if glo.GlobalVar.Debug == 1:
            glo.Log.write_log('[Debug] [IoCacheManager] [is_exist_table] [',
                              glo.Log.ttstr(os.path.exists(tablePath)), ']')
        if op.eq(os.path.exists(tablePath), True):
            return True
        return False

    # [判断并返回result类] database.table是否存在
    @classmethod
    def enable_table(cls, table_name):
        result = Result()
        if op.eq(cls.is_use_database(), False):
            result.flag = True
            result.result = []
            result.result.append(str('[Error] [ don\'t use any database]'))
        elif op.eq(cls.is_exist_table(table_name), False):
            result.flag = True
            result.result = []
            result.result.append(str('[Error] [ don\'t exist table]'))
        return result

    # ======================================================
    # 替换策略,待实现
    @classmethod
    def LRU(cls):
        now_cache = CacheBlock()
        cls.list_cache_block.append(now_cache)
        cls.list_cache_block_name.append("")
        return len(cls.list_cache_block)-1

    # ======================================================
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
            glo.Log.write_log('[Debug] [IoCacheManager] [load_right_now] [metadata:', glo.Log.ttstr(cls.list_cache_block[cache_index].meta), ']')
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
                glo.Log.write_log('[Debug] [IoCacheManager] [check_table_load] [', table_name, ']')
            cls.store_right_now(table_index)
        return

    # 是否需要载入，如果有则不执行，如有没有则载入
    @classmethod
    def check_table_load(cls, table_name):
        table_index = cls.find_cache_block(table_name)
        if table_index == -1:
            if glo.GlobalVar.Debug == 1:
                glo.Log.write_log('[Debug] [IoCacheManager] [check_table_load] [', table_name, ']')
            cls.load_right_now(table_name)
        return

    # 增空条目
    @classmethod
    def insert_table_none_entry(cls, table_name):
        if glo.GlobalVar.Debug == 1:
            glo.Log.write_log('[Debug] [IoCacheManager] [insert_table_none_entry] [input:', table_name, ']')
        # 先判断现在是否使用数据库
        result = cls.enable_table(table_name)
        if op.eq(result.flag, True):
            return result
        cls.check_table_load(table_name)
        table_index = cls.find_cache_block(table_name)
        if glo.GlobalVar.Debug == 1:
            glo.Log.write_log('[Debug] [IoCacheManager] [insert_table_none_entry] [table_index:', table_index, ']')
        more_data = dict()
        for column in IoCacheManager.list_cache_block[table_index].meta:
            more_data[column['column']] = None
        return more_data

    # 增条目
    @classmethod
    def insert_table_entry(cls, table_name, entry):
        if glo.GlobalVar.Debug == 1:
            glo.Log.write_log('[Debug] [IoCacheManager] [insert_table_entry] [input:', table_name, '-', glo.Log.ttstr(entry), ']')
        # 先判断现在是否使用数据库
        result = cls.enable_table(table_name)
        if op.eq(result.flag, True):
            return result
        cls.check_table_load(table_name)
        table_index = cls.find_cache_block(table_name)
        if glo.GlobalVar.Debug == 1:
            glo.Log.write_log('[Debug] [IoCacheManager] [insert_table_entry] [table_index:', table_index, ']')
        # todo : 增加数据时的合法性校验放在哪个地方做check data
        #
        IoCacheManager.list_cache_block[table_index]\
            .insert_table_entry(entry)
        if glo.GlobalVar.Debug == 1:
            glo.Log.write_log('[Debug] [IoCacheManager] [insert_table_entry] [value:',
                  glo.Log.ttstr(IoCacheManager.list_cache_block[table_index].data), ']')
        result.result = []
        result.result.append(str('[Success] [insert_table_entry]'))
        # 立即存
        if int(glo.GlobalVar.save_right_now) == 1:
            cls.store_right_now(table_index)
        return result

    # 增条目时不指定column,则利用元信息list
    @classmethod
    def insert_table_entry_list(cls, table_name, entry_list):
        result = cls.enable_table(table_name)
        if op.eq(result.flag, True):
            return result
        cls.check_table_load(table_name)
        table_index = cls.find_cache_block(table_name)
        if op.eq(len(entry_list), len(IoCacheManager.list_cache_block[table_index].meta)):
            now_entry = dict()
            now_entry[table_name] = dict()
            index = 0
            for column in IoCacheManager.list_cache_block[table_index].meta:
                now_entry[table_name][column['column']] = entry_list[index]
                index += 1
            IoCacheManager.list_cache_block[table_index]\
                .insert_table_entry(now_entry)
        else:
            result.flag = True
            result.result = []
            result.result.append(str('[Error] [ the number of item.key is equal to the number of column'))
        return result

    # 删
    @classmethod
    def delete_table_entry(cls, table_name, entry):
        result = cls.enable_table(table_name)
        if op.eq(result.flag, True):
            return result
        cls.check_table_load(table_name)
        table_index = cls.find_cache_block(table_name)
        son = IoCacheManager.list_cache_block[table_index] \
            .delete_table_entry(entry)
        if op.eq(son.flag, True):
            return son
        return result

    # 改
    @classmethod
    def update_table_entry(cls, table_name, oldentry, newentry):
        result = cls.enable_table(table_name)
        if op.eq(result.flag, True):
            return result
        cls.check_table_load(table_name)
        table_index = cls.find_cache_block(table_name)
        result = IoCacheManager.list_cache_block[table_index] \
            .update_table_entry(oldentry, newentry)
        if op.eq(result.flag, True):
            return result
        result.result = []
        result.result.append(str('[Error] [update_table_entry]'))
        return result

    # 输出整体表
    @classmethod
    def select_table_entry(cls, table_name):
        result = cls.enable_table(table_name)
        if op.eq(result.flag, True):
            return result
        cls.check_table_load(table_name)
        table_index = cls.find_cache_block(table_name)
        result.result = IoCacheManager.list_cache_block[table_index] \
            .all_table_read()
        return result

    # add name in list
    @classmethod
    def add_name_in_list(cls, filePath, entry):
        if op.eq(os.path.exists(filePath), False):
            fp = open(filePath, "w")
            fp.close()
        fp = open(filePath, "r")
        list_table = []
        for line in fp.readlines():
            list_table.append(json.loads(line))
        list_table.append(entry)
        fp.close()
        fp = open(filePath, "w")
        for line in list_table:
            fp.write(json.dumps(line) + '\n')
        fp.close()
        return
    # del name in list
    @classmethod
    def remove_name_in_list(cls, filePath, enrty):
        fp = open(filePath, "r")
        list_table = []
        for line in fp.readlines():
            list_table.append(json.loads(line))
        list_table.remove(enrty)
        fp.close()
        fp = open(filePath, "w")
        for line in list_table:
            fp.write(json.dumps(line) + '\n')
        fp.close()
        return

    # 创表
    @classmethod
    def create_table(cls, table_name, columns):
        # if op.eq(databasePath,""):
        #     glo.Log.write_log("[Error] [Don't use a database or database don't exist]")
        #     return
        result = Result()
        if op.eq(cls.is_use_database(), False):
            result.flag = True
            result.result = []
            result.result.append(str('[Error] [ don\'t use any database]'))
            glo.Log.write_log('[Debug] [IoCacheManager] [create_table] [', result.flag,
                              glo.Log.ttstr(result.result), ']')
            glo.Log.write_log('[Debug] [IoCacheManager] [create_table] [',
                              result.flag, glo.Log.ttstr(result.result), ']')
            return result
        elif op.eq(cls.is_exist_table(table_name), True):
            result.flag = True
            result.result = []
            result.result.append(str('[Error] [ there is a table with the same name]'))
            return result
        tablePath = glo.GlobalVar.dirPath+'/' + glo.GlobalVar.databasePath + '/' + table_name
        if glo.GlobalVar.Debug == 1:
            glo.Log.write_log('[Debug] [IoCacheManager] [create_table] [input:', tablePath, table_name, ']')
            # glo.Log.write_log('[GlobalVar.Debug] [IoCacheManager] [create_table] [input:', tablePath, table_name, ']')
        #  tablePath = Global.dirPath + '/' + table_name
        os.makedirs(tablePath)
        cls.insert_table_in_databaselist(table_name)
        fp = open(tablePath +'/'+'meta', "w")
        for column in columns:
            fp.write(json.dumps(column)+"\n")
        fp.close()
        fp = open(tablePath + '/' + 'data', "w")
        fp.close()
        #   fp = open(Global.dirPath + '/' + table_name, "r")
        #    fp = open(Global.dirPath+'/'+table_name, "r")
        return result

    # 创数据库
    # todo : 创建数据库的原信息存储含有的表list
    @classmethod
    def create_database(cls, database_name):
        schemaPath = glo.GlobalVar.dirPath + '/' + database_name
        result = Result()
        if op.eq(cls.is_exist_database(database_name), True):
            result.flag = True
            result.result = []
            result.result.append(str('[Error] [ there is a database with the same name]'))
            return result
        else:
            os.makedirs(schemaPath)
            fp = open(schemaPath + '/' + 'meta', "w")
            fp.close()
            cls.add_name_in_list(glo.GlobalVar.dirPath + '/meta', database_name)
        if glo.GlobalVar.Debug == 1:
            glo.Log.write_log('[Debug] [IoCacheManager] [create_table] [', glo.Log.ttstr(result.flag), glo.Log.ttstr(result.result), ']')
        return result

    # 删表
    @classmethod
    def drop_table(cls, table_name):
        result = cls.enable_table(table_name)
        if op.eq(result.flag, True):
            return result
        tablePath = glo.GlobalVar.dirPath + '/' + glo.GlobalVar.databasePath + '/' + table_name
        if glo.GlobalVar.Debug == 1:
            glo.Log.write_log('[Debug] [IoCacheManager] [delete_table] [', table_name, ']')
        #  tablePath = Global.dirPath + '/' + table_name
        StoreManager.remove_dir(tablePath)
        #   fp = open(Global.dirPath + '/' + table_name, "r")
        #    fp = open(Global.dirPath+'/'+table_name, "r")
        return result

    # 删数据库
    @classmethod
    def drop_database(cls, database_name):
        schemaPath = glo.GlobalVar.dirPath + '/' + database_name
        if glo.GlobalVar.Debug == 1:
            glo.Log.write_log('[Debug] [IoCacheManager] [delete_table] [', schemaPath, ']')
        result = Result()
        if op.eq(cls.is_exist_database(database_name), True):
            StoreManager.remove_dir(schemaPath)
            cls.remove_name_in_list(glo.GlobalVar.dirPath + '/meta', database_name)
            if op.eq(glo.GlobalVar.databasePath, database_name):
                glo.GlobalVar.databasePath = ""
                cls.list_cache_block = []
                cls.list_cache_block_name = []
        else:
            result.flag = True
            result.result = []
            result.result.append(str('[Error] [ Database isn\'t exited!]'))
        if glo.GlobalVar.Debug == 1:
            glo.Log.write_log('[Debug] [IoCacheManager] [create_table] [', result.flag, glo.Log.ttstr(result.result), ']')
        return result

    # 在数据库原信息中删表：在list中增加表名
    @classmethod
    def delete_table_in_databaselist(cls, table_name):
        if glo.GlobalVar.Debug == 1:
            glo.Log.write_log('[Debug] [IoCacheManager] [delete_table_in_databaselist] [', table_name, ']')
        result = cls.enable_table(table_name)
        if op.eq(result.flag, True):
            return result
        schemaPath = glo.GlobalVar.dirPath + '/' + glo.GlobalVar.databasePath
        cls.remove_name_in_list(schemaPath + '/meta', table_name)
        return

    # 在数据库原信息中增表：在list中增加表名
    @classmethod
    def insert_table_in_databaselist(cls, table_name):
        if glo.GlobalVar.Debug == 1:
            glo.Log.write_log('[Debug] [IoCacheManager] [insert_table_in_databaselist] [', glo.GlobalVar.dirPath, glo.GlobalVar.databasePath, table_name, ']')
        schemaPath = glo.GlobalVar.dirPath + '/' + glo.GlobalVar.databasePath
        cls.add_name_in_list(schemaPath + '/meta', table_name)
        return

    # 输出数据库元信息
    @classmethod
    def show_database(cls):
        result = Result()
        # todo database 需要保留数据库元信息
        if glo.GlobalVar.Debug == 1:
            glo.Log.write_log('[Debug] [IoCacheManager] [show_database] [', glo.GlobalVar.dirPath, ']')
            glo.Log.write_log('[Debug] [IoCacheManager] [show_database] [', glo.GlobalVar.dirPath, ']')

        fp = open(glo.GlobalVar.dirPath + '/' + 'meta', "r")
        result.result = []
        for line in fp.readlines():
            result.result.append(json.loads(line))
        fp.close()
        if glo.GlobalVar.Debug == 1:
            glo.Log.write_log('[Debug] [IoCacheManager] [show_database] [', result.flag, glo.Log.ttstr(result.result), ']')
        return result

    # 输出当前数据库下表列表
    @classmethod
    def show_table(cls):
        result = Result()
        if op.eq(cls.is_use_database(), False):
            result.flag = True
            result.result = []
            result.result.append(str('[Error] [ don\'t use any database]'))
            return result
        schemaPath = glo.GlobalVar.dirPath + '/' + glo.GlobalVar.databasePath
        # todo database 需要保留数据库元信息
        if glo.GlobalVar.Debug == 1:
            glo.Log.write_log('[Debug] [IoCacheManager] [show_table] [', schemaPath, ']')
        fp = open(schemaPath + '/' + 'meta', "r")
        result.result = []
        for line in fp.readlines():
            result.result.append(json.loads(line))
        fp.close()
        if glo.GlobalVar.Debug == 1:
            glo.Log.write_log('[Debug] [IoCacheManager] [show_table] [', result.flag, glo.Log.ttstr(result.result), ']')
        return result

    # 输出当前数据库的表的列
    @classmethod
    def show_columns(cls, table_name):
        result = cls.enable_table(table_name)
        if op.eq(result.flag, True):
            return result
        tablePath = glo.GlobalVar.dirPath + '/' + glo.GlobalVar.databasePath + '/' + table_name
        fp = open(tablePath + '/' + 'meta', "r")
        result.result = []
        for line in fp.readlines():
            now_dict = dict()
            glo.Log.write_log('[Debug] [IoCacheManager] [show_database] [Running', line, ']')
            now_dict[table_name] = json.loads(line)
            result.result.append(now_dict)
        fp.close()
        if glo.GlobalVar.Debug == 1:
            glo.Log.write_log('[Debug] [IoCacheManager] [show_database] [output',
                              result.flag, glo.Log.ttstr(result.result), ']')
        return result

    @classmethod
    def quit_main(cls):
        for index in range(len(cls.list_cache_block_name)):
            cls.store_right_now(index)


