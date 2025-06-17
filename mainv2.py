
import os
import requests
from bs4 import BeautifulSoup
    # 在文件开头添加：
import argparse
from lxpy import copy_headers_dict 
import time
import random

def getUserId(headers):
    url="https://gwypx.gsdj.gov.cn/user/userInfo.do?flag=person"
    rs=requests.post(url,headers=headers).content
    bs=BeautifulSoup(rs,'html.parser')
    # print(bs)
    userId=bs.find('input',attrs={'id':"userId"})['value']
    return userId
def getgradeId(headers):
    url="https://gwypx.gsdj.gov.cn/grade/toMyGradeList.do"
    r=requests.post(url,headers=headers).content
    rs = BeautifulSoup(r,'html.parser')
    gradeId =(rs.find('a',class_="lan"))['onclick'][20:-4]
    print("gradId is %s"%gradeId)
    return gradeId
def gettotalPage(headers,gradeId):
    url="https://gwypx.gsdj.gov.cn/gradeCourse/getGradeCourseList.do"
    data={"gradeId":gradeId,"gcState":1}
    r=requests.post(url,headers=headers,data=data)
    # reqHeaders=r.request.body
    # print(reqHeaders)
    rs = BeautifulSoup(r.content,'html.parser')
    numbs =rs.find_all('b',class_="red")
    text=[]
    for i in numbs:
        text.append(i.text)
    if(len(text)==2):
        totalPage=text[1]
    else:
        print("获取课程总页数失败")
    # print(totalPage)
    return int(totalPage)

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
    print("正在获取未学习的课程列表……")
    '''
    示例url:
    https://gwypx.gsdj.gov.cn/gradeCourse/getCourseUsersJindu.do?gradeId=11&userId=261812&courseId=1012&gcState=1
    ["'1001'"（课程Id）, "'GS1653284077.mp4'"（视频Id）, "'171'", "'碳中和目标下的能源和经济转型研究（上）'"]
    '''
    uncompleteLesson=[] #存放了所有的未播放完成的课程
    uncompleteLessonId=[]
    uncompleteVedioId=[]
    uncompleteLessonName=[]
    uncompletkcdurations=[]
    for lessonsId in lessonLists[0]:

        # lesslsttmp=lessons.removeprefix("javascript:BeginStudy(").removesuffix(');').split(',') 
        try:
            courseId=int(lessonsId)
        except ValueError:
            offlineid=lessonLists[0].index(lessonsId)
            lessonLists[1].insert(offlineid,0)
            lessonLists[2].insert(offlineid,0)
            courseId=0
        # courseId=courseId.removeprefix("'").removesuffix("'")
        if courseId!=0:
            posturl="https://gwypx.gsdj.gov.cn/gradeCourse/getCourseUsersJindu.do?gradeId=%s&userId=%s&courseI=d=%s&gcState=1 "\
                %(gradeId,userId,courseId)
            # print(posturl)
            kcjd=requests.post(url=posturl,headers=head).text
            # print(kcjd)
            if (str(kcjd)!='100%'):
                # print(kcjd)
                #获取当前课程ID的索引，并将视频ID：lessonLists[1]，课程名称lessonLists[2]在相应的索引位置取出来，形成一个新的列表。
                #获取索引：
                uncompleteLessonId.append(courseId)
                indx=lessonLists[0].index(lessonsId)
                uncompleteVedioId.append(lessonLists[1][indx])
                uncompleteLessonName.append(lessonLists[2][indx])
                uncompletkcdurations.append(lessonLists[3][indx])
                #需要重新写未完成播放课程列表函数逻辑2023-08-07
    uncompleteLesson=[uncompleteLessonId,uncompleteVedioId,uncompleteLessonName,uncompletkcdurations]
    return uncompleteLesson

def getjd(head,gradeId,userId,courseId):
    posturl="https://gwypx.gsdj.gov.cn/gradeCourse/getCourseUsersJindu.do?gradeId=%s&userId=%s&courseId=%s&gcState=1 "\
              %(gradeId,userId,courseId)
    # print(posturl)
    try:
        kcjd=requests.post(url=posturl,headers=head).text
    # print("当前学习的课程为%s,学习进度为%s"%(courseId,kcjd))
    except requests.exceptions.ConnectTimeout as e:
        print("获取课程进度超时！")
        kcjd="*"
    except requests.exceptions.ConnectionError as e:
        print("获取课程进度超时！")
        kcjd="*"
    except requests.exceptions.HTTPError as e:
        print("获取课程进度超时！")
        kcjd="*"
    except requests.RequestException as e:
        print("获取课程进度超时！")
        kcjd="*"    
    return kcjd

