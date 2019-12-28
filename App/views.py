from django.http import HttpResponse, StreamingHttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from django.contrib import messages
from django.core import serializers

import json

from MyVedioSystem.settings import MEDIA_URL_PREFIX
from .utils import VideoCamera
from .utils import VideoManager

from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

import time
from .models import VideoStorage
from datetime import datetime
from datetime import timedelta

from .utils import SystemInfo

#系统信息
system_info =SystemInfo()

#管理摄像头的类,注意：usb摄像头必定是0,1号,ip摄像头从2开始排序
video_obj =VideoManager(camera_idx=0,camera_type='usb')

video_obj1=VideoManager(camera_idx=1,camera_type='usb')

video_obj2 =VideoManager(camera_idx=2,camera_type='ip',camera_address='rtsp://admin:scuimage508@202.115.53.245')



#系统最初的初始化时间
# first_login_flag = True
# init_time = ''


def startVideoCamera(*video_obj_list):
    # 仅仅只初始化线程一次
    for i in range(len(video_obj_list)):
        if video_obj_list[i].first_flag:
            video_obj_list[i].start()
            video_obj_list[i].first_flag = False

    # if video_obj.first_flag:
    #     video_obj.start()
    #     video_obj.first_flag = False
    #
    # if video_obj1.first_flag:
    #     video_obj1.start()
    #     video_obj1.first_flag = False
    #
    # if video_obj2.first_flag:
    #     video_obj2.start()
    #     video_obj2.first_flag = False

def videoSquare(request):

    username = request.session.get("username")
    if username:

        #确保开启了摄像头
        startVideoCamera(video_obj, video_obj1, video_obj2)

        #return HttpResponse("欢迎回来，%s" % username)
        return render(request, "basic_templates/videosquare.html", context=locals())
    else:
        return redirect(reverse("app:login"))

def login(request):

     if request.method =="GET":
        return render(request,"basic_templates/login3.html")

     elif request.method =="POST":
        username =request.POST.get("username")
        password =request.POST.get("password")
        if not all([username,password]):
            return render(request,"basic_templates/login3.html")

        if username =="admin" and password =="admin":

            # global first_login_flag
            # if first_login_flag:
            #     global init_time
            #     init_time = datetime.now()
            #     first_login_flag = False
            return render(request, "basic_templates/configuration.html")
        elif username =="libo" and password =="libo":

            #开启摄像头线程,可以重复调用,以确保在不同页面都保证开启
            startVideoCamera(video_obj,video_obj1,video_obj2)
            # 使用session会话技术
            request.session["username"] = username
             #返回用户界面
            return render(request, "basic_templates/videoanalysis.html", locals())
        errmsg = "用户名或者密码错误"
        return render(request,"basic_templates/login3.html",locals())

def user(request):

    username =request.session.get("username")

    #不一定要等于admin,username有值即代表已经登录
    if username:
        return HttpResponse("欢迎回来，%s"%username)

    return HttpResponse("请登录")

def logout(request):

    request.session.flush()

    return redirect(reverse("app:login"))

def videoViewer(request,camera_idx,is_playing):

    #视图函数接受的是内容是字符串类型

    username = request.session.get("username")
    if not username:
        return redirect(reverse("app:login"))

    if camera_idx == '0':
        video_object = video_obj
    elif camera_idx == '1':
        video_object = video_obj1
    else:
        video_object = video_obj2

    print(camera_idx,is_playing,type(camera_idx),type(is_playing))

    # 模板渲染
    if is_playing =='1':
       return StreamingHttpResponse(video_object.videoStream(),
                        content_type='multipart/x-mixed-replace; boundary=frame')
    elif is_playing =='0':
        return StreamingHttpResponse(video_object.getVideoPoster(),
                        content_type='multipart/x-mixed-replace; boundary=frame')
    else:
        return HttpResponse("failed!")


# def videoViewer1(request):
#     # 模板渲染
#     username = request.session.get("username")
#     if not username:
#         return redirect(reverse("app:login"))
#     return StreamingHttpResponse(video_obj1.videoStream(),
#                         content_type='multipart/x-mixed-replace; boundary=frame')
#

