from sql.sqlparser import parser
from pengine.logical_engine import *
from pengine.physical_engine import *
import json
import glo.glovar

if __name__ == '__main__':
    while True:
        try:
            s = input('> ')
        except EOFError:
            break
        ans1 = parser.parse(s)
        print('[Info] [finish Ast]', ans1)
        ans2 = LogicalEngine.run_logical_main(ans1)
        print('[Info] [finish ast2log]', ans2)
        ans3 = PhysicalBlock.dfs_plan_tree(ans2)
        print('[Info] [finish log2phy]', ans3.data)
