# protobuf序列化组件测试
# coding: utf-8
# failed

# 模块选择,抛弃protobuf,同时json模块也不行,选择pickle
try:
    import cPickle as pickle
except ImportError:
    import pickle


class TestObject:
    id = 1
    obName = "11"


biliBili = TestObject()
nowStr = pickle.dumps(biliBili)
print(nowStr)
nowBili = pickle.loads(nowStr)
print(nowBili.id, " ", nowBili.obName)
