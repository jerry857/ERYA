import requests

cookies = {
    'source': '',
    'lv': '0',
    'fid': '72413',
    '_uid': '146189992',
    'uf': 'dff23984ef72c20b18cabecbad908e7fe60a78df359fd9a092ad21a96e5e67887aa90463a84b720809f0c711e7bee7ead110c105546a283d88b83130e7eb4704525546e91da79b5867cc3c653d1ee24541c08171f1b43ace593deeb040f66a7100a3d16a6714812b',
    '_d': '1603459471059',
    'UID': '146189992',
    'vc': 'F3D2FA21C9215BEFAAEED4D0C5787E1C',
    'vc2': 'C6DF003B49749D7608C6CED5BC595A06',
    'vc3': 'Q4ZyHZ0RiWAq412378oW9CnJxRhDE%2F39Q%2FPRZCampFP04zxuxXWPHedkb6dM%2FV8aIZEW3LKd2n70KMDKQvpCRIkS62XBt5ShFLFQGmWEPdjfafZ4h4MsEwodNcwBS3iv9oVLoytT0VZ3VLjQIvpnuex5E7Ej8Se5XI4KguLF2Cc%3Dfc29f2ef15014b52d41552716d5ab464',
    'xxtenc': 'b575917bdfa68c952e38d89388c10595',
    'DSSTASH_LOG': 'C_38-UN_238-US_146189992-T_1603459471061',
    'spaceFid': '72413',
    'tl': '1',
    'thirdRegist': '0',
    'k8s': 'f1c6b2a2cb34afa34deaf27d049fc883156ab36d',
    'jrose': '028DDC4C22DCA5E2DBDF120E0C176BA3.mooc-1096980007-16qzp',
    'route': 'ac9a7739314fa6817cbac7e56032374b',
}

headers = {
    'Host': 'mooc1-api.chaoxing.com',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'https://mooc1-api.chaoxing.com',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://mooc1-api.chaoxing.com/work/phone/doHomeWork?keyboardDisplayRequiresUserAction=1&courseId=214553024&workAnswerId=22263450&workId=10047810&knowledgeId=349156585&classId=31907027&oldWorkId=d1fb975d63f149f68d7a460ea9708ce2&jobId=work-d1fb975d63f149f68d7a460ea9708ce2&mooc=0&enc=4aca88c5cb8f0fb35ea279207d8e4da2&cpi=146096156',
    'Accept-Language': 'zh-CN,zh;q=0.9,zh-TW;q=0.8',
}

params = (
    ('keyboardDisplayRequiresUserAction', '1'),
    ('_classId', '31907027'),
    ('courseid', '214553024'),
    ('token', 'e37c5a424aa0c0aa085db2704878de39'),
    ('workAnswerId', '22263450'),
    ('ua', 'pc'),
    ('formType2', 'post'),
    ('saveStatus', '1'),
    # ('pos', '6c21c5f675c0f5c8b5532b020f6138'),
    # ('rd', '0.4345623597499877'),
    # ('value', '(1251|4388)'),
    # ('wid', '10047810'),
    # ('_edt', '1603534182223212'),
    # ('version', '1'),
)

data = 'pyFlag=&courseId=214553024&classId=31907027&api=1&mooc=0&workAnswerId=22263450&totalQuestionNum=cd8c29480d9c16f5a675e8c2c459245c&fullScore=100.0&knowledgeid=349156585&oldSchoolId=&oldWorkId=d1fb975d63f149f68d7a460ea9708ce2&jobid=work-d1fb975d63f149f68d7a460ea9708ce2&workRelationId=10047810&enc_work=e37c5a424aa0c0aa085db2704878de39&isphone=true&userId=146189992&answer400797952=A&answertype400797952=0&answer400797953=A&answertype400797953=0&answer400797954=true&answertype400797954=3&answerwqbid=400797952%2C400797953%2C400797954'

# response = requests.post('https://mooc1-api.chaoxing.com/work/addStudentWorkNew', headers=headers, params=params, cookies=cookies, data=data)
# print(response.json())




# cookies=cookies,

if __name__ == '__main__':
    import pickle
    import os
    from main.Shuake import *
    Spath = 'C:\\Users\\wangwen\\Desktop\\chaoxing_auto_Shuake\\com\\config/loginInfo\\18925468581'
    if os.path.exists(Spath):
        with open(Spath, "rb") as f:
            seria = pickle.load(f)
            session = seria["session"]
            puid = seria["puid"]
            session.timeOut = 20
            session.headers['Content-Type']= 'application/x-www-form-urlencoded; charset=UTF-8'
            # session.headers['Origin']='https://mooc1-api.chaoxing.com'
            # session.headers['Sec-Fetch-Site']= 'same-origin'
            # session.headers['Sec-Fetch-Mode']='cors'
            # session.headers['Sec-Fetch-Dest']='empty'
            # session.headers['Referer']='https://mooc1-api.chaoxing.com/work/phone/doHomeWork?keyboardDisplayRequiresUserAction=1&courseId=214553024&workAnswerId=22263450&workId=10047810&knowledgeId=349156585&classId=31907027&oldWorkId=d1fb975d63f149f68d7a460ea9708ce2&jobId=work-d1fb975d63f149f68d7a460ea9708ce2&mooc=0&enc=4aca88c5cb8f0fb35ea279207d8e4da2&cpi=146096156'
            # session.headers['Accept-Language']= 'zh-CN,zh;q=0.9,zh-TW;q=0.8'
            response=session.post('https://mooc1-api.chaoxing.com/work/addStudentWorkNew', params=params,
                   data=data)
            print(response.json())
            # print(session.headers)


    pass