def videoLookBack(request):

    username = request.session.get("username")
    if not username:
        return redirect(reverse("app:login"))

    def addtwodimdict(thedict, key_a, key_b, val):
        if key_a in thedict:
            thedict[key_a].update({key_b: val})
        else:
            thedict.update({key_a: {key_b: val}})

    if request.method =="GET":

             return render(request, "basic_templates/videolookback.html", context=locals())

    elif request.method =="POST":
        year = int(request.POST.get("year", default=2019))
        month = int(request.POST.get("month", default=1))
        day = int(request.POST.get("day", default=1))

        hour = int(request.POST.get("hour", default=0))
        minute = int(request.POST.get("minute", default=0))

        query_datetime = datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=0)
        query_video = VideoStorage.objects.filter(start_time__gte=query_datetime).order_by("start_time")
        length = query_video.count()

        if query_video.exists():
            # jsondata = {"msg": "ok",
            #         "data": {"start_time": query_video.start_time,"camera_name":query_video.camera_name,"end_time":query_video.end_time,"video_file":str(query_video.video_file)}
            #         }
            json_data = dict()
            for i, video in enumerate(range(length)):
                key = i
                addtwodimdict(json_data, key, "start_time", query_video[i].start_time.strftime("%Y-%m-%d %H:%M:%S"))
                addtwodimdict(json_data, key, "video_file", str(query_video[i].video_file).replace("realVideo/", ""))
                addtwodimdict(json_data, key, "end_time", query_video[i].end_time.strftime("%Y-%m-%d %H:%M:%S"))
                addtwodimdict(json_data, key, "camera_name", query_video[i].camera_name)

            # jsondata =serializers.serialize("json",query_video)
            return JsonResponse(data=json_data, safe=False)

        else:
            return JsonResponse(data={"msg":"NoVideo"})

def videoAnalysis(request):

    # 确保开启了摄像头
    startVideoCamera(video_obj, video_obj1, video_obj2)

    return render(request,"basic_templates/videoanalysis.html")

def videoStreamPlay(request,camera_idx):
    username = request.session.get("username")
    if not username:
        return redirect(reverse("app:login"))

    if request.method == "GET":
        #print("camera_idx:",camera_idx)
        return render(request,"basic_templates/video_stream_play.html",context=locals())


def videoPlay(request):

    username = request.session.get("username")
    if not username:
        return redirect(reverse("app:login"))

    if request.method =="GET":
        #实际上前端还传了更多参数,但是这里只需要文件名字就够了
        video_file_name =request.GET.get("video_file_name",default="20191220152143.mp4")

        #video_url = "/static/videoStorage/realVideo/"+video_file_name

        video_url =""
        videos_to_play =VideoStorage.objects.filter(video_file=video_file_name)

        #如果不存在又怎么办呢？极端情况下,有可能就在查询的这段时间里,视频已经被覆盖了
        if videos_to_play.exists():
           video_url = MEDIA_URL_PREFIX + videos_to_play.first().video_file.url
           print("video_url",video_url)
        #TODO:考虑下这里查不到怎么办

        video_camera_name =request.GET.get("video_camera_name",default="camera0")
        video_start_time =request.GET.get("video_start_time",default=None)
        video_end_time =request.GET.get("video_end_time",default=None)

        return render(request,"basic_templates/videoplay.html",context={"video_url":video_url,"video_camera_name":video_camera_name,
                                                    "video_start_time":video_start_time,"video_end_time":video_end_time
                                                    })


def configuration(request):

    return render(request,"basic_templates/configuration.html")

def systemInformation(request):
    if request.method =="GET":

        return render(request, "basic_templates/systeminformation.html", context=locals())

        # return render(request, "basic_templates/videolookback.html", context=locals())
    elif request.method =="POST":

        init_time = system_info.getInitTime()

        # init_time = "2019-12-26T09:50:43.919"
        # print(init_time.strftime("%Y-%m-%d %H:%M:%S"))
        # addtwodimdict(json_data, 1, "init_time", init_time)

        return JsonResponse(data=init_time,safe=False)


def signUp(request):

    return HttpResponse("这里是注册页面")


def aboutUs(request):

    return HttpResponse("关于我们")


