from sql.sqlparser import parser
from pengine.logical_engine import *
from pengine.physical_engine import *
from iod.io_cache_manager import *
import json
import glo.glovar

if __name__ == '__main__':
    while True:
        try:
            s = input('> ')
        except EOFError:
            break
        if re.match(r"quit!", s):
            IoCacheManager.quit_main()
            continue
        if re.match(r"show", s):
            s = input('\t> ')
            if re.match(r"d", s):
                s = input('\t\t> ')
                IoCacheManager.show_database(s)
            else:
                s = input('\t\t> ')
                IoCacheManager.show_table(s)
            continue
        ans1 = parser.parse(s)
        print('[Info] [finish Ast]', ans1)
        ans2 = LogicalEngine.run_logical_main(ans1[0])
        print('[Info] [finish ast2log]', ans2)
        ans3 = PhysicalBlock.dfs_plan_tree(ans2)
        print('[Info] [finish log2phy]', ans3.flag, ans3.result, ans3.data)
