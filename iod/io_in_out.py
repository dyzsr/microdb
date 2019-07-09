#
# -*- coding:utf-8 -*-
# 作者：Macaulish
# 创建：2019-07-05
# 作用：作为存储管理器，涉及文件读写,序列化

# ======================================
from glo.glovar import *
try:
    import cPickle as pickle
except ImportError:
    import pickle
import json
import os
import operator as op


class StoreManager:
    @staticmethod
    def object_to_string(obj):
        return json.dumps(obj)

    @staticmethod
    def string_to_object(line):
        return json.loads(line)

    @staticmethod
    def write_table(list_object, table_name):
        if GlobalVar.Debug == 1:
            print('[Debug] [StoreManager] [write_table] [list_object:', list_object.data,
                  'table_name',  table_name, ']')
        list_string = []
        for object_ins in list_object.data:
            list_string.append(StoreManager.object_to_string(object_ins))
        StoreManager.store_table_file(list_string, table_name)

    @staticmethod
    def store_table_file(list_string, table_name):
        tablePath = GlobalVar.dirPath + '/' + GlobalVar.databasePath + '/' + table_name
        table_file = open(tablePath + '/' + 'data', "w")
        for line in list_string:
            if GlobalVar.Debug == 1:
                print('[Debug] [StoreManager] [store_table_file] [line:', line, ']')
            table_file.write(line+"\n")
        table_file.close()


    @staticmethod
    def get_table_metadata(table_name):
        tablePath = GlobalVar.dirPath + '/' + GlobalVar.databasePath + '/' + table_name
        if op.eq(os.path.exists(tablePath), False):
            print("[Error] [Table is not accessible.]")
            return
        list_string = open(tablePath + '/' + 'meta', "r")
        list_meta = []
        for line in list_string.readlines():
            list_meta.append(json.loads(line))
        return list_meta

    @staticmethod
    def read_table(table_name):
        tablePath = GlobalVar.dirPath + '/' + GlobalVar.databasePath + '/' + table_name
        if op.eq(os.path.exists(tablePath), False):
            print("[Error] [Table is not accessible.]")
            return
        list_string = StoreManager.load_table_file(tablePath)
        list_object = []
        for object_string in list_string:
            list_object.append(StoreManager.string_to_object(object_string))
        return list_object

    @staticmethod
    def load_table_file(tablePath):
        list_string = []
        now_table_file = open(tablePath+'/'+'data', "r")
        for line in now_table_file.readlines():
            list_string.append(line)
        now_table_file.close()
        return list_string

    @staticmethod
    def remove_dir(dir):
        dir = dir.replace('\\', '/')
        if os.path.isdir(dir):
            for p in os.listdir(dir):
                StoreManager.remove_dir(os.path.join(dir,p))
            if os.path.exists(dir):
                os.rmdir(dir)
        else:
            if os.path.exists(dir):
                os.remove(dir)




