#
# -*- coding:utf-8 -*-
# 作者：Macaulish
# 创建：2019-07-05
# 作用：物理计划执行
# 主要涉及： 查询结果
#
import operator as op


class Result:
    def __init__(self):
        self.flag = False
        self.result = ""
        pass

    def class_to_dict(self):
        now_dict = dict()
        now_dict['flag'] = self.flag
        now_dict['result'] = self.result
        return now_dict

    def exist_error(self):
        return op.eq(self.flag, False)
