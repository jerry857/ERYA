# -*- coding: utf-8 -*
import sys
import datetime
import os
import time
import logging
import traceback
import json
# 创建一个logger
def get_log():
    curPath = os.path.abspath(os.path.dirname(__file__))
    root_path = os.path.split(os.path.split(curPath)[0])[0]
    logger = logging.getLogger()
    logger.setLevel(logging.ERROR)  # Log等级总开关
    # 创建一个handler，用于写入日志文件
    rq = time.strftime('%Y%m%d', time.localtime(time.time()))
    log_path = root_path + '/Logs/'
    os.makedirs(log_path,exist_ok=True)
    log_name = log_path + rq + '.log'
    logfile = log_name
    fh = logging.FileHandler(logfile, mode='a',encoding="utf-8")
    fh.setLevel(logging.NOTSET)  # 输出到file的log等级的开关
    # 定义handler的输出格式
    formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    fh.setFormatter(formatter)
    rf_handler = logging.StreamHandler(sys.stderr)
    rf_handler.setLevel(logging.DEBUG)
    rf_handler.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(rf_handler)
    # 使用logger.XX来记录错误,这里的"error"可以根据所需要的级别进行修改
    return logger

def get_date():
    GMT_FORMAT = '%a %b %d %Y %H:%M:%S GMT+0800 (CST)'
    return datetime.datetime.now().strftime(GMT_FORMAT)
def get_date_0():
    today = datetime.date.today()
    return int(time.mktime(today.timetuple()))

def users_info_load(users_path):
    with open(users_path, "r") as f:
        users_info = json.load(f)
        return users_info



def users_info_dump(users_path,Udict):
    try:
        with open(users_path, "w") as f:
            # print(Udict)
            json.dump(Udict, f, ensure_ascii=False,indent=4)
        return True
    except Exception as e:
        return False



if __name__ == '__main__':
    curPath = os.path.abspath(os.path.dirname(__file__))
    root_path = os.path.split(curPath)[1]
    print(root_path)