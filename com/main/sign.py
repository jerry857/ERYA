# -*- coding: utf-8 -*

import sys
import os

curPath = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.split(curPath)[0])
import config
from config import loger
from urllib.parse import urlencode
import time
from utils import utils
import requests
import re
import traceback
import json
import random

class Sign():
    def __init__(self, GLOBAL):
        self.GLOBAL = GLOBAL
        self.user_info = None
        self.session = requests.session()
        self.session.headers = {
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 6.0.1; MuMu Build/V417IR) com.chaoxing.mobile/ChaoXingStudy_3_4.3.4_android_phone_494_27 (@Kalimdor)_78e053215bce434394c43c30bb3e7a8a',
            'Accept-Language': 'zh_CN',
        }
        pass

    def login(self, user_info):
        self.user_info = user_info
        login_info = {
            "uname": self.user_info["uname"],
            "code": self.user_info["code"],
            "loginType": GLOBAL["loginType"],
            "roleSelect": GLOBAL["roleSelect"],
        }
        try:
            params = (
                ('cx_xxt_passport', 'json'),
            )
            response = self.session.post('https://passport2-api.chaoxing.com/v11/loginregister', params=params,
                                         data=login_info)
            response = self.session.get('https://sso.chaoxing.com/apis/login/userLogin4Uname.do')
            resp = response.text.encode("utf-8", "ignore").decode("utf-8")
            self.puid = re.search(r"puid\":(.*?),", resp).group(1)
            return True
        except Exception as e:
            loger.error('', exc_info=True)
            loger.info(self.user_info["uname"] + "登陆失败")
            return False

    def sign(self):
        try:
            self.session.headers = {
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0.1; MuMu Build/V417IR; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/52.0.2743.100 Mobile Safari/537.36 com.chaoxing.mobile/ChaoXingStudy_3_4.3.4_android_phone_494_27 (@Kalimdor)_78e053215bce434394c43c30bb3e7a8a',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,en-US;q=0.8',
                'X-Requested-With': 'com.chaoxing.mobile',
            }
            params = (
                ('appId', '253e82f53e6a47fb9dbe8b5c0de5bb0f'),
                ('appKey', '0h1d8P7G5w847du1'),
                ('fidEnc', 'd4ff4bb850f2620a'),
                ('uid', self.puid),
                ('mappId', '116265'),
                ('code', 'VrTLYKxv'),
                ('state', '72413'),
            )
            response = self.session.get('https://office.chaoxing.com/front/clockin/user/clockin', params=params)
            params = (
                ('targetUrl',
                 "https://office.chaoxing.com/front/clockin/user/clockin?appId=253e82f53e6a47fb9dbe8b5c0de5bb0f&appKey=0h1d8P7G5w847du1&fidEnc=d4ff4bb850f2620a&uid={}&mappId=116265&code=VrTLYKxv&state=72413".format(
                     self.puid)),
            )
            response = self.session.get('http://office.chaoxing.com/front/user/login/access', params=params)
            resp = response.text.encode("utf-8", "ignore").decode("utf-8")
            token = re.search(r"oauth.loadInfo\('(.*?)'", resp).group(1)
            params = (
                ('uid', self.puid),
                ('deptid', '4049'),
                ('token', token),
            )
            response = self.session.get('http://office.chaoxing.com/front/user/login/dologin', params=params)
            params = (
                ('appId', '253e82f53e6a47fb9dbe8b5c0de5bb0f'),
                ('appKey', '0h1d8P7G5w847du1'),
                ('fidEnc', 'd4ff4bb850f2620a'),
                ('uid', self.puid),
                ('mappId', '116265'),
                ('code', 'VrTLYKxv'),
                ('state', '72413'),
            )
            response = self.session.get('https://office.chaoxing.com/front/clockin/user/clockin', params=params)
            self.session.headers = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Origin': 'https://office.chaoxing.com',
                'X-Requested-With': 'XMLHttpRequest',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0.1; MuMu Build/V417IR; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/52.0.2743.100 Mobile Safari/537.36 com.chaoxing.mobile/ChaoXingStudy_3_4.3.4_android_phone_494_27 (@Kalimdor)_78e053215bce434394c43c30bb3e7a8a',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Accept-Language': 'zh-CN,en-US;q=0.8',
            }
            data = {
                "clockinLngLat": "",
                "clockinDate": utils.get_date(),
                "clockinAddress": "",
                "remark": "",
                "clockinPicture": [],
            }
            if ("clockinLngLat" in self.user_info) and ("clockinAddress" in self.user_info):
                data["clockinLngLat"] = self.user_info["clockinLngLat"]
                data["clockinAddress"] = self.user_info["clockinAddress"]
            else:
                data["clockinLngLat"] = self.GLOBAL["clockinLngLat"]
                data["clockinAddress"] = self.GLOBAL["clockinAddress"]
            response = self.session.post('https://office.chaoxing.com/data/clockin/user/submit', data=urlencode(data))
            resp = response.json()
            return resp["success"]
        except Exception as e:
            loger.error('', exc_info=True)
            loger.info(self.user_info["uname"] + "\t" + "位置签到失败")
            return False

    def form(self):
        try:
            self.session.headers = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Origin': 'https://office.chaoxing.com',
                'X-Requested-With': 'XMLHttpRequest',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Accept-Language': 'zh-CN,en-US;q=0.8',
            }
            params = (
                ('id', '1584'),
                ('appId', '0a3537b27bc04468af5e68bf9d2462a7'),
                ('appKey', 'z7HqDh2G018DFf1t'),
                ('fidEnc', 'd4ff4bb850f2620a'),
                ('uid', self.puid),
                ('code', 'ZO4a6fF9'),
                ('state', '72413'),
            )

            response = self.session.get('http://office.chaoxing.com/front/apps/forms/fore/apply',
                                        params=params, verify=False)
            # print(response.text)
            form = config.form
            params = (
                ('lookuid', self.puid),
            )
            data = {
                'formId': '1584',
                'formAppId': '',
                'version': '4',
                'formData': str(form).replace("True", "true").replace("False", "false").encode('unicode-escape'),
                'checkCode': '',
                'enc': '',
                'gverify': ''
            }

            reponse = self.session.post('http://office.chaoxing.com/data/apps/forms/fore/user/save', params=params,
                                        data=data, verify=False)
            try:
                resp = reponse.json()
                return resp
            except Exception as e:
                loger.info(self.user_info["uname"] + ":表单提交失败")
                return True
        except Exception as e:
            loger.info(self.user_info["uname"])
            loger.error('', exc_info=True)
            return {"success": False, "msg": "表单提交失败"}

    def form_morning(self):
        try:
            self.session.headers = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Origin': 'https://office.chaoxing.com',
                'X-Requested-With': 'XMLHttpRequest',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Accept-Language': 'zh-CN,en-US;q=0.8',
            }
            params = (
                ('id', '4221'),
                ('appId', '68fea05f172b42df8702d0daf973a12c'),
                ('appKey', '13ocG80L5vI0m40N'),
                ('fidEnc', 'd4ff4bb850f2620a'),
                ("enc","eed61edfd5c197b3867349fceaf673c4"),
                ('uid', self.puid),
                ('mappId', '4172046'),
                ('code', '44gxHBac'),
                ('state', '72413'),
            )

            response = self.session.get('http://office.chaoxing.com/front/apps/forms/fore/apply',
                                        params=params, verify=False)
            # print(response.text)
            formData = json.dumps(config.form_c)
            params = (
                ('lookuid', self.puid),
            )
            data = {
                'formId': '4221',
                'formAppId': '',
                'version': '2',
                'formData': formData,
                'checkCode': '',
                'enc': 'eed61edfd5c197b3867349fceaf673c4',
                'gverify': ''
            }

            reponse = self.session.post('http://office.chaoxing.com/data/apps/forms/fore/user/save', params=params,
                                        data=data, verify=False)
            try:
                resp = reponse.json()
                return resp
            except Exception as e:
                loger.info(self.user_info["uname"])
                loger.error('', exc_info=True)
                return {"success": False, "msg": "表单提交失败"}
        except Exception as e:
            loger.info(self.user_info["uname"])
            loger.error('', exc_info=True)
            return {"success": False, "msg": "表单提交失败"}

    def clear(self):
        self.session.close()
        self.session = requests.session()


