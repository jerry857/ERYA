# -*- coding: utf-8 -*
import os

curPath = os.path.abspath(os.path.dirname(__file__))
root_path = os.path.split(curPath)[0]
from utils import utils

users_path = os.path.join(root_path, "config/users.json")
loger = utils.get_log()
readFromLastChapter=True
readFrom0read=True
readTimelimit=180#单位second 0为无限制
