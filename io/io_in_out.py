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


class StoreManager:
    @staticmethod
    def object_to_string(obj):
        return pickle.dumps(obj)

    @staticmethod
    def string_to_object(line):
        return pickle.loads(line)

    @staticmethod
    def input_table(self, list_object, table_name):
        list_string = []
        for object_ins in list_object:
            list_string.insert(self.object_to_string(object_ins))
        self.store_table_file(list_string, table_name)

    @staticmethod
    def store_table_file(list_string, table_name):
        nowtablefile = open(table_name, "w")
        for line in list_string:
            nowtablefile.write(line+"\n")
        nowtablefile.close()

    @staticmethod
    def output_table(self, table_name):
        try:
            fp = open(table_name, "r")
            fp.close()
        except IOError:
            print("Table is not accessible.")
            return
        list_string = self.load_table_file(table_name)
        list_object = []
        for object_string in list_string:
            list_object.insert(self.string_to_object(object_string))
        return list_object

    @staticmethod
    def load_table_file(table_name):
        list_string = []
        now_table_file = open(table_name, "r")
        for line in now_table_file.readlines():
            list_string.insert(line)
        now_table_file.close()
        return list_string




