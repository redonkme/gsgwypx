import requests
from bs4 import BeautifulSoup
# import se
from lxpy import copy_headers_dict 
import time
import execjs
# import random
def getSrand():
    sRand=""
    url="http://www.gsgwypx.com.cn/user/toLogin/1.shtml"
    r1=requests.get(url).content
    rs = BeautifulSoup(r1,"html.parser")
    sRand=(rs.find('input',attrs={'id':'sRandNum'})['value'])
    return sRand
def getcookie(headers,userName,passwd):
    srand=getSrand()
    cookies=[]
    # headerstr = '''
    # User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36
    # Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
    # Referer: http://www.gsgwypx.com.cn/index/index/2.shtml
    # Accept-Encoding: gzip, deflate
    # Accept-Language: zh-CN,zh;q=0.9
    # Cookie: isLogin=; fc9720fe-c42a-4952-bc58-3114a5748aed=""; 
    # ''' 
    url="http://www.gsgwypx.com.cn/user/toUserLogin.do"
    userNameTemp=userName
    passWordTemp=passwd
    key='skda'
    js = open("des.js",encoding="utf-8").read()
    ctx=execjs.compile(js)
    username=ctx.call("strEnc",userNameTemp,key,key,key)
    password=ctx.call("strEnc",passWordTemp,key,key,key)
    date={"userNameTemp":userNameTemp,"passWordTemp":passWordTemp,\
        "randNum":srand,"sRandNum":srand,\
            "userName":username,\
                "passWord":password,"loginFrom":"index"}
    
    # print(date)
    rs = requests.post(url=url,data=date,headers=headers,allow_redirects=False)
    if(rs.status_code==302):
        print("登录成功")
    else:
        print("用户名或密码错误！")
        quit()
        
    # if ("set-cookie" in rs.headers):
    #     simpleCookies = SimpleCookie(rs.headers["Set-Cookie"])
        
    #     print(f'simpleCookie is {simpleCookies}')
    # print(rs.headers)
    # print(rs.cookies.items())
    # print(rs.text)
    for k,v in rs.cookies.items():
        s=k+'='+v
        # print(s)
        cookies.append(s)
    # for i in cookies:
    #     print(i)
    return cookies
def getUserId(headers):
    url="http://www.gsgwypx.com.cn/user/userInfo.do?flag=person"
    rs=requests.post(url,headers=headers).content
    bs=BeautifulSoup(rs,'html.parser')
    # print(bs)
    userId=bs.find('input',attrs={'id':"userId"})['value']
    return userId
def getLessons(url,head,gradeIdvalue,userId,totalPage):   #获取所有课程
    print("正在获取课程列表……")
    lessonLists=[]
    gcState=1
    pageSize=5
    '''gradeId=11&userId=261812&gcState=1&currentPage=2&totalPage=18&pageSize=5'''
    tmplistcoursId=[]
    tmplistVideoId=[]
    tmplistcoursName=[]
    kcdurations=[]
    for currentpage in range(1,totalPage+1):
        currentPage = currentpage    
        data={"gradeId":gradeIdvalue,"userId":userId,"gcState":gcState,\
          "currentPage":currentPage,"totalPage":totalPage,"pageSize":pageSize}    
        rs=requests.post(url=url,headers=head,data=data).content
        bs = BeautifulSoup(rs,'html.parser')
        # print(bs)
        for kc in bs.find_all('dd',class_='main_r_dd2'):
            tmpLessonList = (kc.find('a', class_="zuo_min").get('href'))[22:-2].split(',')

            for i in range(0,len(tmpLessonList)):
                tmp=tmpLessonList[i].strip("'")
                if(i==0):
                    tmplistcoursId.append(tmp)
                if(i==1):
                    tmplistVideoId.append(tmp)
                if(i==3):
                    tmplistcoursName.append(tmp)
                    #----------
        # for kc in bs.find_all('b',class_="cheng"):  
        #  
            kcshichang=(kc.find('b',class_="cheng"))
            if kcshichang is not None:
                tmpshichang=kcshichang.text.split(':')
                # kcduration.append(kcshichang)
                # tmpshichang=kc.text.split(':')
                kcduration=int(tmpshichang[0])*3600+int(tmpshichang[1])*60+int(tmpshichang[2])
                kcdurations.append(kcduration)
            else:
                print("课程时长获取为空")
            #--------
        
            lessonLists=[tmplistcoursId,tmplistVideoId,tmplistcoursName,kcdurations]      
    return lessonLists
