#
# -*- coding:utf-8 -*-
# 作者：Macaulish
# 创建：2019-07-05
# 作用：作为存储管理器，涉及文件读写,序列化

# ======================================
try:
    import cPickle as pickle
except ImportError:
    import pickle
from glo.glovar import *


class StoreManager:
    @staticmethod
    def object_to_string(obj):
        return pickle.dumps(obj)

    @staticmethod
    def string_to_object(line):
        return pickle.loads(line)

    @staticmethod
    def write_table(list_object, table_name):
        list_string = []
        for object_ins in list_object:
            list_string.append(StoreManager.object_to_string(object_ins))
        StoreManager.store_table_file(list_string, table_name)

    @staticmethod
    def store_table_file(list_string, table_name):
        table_file = open(dirPath+table_name, "w")
        for line in list_string:
            table_file.write(line+"\n")
        table_file.close()

    @staticmethod
    def read_table(table_name):
        try:
            fp = open(dirPath+table_name, "r")
            fp.close()
        except IOError:
            print("Table is not accessible.")
            return
        list_string = StoreManager.load_table_file(table_name)
        list_object = []
        for object_string in list_string:
            list_object.append(StoreManager.string_to_object(object_string))
        return list_object

    @staticmethod
    def load_table_file(table_name):
        list_string = []
        now_table_file = open(dirPath+table_name, "r")
        for line in now_table_file.readlines():
            list_string.append(line)
        now_table_file.close()
        return list_string