if __name__ == '__main__':
    loger.info("运行")
    time.sleep(random.randint(100,300))
    try:
        JSON_INFO = utils.users_info_load(config.users_path)
        GLOBAL = JSON_INFO["GLOBAL"]
        users_info = JSON_INFO["users_info"]
        # print(GLOBAL)
        # print(users_info)
        sign = Sign(GLOBAL)
        error_sign = {}
        error_form = {}
        error_pwd = {}
        try:
            for user_uname in users_info:
                user_info = {
                    "uname": user_uname,
                }
                for key in users_info[user_uname]:
                    user_info[key] = users_info[user_uname][key]
                if users_info[user_uname]["today"] < utils.get_date_0():
                    if sign.login(user_info):
                        if sign.sign():
                            loger.info(
                                users_info[user_uname]["ps"] + "\t" + users_info[user_uname]["industry"] + "： 位置签到成功")
                            time.sleep(0.5)
                        else:
                            loger.info(users_info[user_uname]["ps"] + "\t" + "： 位置签到失败")
                            error_sign[user_uname] = users_info[user_uname]
                        if users_info[user_uname]["industry"] == "computer":
                            message = sign.form_morning()
                            if message["success"]:
                                loger.info(users_info[user_uname]["ps"] + "\t" + message["msg"])
                                time.sleep(0.5)
                            else:
                                loger.info(users_info[user_uname]["ps"] + "\t" + message["msg"])
                                error_form[user_uname] = users_info[user_uname]
                        elif users_info[user_uname]["industry"] == "chyology":
                            message = sign.form_morning()
                            if message["success"]:
                                loger.info(users_info[user_uname]["ps"] + "\t" + message["msg"])
                                time.sleep(0.5)
                            else:
                                loger.info(users_info[user_uname]["ps"] + "\t" + message["msg"])
                                error_form[user_uname] = users_info[user_uname]
                        else:
                            loger.info(users_info[user_uname]["ps"] + "\t" + "： 未知学院")
                            error_form[user_uname] = users_info[user_uname]
                        sign.clear()
                        JSON_INFO["users_info"][user_uname]["today"] = time.time()
                        time.sleep(5)

                    else:
                        loger.info(users_info[user_uname]["ps"] + "\t" + "： 密码错误")
                        error_pwd[user_uname] = users_info[user_uname]
        except Exception as e:
            loger.error('', exc_info=True)
        finally:
            utils.users_info_dump(config.users_path, JSON_INFO)
            utils.users_info_dump(config.error_sign_path, error_sign)
            utils.users_info_dump(config.error_form_path, error_form)
            utils.users_info_dump(config.error_pwd_path, error_pwd)
    except Exception:
        loger.error('', exc_info=True)
