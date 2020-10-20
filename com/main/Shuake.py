# -*- coding: utf-8 -*

import sys
import os

curPath = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.split(curPath)[0])
import config
from config import loger
from urllib.parse import urlencode
import urllib
import time
from utils import utils
import requests
import re
import traceback
import json
import hashlib
import math
import threading
from bs4 import BeautifulSoup
import random


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

    def init_jnodeList(self):
        """
        :return 以节id作为对课程列表的key
        """

        try:
            self.jnodeList = {}
            for courseid in self.clazzList:
                classid = self.clazzList[courseid]['clazzId']
                params = (
                    ('id', classid),
                    ('personid', self.puid),
                    ('fields',
                     'id,bbsid,classscore,isstart,allowdownload,chatid,name,state,isthirdaq,isfiled,information,discuss,visiblescore,begindate,coursesetting.fields(id,courseid,hiddencoursecover,hiddenwrongset),course.fields(id,name,infocontent,objectid,app,bulletformat,mappingcourseid,imageurl,knowledge.fields(id,name,indexOrder,parentnodeid,status,layer,label,begintime,endtime,attachment.fields(id,type,objectid,extension).type(video)))'),
                    ('view', 'json'),
                )

                response = self.session.get('https://mooc1-api.chaoxing.com/gas/clazz',params=params)
                course = response.json()["data"][0]["course"]["data"][0]
                jNodeList = course["knowledge"]["data"]

                for jNode in jNodeList:
                    #jname
                    self.jnodeList[jNode["id"]] = {"jname": jNode["name"], "coursename": course["name"],
                                                         "courseId": course["id"],"parentnodeid":1 if 'parentnodeid' not in course else course["parentnodeid"]}
                # print(self.jnodeList)
            return True
        except Exception as e:
            loger.error('', exc_info=True)
            loger.info(self.user_info["uname"] + "\t" + "获取课程列表失败")
            return False

    def init_clazzList(self):
        """
                :return 以course id作为对班列表的key
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
            # print(self.clazzList)
            return True
        except Exception as e:
            loger.error('', exc_info=True)
            loger.info(self.user_info["uname"] + "\t" + "获取班级列表失败")
            return False

    def init_PageList(self):
        # courseid为大课的id 每个大课又包含许多单元（也可以叫做节）
        # jnodeid为单元id（节id）
        # 返回本单元对应card列表 以cardid作为索引
        try:
            self.pageList = []
            for jnodeid in self.jnodeList:
                if self.jnodeList[jnodeid]['coursename'] == "四史学习":
                    params = (
                        ('page', '1'),
                        ('classifyId', jnodeid),
                        ('element', ''),
                        ('status', ''),
                        ('point', ''),
                        ('name', ''),
                    )
                    response = self.session.get(
                        'https://tsjy.chaoxing.com/plaza/course/{}/node-list'.format(self.jnodeList[jnodeid]["courseId"]),
                        params=params)
                    _PageList = response.json()
                    for page in _PageList["data"]["list"]:
                        _page = {"pageId": page['nodeId'], "jnodeid": page['classifyId'],
                                 'courseId': int(page['courseId']), 'classifyName': page['classifyName'],
                                 'name': page['name'], 'finishStatus': page['finishStatus'], 'read': page['read']}
                        self.pageList.append(_page)
                else:
                    if self.jnodeList[jnodeid]["parentnodeid"]==0:
                        continue
                    _page = {"pageId": jnodeid, "jnodeid": jnodeid,
                             'courseId': int(self.jnodeList[jnodeid]["courseId"]), 'classifyName': self.jnodeList[jnodeid]["coursename"],
                             'name': self.jnodeList[jnodeid]["jname"], 'finishStatus': None, 'read': None}
                    self.pageList.append(_page)
                    pass
            # print(self.pageList)
            return True
        except Exception as e:
            loger.error('', exc_info=True)
            loger.info(self.user_info["uname"] + "\t" + "获取视频列表失败")
            return False

    def get_cards_info(self, pageInfo,num):
        # video 为videoList的字典
        pageid = pageInfo["pageId"]
        courseid = pageInfo["courseId"]
        clazzid = self.clazzList[courseid]['clazzId']
        try:
            params = (
                ('clazzid', clazzid),
                ('courseid', courseid),
                ('knowledgeid', pageid),
                ('num', num),
                ('isPhone', '1'),
                ('control', 'true'),
            )
            response = self.session.get('https://mooc1-api.chaoxing.com/knowledge/cards', params=params).text
            cardsInfo = re.search(r"window.AttachmentSetting =(.*?);\n", response).group(1)
            cardsInfo = json.loads(cardsInfo)
            cardsInfoList = cardsInfo["attachments"]
            reportInfo = cardsInfo["defaults"]
            return cardsInfoList, reportInfo,True
        except:
            loger.info('', exc_info=True)
            loger.info(self.user_info["uname"] + "\t" + "获取视cards息失败")
            return None,None,False


    def get_scoreInfo(self, classId, courseId):
        try:
            params = (
                ('classId', classId),
                ('userId', self.puid),
            )
            response = self.session.get('https://tsjy.chaoxing.com/plaza/score/{}/day-score'.format(courseId),
                                        params=params)
            return response.json()["data"]["rule"]
        except Exception as e:
            loger.error('', exc_info=True)
            loger.info(self.user_info["uname"] + "\t" + "获取分数信息失败")
            return False

    def shuake(self):
        self.init_clazzList()
        self.init_jnodeList()
        self.init_PageList()
        try:
            for pageInfo in self.pageList:
                if self.clazzList[pageInfo['courseId']]['courseName'].find('学术规范') < 0:
                    continue
                for num in ["0","1"]:
                    cardsInfoList, reportInfo,success= self.get_cards_info(pageInfo,num)
                    if success==False:
                        continue
                    # print(cardsInfoList)
                    for cardInfo in cardsInfoList:
                        scoreInfo = {}
                        if self.clazzList[pageInfo['courseId']]['courseName'].find('四史学习')>=0 and scoreInfo["dayScore"] >= scoreInfo["dailyMaxScore"]:

                            scoreInfo = self.get_scoreInfo(self.clazzList[pageInfo['courseId']]['clazzId'],
                                                       pageInfo['courseId'])

                            print("\r",self.user_info["ps"], "今天已刷够", scoreInfo["dailyMaxScore"], "分")
                            break
                        else:

                            scoreInfo["dayScore"] = 100
                        if 'type' not in cardInfo:
                        #cardinfo 如果没有type信息 ，则此card为视频简介信息 不计分 跳过即可
                            continue
                        if cardInfo['type'] == "video":
                            if 'isPassed' in cardInfo and cardInfo['isPassed']:
                                continue
                            params = (
                                ('k', '123845'),
                                ('flag', 'normal'),
                                ('_dc', '1602816161570'),
                            )
                            cardInfo2 = self.session.get(
                                'https://mooc1-api.chaoxing.com/ananas/status/{}'.format(cardInfo["objectId"]),
                                params=params).json()
                            for i in range(math.ceil(cardInfo2['duration'] / 60)):
                                playingTime = i * 60 if i * 60 <= cardInfo2['duration'] else cardInfo2['duration']
                                print("\r{}\t当前：{}分\t正在刷课：".format(self.user_info["ps"],scoreInfo["dayScore"]), "playingTime:{}".format(playingTime),
                                      pageInfo["classifyName"],
                                      pageInfo["name"],cardInfo["property"]['name'], end="")
                                # [clazzId][userid][jobid][objectId][currentTimeSec * 1000][d_yHJ!$pdA~5][duration * 1000][clipTime]
                                enc = "[{}][{}][{}][{}][{}][d_yHJ!$pdA~5][{}][{}]".format(reportInfo["clazzId"],
                                                                                          self.puid, cardInfo["jobid"],
                                                                                          cardInfo["objectId"],
                                                                                          playingTime * 1000,
                                                                                          cardInfo2['duration'] * 1000,
                                                                                          '0_' + str(cardInfo2['duration']))
                                md5enc = hashlib.md5(enc.encode()).hexdigest()
                                params = (
                                    ('clazzId', reportInfo["clazzId"]),
                                    ('playingTime', playingTime),
                                    ('duration', cardInfo2['duration']),
                                    ('clipTime', '0_' + str(cardInfo2['duration'])),
                                    ('objectId', cardInfo["objectId"]),
                                    ('otherInfo', cardInfo["otherInfo"]),
                                    ('jobid', cardInfo["jobid"]),
                                    ('userid', self.puid),
                                    ('isdrag', '3'),
                                    ('enc', md5enc),
                                    ('dtype', 'video'),
                                    ('view', 'json'),
                                )
                                response = self.session.get(reportInfo["reportUrl"] + '/{}'.format(cardInfo2["dtoken"]),
                                                            params=params)
                                if response.json()["isPassed"]:
                                    pass
                                time.sleep(45)
                        if cardInfo['type'] == "read":
                            readtime = self.get_read_time(pageInfo, cardInfo, reportInfo)
                            if config.readTimelimit!=0 and readtime >config.readTimelimit:
                                continue
                            if config.readFrom0read and readtime>0:#从没开始过的章节开始阅读
                                continue
                            chapters,lastChapter = self.get_chapters_info(pageInfo, cardInfo, reportInfo)
                            if not config.readFromLastChapter:
                                lastChapter=0 #如果本句注释从上次记录的chapter开始阅读
                            for chapter in chapters[lastChapter:]:
                                print("\r{}\t当前：{}分\t正在阅读：".format(self.user_info["ps"],scoreInfo["dayScore"]),
                                      pageInfo["classifyName"],
                                      pageInfo["name"], cardInfo["property"]["title"], chapter["chaptername"], end="")
                                response = self.session.get(chapter["url"], ).text
                                params_info = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(chapter["url"]).query))
                                try:
                                    try:
                                        ponits = eval(re.search(r"points:'(.*?)'", response).group(1))
                                        total_points = len(ponits)
                                    except:
                                        total_points=1
                                    current_point = 1
                                    while (current_point <= total_points):
                                        current_point = random.randint(current_point, total_points)
                                        params = (
                                            ('courseId', pageInfo['courseId']),
                                            ('chapterId', chapter["id"][8:]),
                                            ('point', current_point),
                                            ('_from_', params_info['_from_']),
                                            ('rtag', params_info['rtag']),
                                        )
                                        response = self.session.get(
                                            'https://special.zhexuezj.cn/special/course/addUserPoint', params=params)
                                        resp = response.json()
                                        time.sleep(5)

                                except AttributeError:
                                    continue
        except:
            loger.error('', exc_info=True)
            loger.info(self.user_info["uname"] + "\t" + "刷课意外")
            return False

    def get_read_time(self, pageInfo, cardInfo, reportInfo):
        try:
            params = (
                ('courseid', pageInfo['courseId']),
                ('knowledgeid', reportInfo["knowledgeid"]),
                ('userid', 'null'),
                ('ut', 's'),
                ('clazzId', reportInfo["clazzId"]),
                ('jobid', cardInfo["jobid"]),
                ('isphone', 'true'),
                ('enc', cardInfo["enc"]),
                ('utenc', 'undefined'),
                ('cpi', reportInfo["cpi"]),
            )
            response = self.session.get('https://mooc1-api.chaoxing.com/coursedata/readjobv2/show', params=params)
            read_time = int(re.search(r"secondReadTime = \"(.*?)\"", response.text).group(1))
            return read_time
        except:
            loger.error('', exc_info=True)
            loger.info(self.user_info["uname"] + "\t" + "获取分数信息失败")
            return False

    def get_chapters_info(self, pageInfo, cardInfo, reportInfo):
        try:
            params = (
                ('classId', '33359344'),
                ('userId', '34876789'),
            )
            enc = self.session.get('https://tsjy.chaoxing.com/plaza/user/215091538/340728584/modify-node',
                                   params=params).json()["data"]["enc"]
            params = (
                ('_from_', '{}_{}_{}_{}'.format(pageInfo['courseId'], reportInfo['clazzId'], self.puid, enc.lower())),
                ('rtag', '{}_{}_{}'.format(pageInfo['pageId'], reportInfo["cpi"], cardInfo["jobid"])),
            )
            response = self.session.get(
                'https://special.zhexuezj.cn/mobile/mooc/tocourse/{}.html'.format(cardInfo["property"]["id"]),
                params=params, )
            soup = BeautifulSoup(response.text, "lxml")
            chapters_lxml = soup.find(attrs={"class": "topicList"})
            chapters_a = chapters_lxml.find_all(name="a")
            chapters = []
            lastChapter=0
            for i,chapter in enumerate(chapters_a):
                try:
                    chapter_dict = {}
                    chapter_dict["url"] = chapter["attr"]
                    chapter_dict["chaptername"] = chapter["chaptername"]
                    chapter_dict["id"] = chapter["id"]
                    if chapter["style"].find("color")>=0:
                        lastChapter=i
                    chapters.append(chapter_dict)
                except KeyError:
                    continue
            return chapters,lastChapter
        except:
            loger.info('', exc_info=True)
            loger.info(self.user_info["uname"] + "\t" + "获取chapter_info 失败"+"  可能是资源下线，不是程序错误")
            return [],0

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


class myThread(threading.Thread):
    def __init__(self, user_info):
        threading.Thread.__init__(self)
        self.user_info = user_info

    def run(self):
        funShuake(self.user_info)


if __name__ == '__main__':
    loger.info("运行")
    threadList = []
    try:
        JSON_INFO = utils.users_info_load(config.users_path)
        GLOBAL = JSON_INFO["GLOBAL"]
        users_info = JSON_INFO["users_info"]
        try:
            for user_uname in users_info:
                # mythread = myThread(users_info[user_uname])
                # mythread.start()
                # threadList.append(mythread)
                # time.sleep(5)
                if user_uname=="18925468581":
                    funShuake(users_info[user_uname])
            for thread in threadList:
                thread.join()
        except Exception as e:
            loger.error('', exc_info=True)
        finally:
            utils.users_info_dump(config.users_path, JSON_INFO)
    except Exception:
        loger.error('', exc_info=True)
