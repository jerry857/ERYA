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
import hashlib
import math

class Shuake():
    def __init__(self, GLOBAL):
        self.GLOBAL = GLOBAL
        self.user_info = None
        self.session = requests.session()
        self.session.headers = {
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0.1; MuMu Build/V417IR; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/52.0.2743.100 Mobile Safari/537.36 com.chaoxing.mobile/ChaoXingStudy_3_4.3.4_android_phone_494_27 (@Kalimdor)_78e053215bce434394c43c30bb3e7a8a',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,en-US;q=0.8',
            'X-Requested-With': 'com.chaoxing.mobile',
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

    def init_courseList(self):
        """
        :return 以节id作为对课程列表的key
        """
        try:
            response = self.session.get('https://tsjy.chaoxing.com/plaza/course/215091538/classify-list')
            courseList = response.json()["data"]["list"]
            self.courseList = {}
            for course in courseList:
                self.courseList[course["nodeId"]] = {"jname": course["name"], "coursename": course["pnodeName"],
                                                     "courseId": course["courseId"]}
            print(self.courseList)
            return True
        except Exception as e:
            loger.error('', exc_info=True)
            loger.info(self.user_info["uname"] + "\t" + "获取课程列表失败")
            return False

    def init_clazzList(self):
        """
                :return 以课程id作为对班列表的key
        """
        try:
            params = (
                ('view', 'json'),
                ('rss', '1'),
            )
            response = self.session.get('http://mooc1-api.chaoxing.com/mycourse/backclazzdata', params=params)
            clazzList = response.json()["channelList"]
            self.clazzList = {}
            for clazz in clazzList:
                for i in range(len(clazz["content"]["course"]["data"])):
                    self.clazzList[clazz["content"]["course"]["data"][i]["id"]] = {
                        "courseTeacher": clazz["content"]["course"]["data"][i]["teacherfactor"],
                        "clazzId": clazz["content"]["id"], "courseName": clazz["content"]["course"]["data"][i]["name"]}
            print(self.clazzList)
            return True
        except Exception as e:
            loger.error('', exc_info=True)
            loger.info(self.user_info["uname"] + "\t" + "获取班级列表失败")
            return False

    def init_PageList(self):
        # courseid为大课的id 每个大课又包含许多单元（也可以叫做节）
        # jnodeid为单元id（节id）
        # 返回本单元对应视频列表 以视频id作为索引
        try:
            self.pageList = []
            for jnodeid in self.courseList:
                params = (
                    ('page', '1'),
                    ('classifyId', jnodeid),
                    ('element', ''),
                    ('status', ''),
                    ('point', ''),
                    ('name', ''),
                )
                response = self.session.get(
                    'https://tsjy.chaoxing.com/plaza/course/{}/node-list'.format(self.courseList[jnodeid]["courseId"]),
                    params=params)
                _VideoList = response.json()
                for video in _VideoList["data"]["list"]:
                    _video = {"pageId": video['nodeId'], "jnodeid": video['classifyId'],
                              'courseId': int(video['courseId']), 'classifyName': video['classifyName'],
                              'name': video['name'], 'finishStatus': video['finishStatus'], 'read': video['read']}
                    self.pageList.append(_video)
            print(self.pageList)
            return True
        except Exception as e:
            loger.error('', exc_info=True)
            loger.info(self.user_info["uname"] + "\t" + "获取视频列表失败")
            return False
    def get_videos_infoList(self, page):
        # video 为videoList的字典
        pageid = page["pageId"]
        courseid = page["courseId"]
        clazzid = self.clazzList[courseid]['clazzId']
        try:
            params = (
                ('clazzid', clazzid),
                ('courseid', courseid),
                ('knowledgeid', pageid),
                ('num', '1'),
                ('isPhone', '1'),
                ('control', 'true'),
            )
            response = self.session.get('https://mooc1-api.chaoxing.com/knowledge/cards', params=params).text
            VideosInfo = re.search(r"window.AttachmentSetting =(.*?);\n", response).group(1)
            VideosInfo = json.loads(VideosInfo)["attachments"]
            return VideosInfo
        except Exception as e:
            loger.error('', exc_info=True)
            loger.info(self.user_info["uname"] + "\t" + "获取视频信息失败")
            return False
    def get_scoreInfo(self,classId,courseId):
        try:
            params = (
                ('classId', classId),
                ('userId', self.puid),
            )
            response = self.session.get('https://tsjy.chaoxing.com/plaza/score/{}/day-score'.format(courseId), params=params)
            return response.json()["data"]["rule"]
        except Exception as e:
            loger.error('', exc_info=True)
            loger.info(self.user_info["uname"] + "\t" + "获取分数信息失败")
            return False
    def shuake(self):
        self.init_courseList()
        self.init_clazzList()
        self.init_PageList()
        try:
            for pageinfo in shuake.pageList:
                videosinfoList = self.get_videos_infoList(pageinfo)
                for videoinfo in videosinfoList:
                    scoreInfo=self.get_scoreInfo(self.clazzList[pageinfo['courseId']]['clazzId'],pageinfo['courseId'])
                    if scoreInfo["dayScore"]>=scoreInfo["dailyMaxScore"]:
                        print("今天已刷够",scoreInfo["dailyMaxScore"],"分")
                    if videoinfo['type'] != "video":
                        continue
                    if 'isPassed' in videoinfo and videoinfo['isPassed']:
                        continue
                    params = (
                        ('k', '123845'),
                        ('flag', 'normal'),
                        ('_dc', '1602816161570'),
                    )
                    videoinfo2 = self.session.get(
                        'https://mooc1-api.chaoxing.com/ananas/status/{}'.format(videoinfo["objectId"]), params=params).json()
                    for i in range(math.ceil(videoinfo2['duration']/60)):
                        playingTime = i*60 if i*60<=videoinfo2['duration'] else videoinfo2['duration']
                        print("\r当前正在刷课：", "playingTime:{}".format(playingTime), pageinfo["classifyName"],
                              pageinfo["name"],end="")
                        # [clazzId][userid][jobid][objectId][currentTimeSec * 1000][d_yHJ!$pdA~5][duration * 1000][clipTime]
                        enc = "[{}][{}][{}][{}][{}][d_yHJ!$pdA~5][{}][{}]".format(self.clazzList[pageinfo['courseId']]['clazzId'],
                                                                                  self.puid, videoinfo["jobid"],
                                                                                  videoinfo["objectId"], playingTime * 1000,
                                                                                  videoinfo2['duration'] * 1000,
                                                                                  '0_' + str(videoinfo2['duration']))
                        md5enc=hashlib.md5(enc.encode()).hexdigest()
                        params = (
                            ('clazzId', self.clazzList[pageinfo['courseId']]['clazzId']),
                            ('playingTime', playingTime),
                            ('duration', videoinfo2['duration']),
                            ('clipTime', '0_' + str(videoinfo2['duration'])),
                            ('objectId', videoinfo["objectId"]),
                            ('otherInfo', videoinfo["otherInfo"]),
                            ('jobid', videoinfo["jobid"]),
                            ('userid', self.puid),
                            ('isdrag', '3'),
                            ('enc', md5enc),
                            ('dtype', 'video'),
                            ('view', 'json'),
                        )
                        response = self.session.get('https://mooc1-api.chaoxing.com/multimedia/log/a/{}/{}'.format(re.search(r"cpi_(.*)", videoinfo["otherInfo"]).group(1),videoinfo2["dtoken"]), params=params)
                        if response.json()["isPassed"]:
                            break
                        time.sleep(55)
        except Exception as e:
            loger.error('', exc_info=True)
            loger.info(self.user_info["uname"] + "\t" + "刷课意外")
            return False

    def clear(self):
        self.session.close()
        self.session = requests.session()

def funShuake(user_info):
    JSON_INFO = utils.users_info_load(config.users_path)
    GLOBAL = JSON_INFO["GLOBAL"]
    shuake = Shuake(GLOBAL)
    if shuake.login(user_info):
        try:
            shuake.shuake()
        except Exception:
            loger.error('', exc_info=True)
    else:
        loger.info(users_info[user_uname]["ps"] + "\t" + "： 密码错误")
if __name__ == '__main__':
    loger.info("运行")
    try:
        JSON_INFO = utils.users_info_load(config.users_path)
        GLOBAL = JSON_INFO["GLOBAL"]
        users_info = JSON_INFO["users_info"]
        shuake = Shuake(GLOBAL)
        try:
            for user_uname in users_info:
                user_info = {
                    "uname": user_uname,
                }
                for key in users_info[user_uname]:
                    user_info[key] = users_info[user_uname][key]
                if shuake.login(user_info):
                    shuake.shuake()
                else:
                    loger.info(users_info[user_uname]["ps"] + "\t" + "： 密码错误")
        except Exception as e:
            loger.error('', exc_info=True)
        finally:
            utils.users_info_dump(config.users_path, JSON_INFO)
    except Exception:
        loger.error('', exc_info=True)