def learn(head,gradeId,userId,uncompleteLessList):    #学习课程
    '''
    用POST方法向该链接：https://gwypx.gsdj.gov.cn:84/gansu-spcrm/rest/AddCourse
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
        posturl="https://gwypx.gsdj.gov.cn:84/gansu-spcrm/rest/AddCourse"

        coursId=unLesson[0]
        uncompletcoursIds=[]

        # coursId=coursId.removeprefix("'").removesuffix("'")
        CourseCode=unLesson[1]
        # CourseCode=CourseCode.removeprefix("'").removesuffix("'")
        for m in range(0,6000,10):
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
        #"head,gradeId,userId,uncompleteLessList,nums"
    else:
        if (len(uncompleteLessons[0])<nums):
            studyList=uncompleteLessons
            unstudyList=[]
        else:
            studyList = [uncompleteLessons[0][:nums],uncompleteLessons[1][:nums],uncompleteLessons[2][:nums],uncompleteLessons[3][:nums]]
            unstudyList=[uncompleteLessons[0][nums:],uncompleteLessons[1][nums:],uncompleteLessons[2][nums:],uncompleteLessons[3][nums:]]
            # Duration=studyList[3][studyList[0].index(coursId)]
        while(len(studyList[0])!=0):
            maxduration=max(studyList[3])
            for loca in range(random.randint(1,10),maxduration,nums):
                # time.sleep(10/int(len(uncompleteLessons[0])))
                for i in studyList[0]:
                    # loca=loca+loca*loca

                    coursId =i
                    CourseCode=studyList[1][studyList[0].index(coursId)]
                    Duration=studyList[3][studyList[0].index(coursId)]
                    postdata={"CourseId":coursId,
                                    "UserId":userId,
                                    "SessionId":"31411EE795AB12F237175EC6ECE65DAD769A61EA36C015621F63A462EBD750A3AA107CD283810F3A9DADF60AD8AF2A056E7A1267A9284D8396A804071661E4BFE71A6222FC0ED462",
                                    "GreadId":gradeId,
                                    "Location":loca,
                                    "Sessiontime":"00:00:5",
                                    "ScormOrVideo":"171",
                                    "Systime":int(time.time()*1000)+loca*nums*100,
                                    "CourseCode":CourseCode,
                                    "Duration":Duration}
                    CourseName = studyList[2][studyList[0].index(coursId)]
                    # if (loca%10==0):
                    kcjd = getjd(head,gradeId,userId,coursId)
                    time.sleep(0.1)
                    if(kcjd=='100%'):
                        os.system("cls")
                        print(kcjd)
                        print("%s的课程已经学完"%coursId)
                        index = studyList[0].index(coursId)
                        (studyList[0]).remove(coursId)
                        (studyList[1]).pop(index)
                        studyList[2].pop(index)
                        studyList[3].pop(index)
                        if(len(unstudyList[0])!=0):
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
                        posturl="https://gwypx.gsdj.gov.cn/gansu-spcrm/rest/AddCourse"
                        try:
                            r=requests.post(url=posturl,headers=head,data=postdata,timeout=(50,80)).text
                            # print(r)
                            
                            print("正在学习%s：%s，进度为%s"%(coursId,CourseName,kcjd))
                            # time.sleep(0.1)
                        except requests.exceptions.ConnectTimeout as e :
                            print("课程进度获取超时")
            print("一轮duration完成，开始下一轮")
            time.sleep(5)
           
        print("所有的课程全部学习完成，开始考试")
def kaoshi(header):
    # radio=[]
    for courseId in range(1151,1245):
        radiodx=[]
        radiopd=[]
         #获取考题信息
        url="https://gwypx.gsdj.gov.cn/gradeExam/gradeExamInfo.do?courseId=%d&gradeId=11"%courseId
        r=requests.get(url=url,headers=header).content
        bs=BeautifulSoup(r,"html.parser").find_all("input",type="radio")
        for i in bs:
            tmp=i.get("name")
            if tmp[0:3]=="dan":
                radiodx.append(tmp)
            else:
                radiopd.append(tmp)
        radiodx=list(set(radiodx)) #所有单选题
        if  len(radiodx)!=0:
            radiopd=list(set(radiopd))#所有判断题
            finddx=BeautifulSoup(r,"html.parser").find_all("input",type="checkbox")
            
            checkbox=[]#多选题目
            for idx in finddx:
                tmps=(idx.get('name'),idx.get("value"))
                checkbox.append(tmps)
            # print("多选：%s"%checkbox)
            # print("判断：%s"%radiopd)
            # print("单选：%s"%radiodx)
            #构造请求数据
            postdate=[("courseId",courseId),("testTime",""),('gradeId',13),('jsTime','00:06:50')]
            for i in radiodx:
                postdate.append((i,'A'))
            for i in checkbox:
                postdate.append(i) 
            for i in radiopd:
                postdate.append((i,1))    
                #courseId=925&testTime=&gradeId=11&jsTime=00:06:50&danxuan8183=A&danxuan8184=A&duoxuan8185=A&duoxuan8185=B&duoxuan8185=C&duoxuan8185=D&panduan8186=1&panduan8187=1'
        #拼接答案
            url= 'https://gwypx.gsdj.gov.cn/gradeExam/gradeExamSave.do?callback=myCallbackFunction'
            res=requests.post(url,headers=header,data=postdate).text
            rep=res[20:-2]
            if(rep!="isOk"):
                postdate=[("courseId",courseId),("testTime",""),('gradeId',13),('jsTime','00:06:50')]
                for i in radiodx:
                    postdate.append((i,'B'))
                for i in checkbox:
                    postdate.append(i) 
                for i in radiopd:
                    postdate.append((i,1))
                resd=requests.post(url,headers=header,data=postdate).text
                rep=resd[20:-2]
            if(rep!="isOk"):
                postdate=[("courseId",courseId),("testTime",""),('gradeId',13),('jsTime','00:06:50')]
                for i in radiodx:
                    postdate.append((i,'C'))
                for i in checkbox:
                    postdate.append(i) 
                for i in radiopd:
                    postdate.append((i,1))
                resd=requests.post(url,headers=header,data=postdate).text
                rep=resd[20:-2]
            if(rep!="isOk"):
                postdate=[("courseId",courseId),("testTime",""),('gradeId',13),('jsTime','00:06:50')]
                for i in radiodx:
                    postdate.append((i,'D'))
                for i in checkbox:
                    postdate.append(i) 
                for i in radiopd:
                    postdate.append((i,1))
                resd=requests.post(url,headers=header,data=postdate).text
                rep=resd[20:-2] 
            if(rep!="isOk"):
                postdate=[("courseId",courseId),("testTime",""),('gradeId',13),('jsTime','00:06:50')]
                for i in radiodx:
                    postdate.append((i,'A'))
                for i in checkbox:
                    postdate.append(i) 
                for i in radiopd:
                    postdate.append((i,0))
                resd=requests.post(url,headers=header,data=postdate).text
                rep=resd[20:-2] 
            if(rep!="isOk"):
                postdate=[("courseId",courseId),("testTime",""),('gradeId',13),('jsTime','00:06:50')]
                for i in radiodx:
                    postdate.append((i,'B'))
                for i in checkbox:
                    postdate.append(i) 
                for i in radiopd:
                    postdate.append((i,0))
                resd=requests.post(url,headers=header,data=postdate).text
                rep=resd[20:-2]                
            if(rep!="isOk"):
                postdate=[("courseId",courseId),("testTime",""),('gradeId',13),('jsTime','00:06:50')]
                for i in radiodx:
                    postdate.append((i,'C'))
                for i in checkbox:
                    postdate.append(i) 
                for i in radiopd:
                    postdate.append((i,0))
                resd=requests.post(url,headers=header,data=postdate).text
                rep=resd[20:-2] 
            if(rep!="isOk"):
                postdate=[("courseId",courseId),("testTime",""),('gradeId',13),('jsTime','00:06:50')]
                for i in radiodx:
                    postdate.append((i,'D'))
                for i in checkbox:
                    postdate.append(i) 
                for i in radiopd:
                    postdate.append((i,0))
                resd=requests.post(url,headers=header,data=postdate).text
                rep=resd[20:-2]
            if(rep!="isOk"):
                postdate=[("courseId",courseId),("testTime",""),('gradeId',13),('jsTime','00:06:50')]
                # for i in radiodx:
                postdate.append((radiodx[0],'A'))
                postdate.append((radiodx[1],'B'))
                for i in checkbox:
                    postdate.append(i) 
                for i in radiopd:
                    postdate.append((i,0))
                resd=requests.post(url,headers=header,data=postdate).text
                rep=resd[20:-2]
            if(rep!="isOk"):
                postdate=[("courseId",courseId),("testTime",""),('gradeId',13),('jsTime','00:06:50')]
                # for i in radiodx:
                postdate.append((radiodx[0],'A'))
                postdate.append((radiodx[1],'C'))
                for i in checkbox:
                    postdate.append(i) 
                for i in radiopd:
                    postdate.append((i,0))
                resd=requests.post(url,headers=header,data=postdate).text
                rep=resd[20:-2]
            if(rep!="isOk"):
                postdate=[("courseId",courseId),("testTime",""),('gradeId',13),('jsTime','00:06:50')]
                # for i in radiodx:
                postdate.append((radiodx[0],'A'))
                postdate.append((radiodx[1],'D'))
                for i in checkbox:
                    postdate.append(i) 
                for i in radiopd:
                    postdate.append((i,0))
                resd=requests.post(url,headers=header,data=postdate).text
                rep=resd[20:-2]
            if(rep!="isOk"):
                postdate=[("courseId",courseId),("testTime",""),('gradeId',13),('jsTime','00:06:50')]
                # for i in radiodx:
                postdate.append((radiodx[0],'A'))
                postdate.append((radiodx[1],'B'))
                for i in checkbox:
                    postdate.append(i) 
                # for i in radiopd:
                postdate.append((radiopd[0],0))
                postdate.append((radiopd[1],1))
                resd=requests.post(url,headers=header,data=postdate).text
                rep=resd[20:-2]
            if(rep!="isOk"):
                postdate=[("courseId",courseId),("testTime",""),('gradeId',13),('jsTime','00:06:50')]
                # for i in radiodx:
                postdate.append((radiodx[0],'A'))
                postdate.append((radiodx[1],'C'))
                for i in checkbox:
                    postdate.append(i) 
                postdate.append((radiopd[0],0))
                postdate.append((radiopd[1],1))
                resd=requests.post(url,headers=header,data=postdate).text
                rep=resd[20:-2]
            if(rep!="isOk"):
                postdate=[("courseId",courseId),("testTime",""),('gradeId',13),('jsTime','00:06:50')]
                # for i in radiodx:
                postdate.append((radiodx[0],'A'))
                postdate.append((radiodx[1],'D'))
                for i in checkbox:
                    postdate.append(i) 
                # for i in radiopd:
                #     postdate.append((i,0))
                postdate.append((radiopd[0],0))
                postdate.append((radiopd[1],1))
                resd=requests.post(url,headers=header,data=postdate).text
                rep=resd[20:-2]                      
            if (rep=="isOk"):
                print("第%d题已经考完，继续下一题考试"%courseId)
            else:
                
                print("第%d题答案错误，请手动作答当前题目"%courseId)
        else:
            print("课程未上线，不需要考试")
           
if __name__=="__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run course learning and exam automation.")
    parser.add_argument("--nums", type=int, default=10, help="Number of courses to learn concurrently (default: 10)")
    args = parser.parse_args()
    url="https://gwypx.gsdj.gov.cn/index/centerIndex/2.shtml"
    try:
        # f=open(r'E:\pro\gwyxxw\dist\user01\cookie.txt',encoding="utf-8").readlines()
        f=open(r'E:\pro\gwyxxw\dist\user01\cookie.txt',encoding="utf-8").readlines()

        # print(f)
        headerstr=f[1]
        # lins=[line.strip().split(':') for line in f]
        # userName=lins[0][1]
        # passwd=lins[1][1]
    except FileNotFoundError as e:
        print("用户配置文件不在此，请在当前目录下创建cookie.txt，内容为Cookie: token=176a4a5b-6e5d-4810-a0e3-230fce07abed; JSESSIONID=0D53AC689C88E01B9FB2903E9E90")
    # headerstr = '''
    #         Cookie: token=176a4a5b-6e5d-4810-a0e3-230fce07abed; JSESSIONID=0D53AC689C88E01B9FB2903E9E903B53
    #         '''
    headers = copy_headers_dict(headerstr)

    r= requests.get(url=url,headers=headers).content
    bs = BeautifulSoup(r,'lxml').title.string
    # print(type(r))
    # print(r)
    if(bs=='Insert title here'):
        while True:
            print("登录失败，请更新cookie值后再启动程序")
            time.sleep(1000000)
    else:
        gradeId=getgradeId(headers=headers)
        userId=getUserId(headers)
        totalPage=gettotalPage(headers=headers,gradeId=gradeId)
        lessLists = getLessons('https://gwypx.gsdj.gov.cn/gradeCourse/getGradeCourseList.do',\
                headers,gradeId,userId,totalPage)
        # for i in lessList:
        #     print(i)
        uncomplet = getUncompleteLesson(headers,lessLists,gradeId,userId)

        learnQuick(headers,gradeId,userId,uncomplet,nums=args.nums)
        kaoshi(headers)
        while True:
            print("课程学习考试完成，请及时打印证书")
            time.sleep(1000000)
