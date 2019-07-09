import time


class GlobalVar:
    dirPath = "D:/dbms/store"
    databasePath = ""
    Debug = 1
    save_right_now = 1


class Log:
    @staticmethod
    def write_log(*str ):
        strout = '[' +time.asctime(time.localtime()) + ']'
        if len(str) != 0:
            for p in str:
                strout = strout + " " + Log.ttstr(p)
        print(strout)
        with open(GlobalVar.dirPath+'/log', 'a+') as f:
            f.write(strout+'\n')

    @staticmethod
    def ttstr(obj):
        if isinstance(obj, int):
            return str(obj)
        elif isinstance(obj, str):
            return obj
        elif isinstance(obj, float):
            return str(obj)
        elif isinstance(obj, bool):
            return str(obj)
        elif isinstance(obj, list):
            return str(obj)
        elif isinstance(obj, tuple):
            return obj.__str__()
        elif isinstance(obj, dict):
            return str(obj)
        elif isinstance(obj, set):
            return str(obj)
        return str(obj)


