# -*- coding: utf-8 -*

import sys
import os
import pickle
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
import socket
socket.timeout=20
class Session(requests.Session):
    def __init__(self,timeOut=20):
        super(Session,self).__init__()
        self.timeOut=timeOut
    def get(self,*args,**kwargs):
        for i in range(10):
            try:
                return super(Session,self).get(*args,**kwargs,timeout=self.timeOut)
            except:
                if i<9:
                    time.sleep(5)
                else:raise

    def post(self,*args,**kwargs):
        for i in range(10):
            try:
                return super(Session,self).post(*args,**kwargs,timeout=self.timeOut)
            except:
                if i < 9:
                    time.sleep(5)
                else:
                    raise


class Shuake():
    def __init__(self):
        self.user_info = None
        self.session=None
        self.puid=None
        self.login_flag=False
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
            if not self.sessionload():
                self.session = Session(config.timeOut)
                # self.session.keep_alive = False
                self.session.headers = {
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 ChaoXingStudy/ChaoXingStudy_3_4.3.2_ios_phone_201911291130_27 (@Kalimdor)_2092948143612148043',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,en-US;q=0.8',
                    'X-Requested-With': 'com.chaoxing.mobile',
                }
                params = (
                    ('cx_xxt_passport', 'json'),
                )
                response = self.session.post('https://passport2-api.chaoxing.com/v11/loginregister', params=params,
                                             data=login_info)
                response = self.session.get('https://sso.chaoxing.com/apis/login/userLogin4Uname.do')
                resp = response.text.encode("utf-8", "ignore").decode("utf-8")
                self.puid = re.search(r"puid\":(.*?),", resp).group(1)
                self.login_flag=True
                self.sessionDump()
                return self.login_flag
            else:
                self.login_flag=True
                self.sessionDump()
                return self.login_flag
        except Exception as e:
            loger.error('', exc_info=True)
            loger.info(self.user_info["uname"] + "登陆失败")
            return self.login_flag

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
            return True
        except Exception as e:
            loger.error('', exc_info=True)
            loger.info(self.user_info["uname"] + "\t" + "获取班级列表失败")
            return False

    def init_knowledegList(self):
        """
        :return courseId作为对knowledge列表的key
        """
        try:
            self.knowlegeList = {}
            for courseid in self.clazzList:
                clazzId = self.clazzList[courseid]['clazzId']
                params = (
                    ('id', clazzId),
                    ('personid', self.puid),
                    ('fields',
                     'id,bbsid,classscore,isstart,allowdownload,chatid,information,discuss,name,state,isfiled,isthirdaq,visiblescore,begindate,course.fields(id,name,infocontent,objectid,app,mappingcourseid,coursesetting.fields(id,courseid,hiddencoursecover,hiddenwrongset),imageurl,bulletformat,knowledge.fields(id,lastmodifytime,createtime,begintime,name,indexOrder,parentnodeid,status,layer,label,card.fields(id,title),attachment.fields(id,objectid,type,extension).type(video)))'),
                    ('view', 'json'),
                )

                response = self.session.get('https://mooc1-api.chaoxing.com/gas/clazz', params=params)
                course = response.json()["data"][0]["course"]["data"][0]
                knowledegList = course["knowledge"]["data"]
                if course["id"] not in self.knowlegeList:
                    self.knowlegeList[course["id"]] = []
                jDict = {}

                def knowledeg_sort(knowlege):
                    labels=knowlege["label"]
                    labels=labels.split(".")
                    label=labels[0]
                    ff=""
                    for f in labels[0:]:
                        ff+=f
                    label+="."
                    label+=ff
                    return float(label)

                for knowlege in knowledegList:
                    jDict[knowlege["id"]] = knowlege
                for knowlege in knowledegList:
                    if knowlege["parentnodeid"] == 0: continue  # 章标题
                    if knowlege["parentnodeid"] not in jDict:continue#问题节点
                    parentnodeid = knowlege["parentnodeid"]
                    # indexorder = knowlege["indexorder"]
                    # k = 2
                    while (True):
                        if jDict[parentnodeid]["parentnodeid"] == 0:
                            break
                        else:
                            parentnodeid = jDict[parentnodeid]["parentnodeid"]

                    self.knowlegeList[course["id"]].append(
                        {"knowlegeName": knowlege["name"], "courseName": course["name"], "knowledgeId": knowlege["id"],
                         "courseId": course["id"], "clazzId": clazzId, "parentnodeid": parentnodeid,
                         # 章id
                         "parentnodeNmae": jDict[parentnodeid]["name"],
                         "label": knowlege["label"],
                         "card": knowlege["card"]["data"],
                         "status": knowlege["status"]})
                self.knowlegeList[course["id"]].sort(key=knowledeg_sort)
                # print(self.knowlegeList)
            return True
        except Exception as e:
            loger.error('', exc_info=True)
            loger.info(self.user_info["uname"] + "\t" + "获取课程列表失败")
            return False

    def knowledgeStart(self, knowledegList):
        knowledge = knowledegList[0]
        nodes = str(knowledge["knowledgeId"])
        for node in knowledegList:
            nodes += "," + str(node["knowledgeId"])
        data = {
            'clazzid': knowledge["clazzId"],
            'userid': self.puid,
            'view': 'json',
            'nodes': nodes,
            'courseid': knowledge["courseId"]
        }
        response = self.session.post('https://mooc1-api.chaoxing.com/job/myjobsnodesmap', data=data).json()
        start = None
        for i, knowledge in enumerate(knowledegList):
            knowledgeId = str(knowledge["knowledgeId"])
            if response[knowledgeId]["unfinishcount"] > 0:
                start = i
                break
        return start

    def get_cards_info(self, knowledge, num):
        # video 为videoList的字典
        clazzid = knowledge['clazzId']
        try:
            params = (
                ('clazzid', clazzid),
                ('courseid', knowledge["courseId"]),
                ('knowledgeid', knowledge["knowledgeId"]),
                ('num', num),
                ('isPhone', '1'),
                ('control', 'true'),
            )
            response = self.session.get('https://mooc1-api.chaoxing.com/knowledge/cards', params=params).text
            cardsInfo = re.search(r"window.AttachmentSetting =(.*?);\n", response).group(1)
            cardsInfo = json.loads(cardsInfo)
            cardsInfoList = cardsInfo["attachments"]
            reportInfo = cardsInfo["defaults"]
            return cardsInfoList, reportInfo, True
        except:
            loger.info('', exc_info=True)
            loger.info(self.user_info["uname"] + "\t" + "获取视cards息失败")
            return None, None, False

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
    def submit_study(self,knowledge):#提交任务点，模拟点击章标题
        params = (
            ('node', knowledge["knowledgeId"]),
            ('userid', self.puid),
            ('clazzid', knowledge["clazzId"]),
            ('courseid', knowledge["courseId"]),
            ('view', 'json'),
        )
        response = self.session.get('https://mooc1-api.chaoxing.com/job/submitstudy', params=params)
    def shuake(self):
        self.init_clazzList()
        self.init_knowledegList()
        try:
            for courseId in self.knowlegeList:
                flag = 0
                if "courseName" in self.user_info:
                    for course in self.user_info['courseName']:
                        if self.clazzList[courseId]['courseName'].find(course) >= 0:
                            flag = 1
                            break
                if flag != 1:
                    continue
                start = self.knowledgeStart(self.knowlegeList[courseId])
                if start is None: continue# 本课已刷完
                for knowledge in self.knowlegeList[courseId][start:]:
                    scoreInfo = {}
                    if knowledge["courseName"].find('四史学习') >= 0:
                        scoreInfo = self.get_scoreInfo(self.clazzList[knowledge['courseId']]['clazzId'],
                                                       knowledge['courseId'])
                        if scoreInfo["dayScore"] >= scoreInfo["dailyMaxScore"]:
                            print("\r", self.user_info["ps"], "今天已刷够", scoreInfo["dailyMaxScore"], "分")
                            break
                    else:
                        scoreInfo["dayScore"] = 100
                    self.submit_study(knowledge)
                    for num in range(len(knowledge["card"])):
                        cardsInfoList, reportInfo, success = self.get_cards_info(knowledge, num)
                        if success == False:
                            return
                        # print(cardsInfoList)
                        for cardInfo in cardsInfoList:
                            if "job" not in cardInfo or ("job" in cardInfo and cardInfo["job"]):
                                if 'type' not in cardInfo:
                                    continue  # cardinfo 如果没有type信息 ，则此card为视频简介信息 不计分 跳过即可
                                elif cardInfo['type'] == "video":
                                    self.watch_video(cardInfo, reportInfo, knowledge, scoreInfo)
                                elif cardInfo['type'] == "read":
                                    self.read_book(cardInfo, reportInfo, knowledge, scoreInfo)
                                elif cardInfo['type'] == "workid":
                                    self.dati(cardInfo, reportInfo, knowledge)
        except:
            loger.error('', exc_info=True)
            loger.info(self.user_info["uname"] + "\t" + "刷课意外")
            return False

    def watch_video(self, cardInfo, reportInfo, knowledge, scoreInfo):
        if 'isPassed' in cardInfo and cardInfo['isPassed']:
            return
        params = (
            ('k', '123845'),
            ('flag', 'normal'),
            ('_dc', '1602816161570'),
        )
        cardInfo2 = self.session.get(
            'https://mooc1-api.chaoxing.com/ananas/status/{}'.format(cardInfo["objectId"]),
            params=params).json()
        for i in range(math.ceil(cardInfo2['duration'] / 60)+1):
            if i * 60 <= cardInfo2['duration']:#3个if为了让视频看完
                playingTime = i * 60
            elif (i-1) * 60 <= cardInfo2['duration']:
                playingTime=cardInfo2['duration']-30
            else:
                playingTime = cardInfo2['duration']
            print("\r{}\t当前：{}分\t正在刷课：".format(self.user_info["ps"], scoreInfo["dayScore"]),
                  "playingTime:{}".format(playingTime),
                  knowledge["courseName"],
                  knowledge["parentnodeNmae"],"label："+knowledge["label"],
                  knowledge["knowlegeName"], cardInfo["property"]['name'], end="")
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
                continue
            time.sleep(60/self.user_info["speed"])

    def dati(self, cardInfo, reportInfo, knowledge):
        print("\r{}\t正在答题：".format(self.user_info["ps"],),
              knowledge["courseName"],
              knowledge["parentnodeNmae"],"label："+knowledge["label"],
              knowledge["knowlegeName"], cardInfo["property"]['title'], end="")
        def answer(question):
            try:
                url2 = "http://api.gochati.cn/jsapi.php?token=test123&q=" + question
                url2 = url2.replace("（    ）", "（）")
                url2 = url2.replace("（   ）", "（）")
                url2 = url2.replace("（  ）", "（）")
                url2 = url2.replace("（ ）", "（）")
                response = self.session.get(url2).json()
                ans=response["da"]
                if ans !="":
                    ans = ans.replace("\n\n", "\n \n")
                    ans = ans.replace("#", "\n \n")  # '资本主义道路#民主社会主义道路'
                    ans = ans.replace("\u0001", "\n \n")  # '资本主义道路#民主社会主义道路'
                    ans = ans.replace(" --- ", "\n \n")
                    ans = ans.replace("===", "\n \n")#'以宗法、家庭伦理为最高的考量===宗法伦理被视为法的一个渊源===伦理和法律之间没有明确的界限'
                    ans = ans.split("\n \n")
                    while(''in ans):
                        ans.remove('')
                    return ans
            except:
                loger.info(url2 + "出错")
            try:
                url = "http://c.ykhulian.com/chati/0/" + question
                response = self.session.get(url).json()
                if response["success"] == 200 and response["question"].find("维护") < 0:
                    ans = response["answer"].replace("\n\n", "\n \n")
                    ans = ans.replace("#", "\n \n")  # '资本主义道路#民主社会主义道路'
                    ans = ans.replace("\u0001", "\n \n")  # '资本主义道路#民主社会主义道路'
                    ans = ans.replace(" --- ", "\n \n")  # '资本主义道路#民主社会主义道路''效度 --- 信度'
                    ans = ans.replace("===", "\n \n")  # '资本主义道路#民主社会主义道路''效度 --- 信度'
                    ans = ans.split("\n \n")
                    while ('' in ans):
                        ans.remove('')
                    return ans
                return None
            except:
                loger.error('题目：'+question, exc_info=True)
                loger.error('搜索答案出错', exc_info=True)
                return None


        try:
            params = (
                ('workId', cardInfo["property"]["workid"]),
                ('courseId', knowledge["courseId"]),
                ('clazzId', knowledge["clazzId"]),
                ('knowledgeId', knowledge["knowledgeId"]),
                ('jobId', cardInfo["jobid"]),
                ('enc', cardInfo["enc"]),
                ('cpi', reportInfo['cpi']),
            )
            response = self.session.get('https://mooc1-api.chaoxing.com/work/phone/work', params=params)
            paramsurl = response.url
            params_info = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(paramsurl).query))
            soup = BeautifulSoup(response.text, "lxml")
            titleList = soup.find_all(name="title")
            for title in titleList:
                if title.text.find("已批阅")>=0:
                    return
            else:
                form = soup.find(attrs={"id": "form1"})
                def get_method(form):
                    try:
                        return form["method"]
                    except:
                        return "post2"
                params = (
                    ('keyboardDisplayRequiresUserAction', 1),
                    ('_classId', knowledge["clazzId"]),
                    ('courseid', params_info["courseId"]),
                    ('token', form.find(attrs={"id":"enc_work"})["value"]),
                    # ('workAnswerId', params_info["workAnswerId"]),
                    ('totalQuestionNum', form.find(attrs={"id":"totalQuestionNum"})["value"]),
                    ('ua', 'app'),
                    ('formType2', get_method(form)),
                    ('saveStatus', '1'),
                    # ('pos', ''),
                    ('version', '1'),
                )
                data = {'pyFlag': '',
                        'courseId': form.find(attrs={"id":"courseId"})["value"],
                        'classId': form.find(attrs={"id":"classId"})["value"],
                        'api': form.find(attrs={"id":"api"})["value"],
                        'mooc': form.find(attrs={"id":"mooc"})["value"],
                        'workAnswerId': form.find(attrs={"id":"workAnswerId"})["value"],
                        'totalQuestionNum': form.find(attrs={"id":"totalQuestionNum"})["value"],
                        'fullScore': form.find(attrs={"id":"fullScore"})["value"],
                        'knowledgeid': form.find(attrs={"id":"knowledgeid"})["value"],
                        'oldSchoolId': form.find(attrs={"id":"oldSchoolId"})["value"],
                        'oldWorkId': form.find(attrs={"id":"oldWorkId"})["value"],
                        'jobid': form.find(attrs={"id":"jobid"})["value"],
                        'workRelationId': form.find(attrs={"id":"workRelationId"})["value"],
                        'enc_work': form.find(attrs={"id":"enc_work"})["value"],
                        'isphone': 'true',
                        'userId': self.puid
                        }
                questionList=form.find_all(attrs={"class":"Py-mian1"})
                answerwqbid=""
                for question in questionList:
                    questionName=question.find(attrs={"class":"Py-m1-title fs16"}).text.split("\n")[2].lstrip()
                    questionAnswer=answer(questionName)
                    assert questionAnswer is not None
                    submits = question.find_all("input")
                    for submit in submits:
                        if submit["id"].find("type")<0:
                            flag = 0
                            data[submit["id"].replace("answers","answer")] = ""
                            if question.find(attrs={"class":"quesType"}).text=='[单选题]':
                                formAnswers=question.find_all("li")
                                answerwqbid+=formAnswers[0]["id-param"]
                                answerwqbid += ","
                                for formAns in formAnswers:
                                    if formAns.text.find(questionAnswer[0])>=0: #or questionAnswer[0].find(re.search(r"\n\n(.*?)\n\n",formAns.text).group(1))>=0:
                                        data[submit["id"]]=formAns.text.split("\n")[1]
                                        flag=1
                                        break
                            elif question.find(attrs={"class":"quesType"}).text=='[多选题]':
                                formAnswers = question.find_all("li")
                                if questionName.find("以下说法正确的")>=0 and questionName.find("以下说法正确的")<=5:
                                    questionAnswer = answer(formAnswers[0].text.split("\n")[3])
                                answerwqbid+=formAnswers[0]["id-param"]
                                answerwqbid += ","
                                assert len(questionAnswer) > 1
                                dataAns=[]
                                for quesAns in questionAnswer:
                                    flag = 0
                                    for formAns in formAnswers:
                                        if formAns.text.find(quesAns) >= 0: #or quesAns.find(re.search(r"\n\n(.*?)\n\n",formAns.text).group(1))>=0:
                                            dataAns.append(formAns.text.split("\n")[1])
                                            flag = 1
                                            break
                                dataAns.sort()
                                for dataAn in dataAns:
                                    data[submit["id"].replace("answers","answer")] += dataAn
                            elif question.find(attrs={"class":"quesType"}).text=="[判断题]":
                                formAnswers = question.find_all("li")
                                answerwqbid+=formAnswers[0]["id-param"]
                                answerwqbid += ","
                                if questionAnswer[0].find("对")>=0 or questionAnswer[0].find("正确")>=0 or questionAnswer[0].find("√")>=0 or questionAnswer[0].find("是")>=0:
                                    data[submit["id"]] = "true"
                                    flag=1
                                else:
                                    data[submit["id"]] = "false"
                                    flag = 1
                            else:
                                raise Exception("题型："+question.find(attrs={"class":"quesType"}).text+"  需补充")
                            assert flag == 1  # 若发生异常  答案没找到
                        else:data[submit["id"]]=submit["value"]
                data["answerwqbid"]=answerwqbid

                self.session.headers['Content-Type']='application/x-www-form-urlencoded; charset=UTF-8'
                response = self.session.post('https://mooc1-api.chaoxing.com/work/addStudentWorkNew', params=params,
                                         data=urlencode(data),allow_redirects=False)
                del self.session.headers['Content-Type']
                assert response.json()["msg"]=='success!'
        except:
            loger.error(knowledge["courseName"]+"\t"+knowledge["parentnodeNmae"]+"\t"+knowledge["knowlegeName"]+"\t"+cardInfo["property"]['title'])
            loger.error('答题出错',exc_info=True)
            # raise

    def read_book(self, cardInfo, reportInfo, knowledge, scoreInfo):
        readtime = self.get_read_time(knowledge, cardInfo, reportInfo)
        if readtime is not None:
            if  config.readTimelimit != 0 and readtime > config.readTimelimit:
                return
            if   config.readFrom0read and readtime > 0:  # 从没开始过的章节开始阅读
                return
        if "jobid" not in cardInfo:
            jobid=cardInfo["property"]["_jobid"]
        else:
            jobid=cardInfo["jobid"]
        params = (
            ('jobid', jobid),
            ('knowledgeid', knowledge["knowledgeId"]),
            ('courseid', knowledge["courseId"]),
            ('clazzid', knowledge["clazzId"]),
            ('jtoken', cardInfo["jtoken"]),
            ('_dc', int(time.time()*1000)),
        )

        response = self.session.get('https://mooc1-api.chaoxing.com/ananas/job/readv2', params=params,)#添加考核点
        chapters, lastChapter = self.get_chapters_info(knowledge, cardInfo, reportInfo)
        if not config.readFromLastChapter:
            lastChapter = 0  # 从第一章开始读chapter开始阅读
        for chapter in chapters[lastChapter:]:
            print("\r{}\t当前：{}分\t正在阅读：".format(self.user_info["ps"], scoreInfo["dayScore"]),
                  knowledge["courseName"],
                  knowledge["parentnodeNmae"],"label："+knowledge["label"],
                  knowledge["knowlegeName"], cardInfo["property"]["title"], chapter["chaptername"], end="")
            response = self.session.get(chapter["url"], ).text
            params_info = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(chapter["url"]).query))
            try:
                try:
                    ponits = eval(re.search(r"points:'(.*?)'", response).group(1))
                    total_points = len(ponits)
                except:
                    total_points = 1
                current_point = 1
                starttime=time.time()
                while (current_point < total_points):
                    current_point = random.randint(current_point, total_points)
                    params = (
                        ('courseId', knowledge['courseId']),
                        ('chapterId', chapter["id"][8:]),
                        ('point', current_point),
                        ('_from_', params_info['_from_']),
                        ('rtag', params_info['rtag']),
                    )
                    response = self.session.get(
                        'https://special.zhexuezj.cn/special/course/addUserPoint', params=params)
                    resp = response.json()
                    time.sleep(5)
                    readtime = self.get_read_time(knowledge, cardInfo, reportInfo)
                    if readtime is not None:
                        if config.readTimelimit != 0 and readtime > config.readTimelimit:
                            return
                    if (time.time()-starttime)>=(config.readTimelimit*2):
                        return

            except AttributeError:
                continue

    def get_read_time(self, knowledge, cardInfo, reportInfo):
        try:
            params = (
                ('courseid', knowledge['courseId']),
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
            loger.info('', exc_info=True)
            loger.info(self.user_info["uname"] + "\t" + "获取分数信息失败")#正常的课没有阅读时长统计
            return None

    def get_chapters_info(self, knowledge, cardInfo, reportInfo):
        try:
            params = (
                ('classId', '33359344'),
                ('userId', '34876789'),
            )
            enc = self.session.get('https://tsjy.chaoxing.com/plaza/user/215091538/340728584/modify-node',
                                   params=params).json()["data"]["enc"]
            params = (
                ('_from_', '{}_{}_{}_{}'.format(knowledge['courseId'], reportInfo['clazzId'], self.puid, enc.lower())),
                ('rtag', '{}_{}_{}'.format(knowledge['knowledgeId'], reportInfo["cpi"], cardInfo["jobid"])),
            )
            response = self.session.get(
                'https://special.zhexuezj.cn/mobile/mooc/tocourse/{}.html'.format(cardInfo["property"]["id"]),
                params=params, )
            soup = BeautifulSoup(response.text, "lxml")
            chapters_lxml = soup.find(attrs={"class": "topicList"})
            chapters_a = chapters_lxml.find_all(name="a")
            chapters = []
            lastChapter = 0
            for i, chapter in enumerate(chapters_a):
                try:
                    chapter_dict = {}
                    chapter_dict["url"] = chapter["attr"]
                    chapter_dict["chaptername"] = chapter["chaptername"]
                    chapter_dict["id"] = chapter["id"]
                    if chapter["style"].find("color") >= 0:
                        lastChapter = i
                    chapters.append(chapter_dict)
                except KeyError:
                    continue
            return chapters, lastChapter
        except:
            loger.info('', exc_info=True)
            loger.info(self.user_info["uname"] + "\t" + "获取chapter_info 失败" + "  可能是资源下线，不是程序错误")
            return [], 0

    def clear(self):
        self.session.close()
        self.session = Session(20)
    def sessionDump(self):
        if self.login_flag:
            Spath = os.path.join(config.loginInfo_path, self.user_info["uname"])
            with open(Spath,"wb") as f:
                session_Info = {"session": self.session, "puid": self.puid}
                pickle.dump(session_Info, f)
    def sessionload(self):
        Spath=os.path.join(config.loginInfo_path,self.user_info["uname"])
        if os.path.exists(Spath):
            try:
                with open(Spath,"rb") as f:
                    seria=pickle.load(f)
                    self.session=seria["session"]
                    self.puid=seria["puid"]
                    self.session.timeOut=config.timeOut
                    resp=self.session.get('https://mooc1-1.chaoxing.com/work/validate')
                    if resp.text.find("请重新登录")>=0:
                        print("\r",self.user_info["ps"], "正在重新登录")
                        time.sleep(2)
                        return False
                    params = (
                        ('view', 'json'),
                        ('rss', '1'),
                    )
                    resp = self.session.get('http://mooc1-api.chaoxing.com/mycourse/backclazzdata', params=params)
                    if resp.text.find("验证码")>=0:
                        print("\r",self.user_info["ps"], "正在重新登录")
                        time.sleep(2)
                        return False
                    print("\r",self.user_info["ps"],"加载Session成功")
                    return False
            except:
                print("\r",self.user_info["ps"], "正在重新登录")
                time.sleep(2)
                return False
        else:
            print("\r",self.user_info["ps"], "正在重新登录")
            time.sleep(2)
            return False
    def __del__(self):
        self.sessionDump()
        print("\r",self.user_info["ps"],"登录信息已保存")

def funShuake(user_info):
    JSON_INFO = utils.users_info_load(config.users_path)
    GLOBAL = JSON_INFO["GLOBAL"]
    for glo in GLOBAL:
        if glo not in user_info:
            user_info[glo]=GLOBAL[glo]
    shuake = Shuake()
    if shuake.login(user_info):
        try:
            # pass
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
    JSON_INFO = utils.users_info_load(config.users_path)
    GLOBAL = JSON_INFO["GLOBAL"]  ######
    users_info = JSON_INFO["users_info"]
    try:
        for user_uname in users_info:
            #if user_uname == "18110329539":
                 #continue
            mythread = myThread(users_info[user_uname])
            mythread.start()
            threadList.append(mythread)
            time.sleep(5)
            #if user_uname == "18110329539":
                #funShuake(users_info[user_uname])
        for thread in threadList:
            thread.join()
    except Exception as e:
        loger.error('', exc_info=True)