def getUncompleteLesson(head,lessonLists,gradeId,userId):  #获得未完成的课程列表
    print("正在获取未学习完成的课程列表……")
    '''
    示例url:
    http://www.gsgwypx.com.cn/gradeCourse/getCourseUsersJindu.do?gradeId=11&userId=261812&courseId=1012&gcState=1
    ["'1001'"（课程Id）, "'GS1653284077.mp4'"（视频Id）, "'171'", "'碳中和目标下的能源和经济转型研究（上）'"]
    '''
    uncompleteLesson=[] #存放了所有的未播放完成的课程
    uncompleteLessonId=[]
    uncompleteVedioId=[]
    uncompleteLessonName=[]
    uncompletkcdurations=[]
    for lessonsId in lessonLists[0]:

        # lesslsttmp=lessons.removeprefix("javascript:BeginStudy(").removesuffix(');').split(',') 
        courseId=lessonsId
        # courseId=courseId.removeprefix("'").removesuffix("'")
        posturl="http://www.gsgwypx.com.cn/gradeCourse/getCourseUsersJindu.do?gradeId=%s&userId=%s&courseId=%s&gcState=1 "\
              %(gradeId,userId,courseId)
        # print(posturl)
        kcjd=requests.post(url=posturl,headers=head).text
        # print(kcjd)
        if (str(kcjd)!='100%'):
            # print(kcjd)
            #获取当前课程ID的索引，并将视频ID：lessonLists[1]，课程名称lessonLists[2]在相应的索引位置取出来，形成一个新的列表。
            #获取索引：
            uncompleteLessonId.append(lessonsId)
            indx=lessonLists[0].index(courseId)
            uncompleteVedioId.append(lessonLists[1][indx])
            uncompleteLessonName.append(lessonLists[2][indx])
            uncompletkcdurations.append(lessonLists[3][indx])
            #需要重新写未完成播放课程列表函数逻辑2023-08-07
    uncompleteLesson=[uncompleteLessonId,uncompleteVedioId,uncompleteLessonName,uncompletkcdurations]
    return uncompleteLesson

def getjd(head,gradeId,userId,courseId):
    posturl="http://www.gsgwypx.com.cn/gradeCourse/getCourseUsersJindu.do?gradeId=%s&userId=%s&courseId=%s&gcState=1 "\
              %(gradeId,userId,courseId)
    # print(posturl)
    try:
        kcjd=requests.post(url=posturl,headers=head).text
    # print("当前学习的课程为%s,学习进度为%s"%(courseId,kcjd))
    except requests.exceptions.ConnectTimeout as e:
        print("获取课程进度超时！")
        kcjd="*"
    return kcjd

def learn(head,gradeId,userId,uncompleteLessList):    #学习课程
    '''
    用POST方法向该链接：http://www.gsgwypx.com.cn:84/gansu-spcrm/rest/AddCourse
    发送如下字段：
    CourseId=941
    &UserId=261812
    &SessionId=BE166CB97BF98633FC82423A179B69389B71687B8D9157D3534476CFFE76C9EB8BA94131D66325F36AEC7E74D0DFF3ACC8D692FE2B7CA054F74D87A1DCB679619453C3512F08FBB5
    &GreadId=11
    &Location=2728
    &Sessiontime=
    00%3A00%3A10
    &ScormOrVideo=171&Systime=1691301773339
    &CourseCode=GS1653284018.mp4
    &Duration=3398
    nums 同时学习的课程数量
    '''

    for unLesson in uncompleteLessList:
        '''
        unLesson=["'977'", "'GS1653284054.mp4'", "'171'", "'在新时代西部大开发上闯新路'"]
        '''
        posturl="http://www.gsgwypx.com.cn:84/gansu-spcrm/rest/AddCourse"

        coursId=unLesson[0]
        uncompletcoursIds=[]

        # coursId=coursId.removeprefix("'").removesuffix("'")
        CourseCode=unLesson[1]
        # CourseCode=CourseCode.removeprefix("'").removesuffix("'")
        for m in range(0,3000,30):
            for i in range(1,10):
                location=m+i
                postdata={"CourseId":coursId,
                        "UserId":userId,
                        "SessionId":"BE166CB97BF98633FC82423A179B69389B71687B8D9157D3534476CFFE76C9EB8BA94131D66325F36AEC7E74D0DFF3ACC8D692FE2B7CA054F74D87A1DCB679619453C3512F08FBB5",
                        "GreadId":gradeId,
                        "Location":str(location),
                        "Sessiontime":"00%3A00%3A10",
                        "ScormOrVideo":"171","Systime":"1691301773339",
                        "CourseCode":CourseCode,
                        "Duration":"3398"}
                requests.post(url=posturl,headers=head,data=postdata)
                time.sleep(5)
            jd=getjd(head,gradeId,userId,coursId)
            if(jd=='100%'):
                break

        print(unLesson)

