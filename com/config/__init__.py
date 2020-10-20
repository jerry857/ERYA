# -*- coding: utf-8 -*
import os

curPath = os.path.abspath(os.path.dirname(__file__))
root_path = os.path.split(curPath)[0]
from utils import utils

users_path = os.path.join(root_path, "config/users.json")
error_sign_path = os.path.join(root_path, "config/error_sign.json")
error_form_path = os.path.join(root_path, "config/error_form.json")
error_pwd_path = os.path.join(root_path, "config/error_pwd.json")

loger = utils.get_log()
readFromLastChapter=True
readFrom0read=False
readTimelimit=0#单位second 0为无限制