#
#
# def recordstatus(request):
#
#     username = request.session.get("username")
#     if not username:
#         return redirect(reverse("app:login"))
#
#     if request.method =='POST':
#         print("the method is POST")
#
#     json_result = json.loads(request.body)
#     status =json_result['status']
#
#     if status =='start_record':
#
#         videoObj.start_record()
#
#         return JsonResponse(data={"result":"start recording"})
#
#     elif status =='stop_record':
#
#         videoObj.stop_record()
#
#         return JsonResponse(data={"result": "stop recording"})
#
# def playstatus(request):
#     username = request.session.get("username")
#     if not username:
#         return redirect(reverse("app:login"))
#
#     if request.method =='POST':
#         print("the method is POST")
#
#     postBody = request.body
#     json_result = json.loads(postBody)
#
#     status =json_result['status']
#
#     if status =='start_play':
#
#          videoObj.start_play()
#
#          return JsonResponse(data={"result": "start playing"})
#
#     elif status =='suspend_play':
#
#          videoObj.stop_paly()
#
#          return JsonResponse(data={"result":"stop playing"})
#



# """
#
# 下面的视图函数全是测试用的,暂无实际用处：
#
# """
#

def saveVideo(request):

    current_time = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))

    print(type(current_time),current_time)

    front_path = "{0}.{1}".format(current_time, "mp4")

    f = BytesIO()

    file_object = open('./static/video1.mp4',"rb")
    try:
        all_the_bytes = file_object.read()
    finally:
        file_object.close()

    f.write(all_the_bytes)

    video_loaded = InMemoryUploadedFile(f, None, front_path, "video/mpeg", len(all_the_bytes), None, None)

    # with open("./static/video.avi", "rb") as f:
    #     # 循环读取一段视频，一次性读取1024个字节
    #     while True:
    #         strb = f.read(1024)
    #         if strb == b"":
    #             break
    #         print(type(strb))

    #VideoStorage.objects.last()

    nowtime =datetime.now()

    newvideo =VideoStorage()

    newvideo.camera_name ="camera1"

    newvideo.start_time =nowtime

    newvideo.video_file =video_loaded

    newvideo.save()

    return HttpResponse("已经存储视频")


def testFile(request):
    #earliest_video =VideoStorage.objects.last()
    if request.method =="POST":
        json_result = json.loads(request.body)
        minute = int(json_result['minute'])

        print("minute:",minute)

        query_video = VideoStorage.objects.filter(start_time__minute=minute).order_by("start_time")
        return JsonResponse(data={"json_state": "already received json!"})

        # return render(request, "videoShow.html", context=locals())
    else:
        return HttpResponse("testFile!!!")

    #query_video = VideoStorage.objects.all()

    #print("earliest_video type:",type(earliest_video))

    #print("earliest_video video file type:",type(earliest_video.video_file))

    #print(earliest_video.video_file.path)

    # import os
    #
    # if os.path.exists(video.video_file.path):
    #     os.remove(video.video_file.path)

    # print(video.video_file.url)
    #
    # print(MEDIA_URL_PREFIX+video.video_file.url)

    # return render(request,"videolookback.html",context =locals())


def testVideo(request):

    testvideo_count =VideoStorage.objects.all().count()

    testvideo =VideoStorage.objects.all().first()

    video_url =MEDIA_URL_PREFIX+testvideo.video_file.url
    #testvideo.delete()
    print(video_url)

    #return HttpResponse("视频个数为{}".format(testvideo_count))
    return render(request,"videoShow.html",context=locals())

def queryVideo(request):

    #通过request获取查询字段

    #假设这是我想看的时间，那么需要获取一个查询时间段,假设每段视频的长度为video_timedelta
    video_timedelta =timedelta(minutes=10)
    query_time =datetime(year=2019,month=12,day =3,hour=22,minute=10,second=0)
    query_range =[query_time-video_timedelta,query_time+video_timedelta]
    query_video =VideoStorage.objects.filter(start_time__range=query_range).order_by("start_time")

    #时间间隔
    t_now =datetime.now()
    t_delta =timedelta(minutes=20000) #这个时间间隔决定了,我们的数据库最多能保存多长时间的视频
    t_start =t_now -t_delta

    print("t_now:",t_now)
    print("t_start:",t_start)

    query =VideoStorage.objects.filter(camera_name="camera1",start_time__range=[t_start,t_now])

    #query_test =VideoStorage.objects.filter()

    #query = VideoStorage.objects.filter(start_time__year=2020)

    if query.exists() or query_video.exists():
        #print("objects type:", VideoStorage.objects)

        #print("query:", query[0])

        #print("query name:", query[0].start_time)

        return render(request, "videoShow.html", context=locals())
    else:
        return HttpResponse("查询不存在")