def learnQuick(head,gradeId,userId,uncompleteLessons,nums):
    if (len(uncompleteLessons)==0):
        print("课程列表获取失败")
        "head,gradeId,userId,uncompleteLessList,nums"
    else:
        if (len(uncompleteLessons[0])<nums):
            studyList=uncompleteLessons
            unstudyList=[]
        else:
            studyList = [uncompleteLessons[0][:nums],uncompleteLessons[1][:nums],uncompleteLessons[2][:nums],uncompleteLessons[3][:nums]]
            unstudyList=[uncompleteLessons[0][nums:],uncompleteLessons[1][nums:],uncompleteLessons[2][nums:],uncompleteLessons[3][nums:]]
        while(len(studyList[0])!=0):
            for loca in range(1,3890):
                time.sleep(10/nums)
                for i in studyList[0]:
                    # loca=loca+loca*loca

                    coursId =i
                    CourseCode=studyList[1][studyList[0].index(coursId)]
                    Duration=studyList[3][studyList[0].index(coursId)]
                    postdata={"CourseId":coursId,
                                    "UserId":userId,
                                    "SessionId":"BE166CB97BF98633FC82423A179B69389B71687B8D9157D3534476CFFE76C9EB8BA94131D66325F36AEC7E74D0DFF3ACC8D692FE2B7CA054F74D87A1DCB679619453C3512F08FBB5",
                                    "GreadId":gradeId,
                                    "Location":loca,
                                    "Sessiontime":"00:00:2",
                                    "ScormOrVideo":"171","Systime":"1691301773339",
                                    "CourseCode":CourseCode,
                                    "Duration":Duration}
                    CourseName = studyList[2][studyList[0].index(coursId)]
                    kcjd = getjd(head,gradeId,userId,coursId)
                    if(kcjd=='100%'):
                        print(kcjd)
                        print("%s的课程已经学完"%coursId)
                        index = studyList[0].index(coursId)
                        (studyList[0]).remove(coursId)
                        (studyList[1]).pop(index)
                        studyList[2].pop(index)
                        studyList[3].pop(index)
                        if(len(unstudyList)!=0):
                            studyList[0].append(unstudyList[0][0])
                            unstudyList[0].pop(0)
                            studyList[1].append(unstudyList[1][0])
                            unstudyList[1].pop(0)
                            studyList[2].append(unstudyList[2][0])
                            unstudyList[2].pop(0)
                            studyList[3].append(unstudyList[3][0])
                            unstudyList[3].pop(0)
                        continue
                    else:
                        posturl="http://www.gsgwypx.com.cn:89/gansu-spcrm/rest/AddCourse"
                        try:
                            r=requests.post(url=posturl,headers=head,data=postdata,timeout=(50,80)).text
                            # print(r)
                            
                            print("正在学习%s：%s，进度为%s"%(coursId,CourseName,kcjd))
                        except requests.exceptions.ConnectTimeout as e :
                            print("课程进度获取超时")
                # time.sleep(3)
                # b=time.time()
                # print(b)tim
                # tmp = b -a
                # print(b-a)
                print(loca)
                # if(len(studyList[0])<3):
                #     time.sleep(2)
        else:
            print("所有的课程全部学习完成")
            
if __name__=="__main__":
    LessonsNum=89
    pagerange=18
    url="http://www.gsgwypx.com.cn/index/centerIndex/2.shtml"
    headerstr = '''Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9
    Cache-Control: max-age=0
    Connection: keep-alive
    Cookie: isLogin=1; JSESSIONID=73C94A1D37EE2C1AB12575FA9345FC62
    Host: www.gsgwypx.com.cn
    Referer: http://www.gsgwypx.com.cn/index/index/2.shtml
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'''
    headers = copy_headers_dict(headerstr)
    f=open(r'E:/pro/gwyxxw/user.txt',encoding="utf-8").readlines()
    lins=[line.strip().split(':') for line in f]
    userName=lins[0][1]
    passwd=lins[1][1]
    # userName=input("请输入用户名：")
    # passwd=input("请输入密码：")
    getcookie=getcookie(headers,userName,passwd)
    headers['Cookie']=getcookie[0]+';'+getcookie[1]
    # print(headers)
    r= requests.get(url=url,headers=headers)
    gradeId="11"
    userId=getUserId(headers)
    lessLists = getLessons('http://www.gsgwypx.com.cn/gradeCourse/getGradeCourseList.do',\
               headers,gradeId,userId,pagerange)
    # for i in lessList:
    #     print(i)
    uncomplet = getUncompleteLesson(headers,lessLists,gradeId,userId)

    learnQuick(headers,gradeId,userId,uncomplet,10)
