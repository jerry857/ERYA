## 功能描述
- 登录方式：
- 支持:
  - 手机号码登录和学号登录
  - 支持多账号同时刷课（下图为用户数据结构）:
    * uname 为账号 code 为密码 其他信息为补充
  ![avatar](./userInfo.png)
  - 支持刷自定义课程（/com/main/Shuake.py）：
  ![avatar](./自定义刷课.png)

- 新增:
  - 阅读功能

- 待完善：
  - 答题功能

- 解释：
  - clazzid（代表班级）
  - couseid（代表课程）
  - jnodeid（代表节或者单元）
  - pageid（代表页，代表客户端刷课页面）
  - cardid（代表视频或者阅读的最小表示单元，也叫做knowlegedid，每个page中可能包含多个card）

