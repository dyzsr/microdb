# protobuf序列化组件测试
# coding: utf-8
# failed

# 模块选择,抛弃protobuf,同时json模块也不行,选择pickle
try:
    import cPickle as pickle
except ImportError:
    import pickle

import operator as op


class TestObject:
    id = 1
    obName = "11"


dict = {'Name': 'Zara', 'Age': 7, 'Class': 'First'}

biliBili = TestObject()
nowStr = pickle.dumps(dict)
print(nowStr)
nowBili = pickle.loads(nowStr)
print(nowBili['Name'], " ", nowBili['Class'])

dict1 = {'Name': 'Zara', 'Age': 7}
dict2 = {'Name': 'Mahnaz', 'Age': 27}
dict3 = {'Name': 'Abid', 'Age': 27}
dict4 = {'Age': 7, 'Name': 'Zara'}
dict5 = {'Name': 'Zara'}
print("Return Value : %d", op.eq(dict1, dict2))
print("Return Value : %d", op.eq(dict2, dict3))
print("Return Value : %d", op.eq(dict1, dict4))
