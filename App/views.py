from django.http import HttpResponse, StreamingHttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from django.contrib import messages
from django.core import serializers

import json

from MyVideoSystem.settings import MEDIA_URL_PREFIX
from .utils import VideoCamera
from .utils import VideoManager

from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

import time
from .models import VideoStorage
from .models import UserInfo
from datetime import datetime
from datetime import timedelta

from .utils import SystemInfo
from .utils import CheckUserEmail

from django.db.models import Q

#系统信息
system_info =SystemInfo()

#验证用户及邮箱的对象
check_user_email =CheckUserEmail()

#系统最初的初始化时间
# first_login_flag = True
# init_time = ''

# 管理摄像头的类,注意：usb摄像头必定是0,1号,ip摄像头从2开始排序; 使用默认配置信息
video_obj = VideoManager(camera_idx=0, camera_type='usb', system_info=system_info)

video_obj1 = VideoManager(camera_idx=1, camera_type='usb', system_info=system_info)

video_obj2 = VideoManager(camera_idx=2, camera_type='ip',
                          camera_address='rtsp://admin:scuimage508@202.115.52.245', system_info=system_info)


def startVideoCamera(system_info,*video_obj_list):
    # 仅仅只初始化线程一次，保证系统最开始开启，就不能改变。
    for i in range(len(video_obj_list)):
        if video_obj_list[i].first_flag:

            print(system_info.videos_max_num,system_info.frames_max_num,system_info.videos_fps)

            #配置的系统信息
            video_obj_list[i].setVideosMaxNum(system_info)
            video_obj_list[i].setFramesMaxNumAndFps(system_info)

            #开启相关线程
            video_obj_list[i].start()
            video_obj_list[i].first_flag = False

def videoSquare(request):
    # 保证用户已登录
    username = request.session.get("username")
    if username:

        #return HttpResponse("欢迎回来，%s" % username)
        return render(request, "basic_templates/videosquare.html", context=locals())
    else:
        return redirect(reverse("app:login"))

def login(request):
     if request.method =="GET":
        return render(request,"basic_templates/login3.html")

     elif request.method =="POST":
        name_or_email =request.POST.get("username")

        #如果是邮箱,为方便起见,也全部转换成用户名
        user_name =check_user_email.matchName(name_or_email)
        pass_word =request.POST.get("password")


        #check_user_email.matchName如果返回None,则重新登录
        if not all([user_name,pass_word]):

            return render(request,"basic_templates/login3.html")

        if check_user_email.checkNamePassword(user_name,pass_word):


            # 使用session会话技术
            request.session["username"] = user_name

            #管理员登录,直接去到系统信息页面
            if check_user_email.checkAdmin(user_name):

                #return render(request, "basic_templates/configuration.html")
                #redirevt重定向，reverse反向解析
                 return redirect(reverse("app:configuration"))
            #普通用户登录
            else:

                #开启摄像头线程,可以重复调用,以确保在不同页面都保证开启
                # startVideoCamera(video_obj,video_obj1,video_obj2)
                 #返回一个界面
                return render(request, "basic_templates/videoanalysis.html", locals())

        else:
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

            json_data = dict()
            for i, video in enumerate(range(length)):
                key = i
                addtwodimdict(json_data, key, "start_time", query_video[i].start_time.strftime("%Y-%m-%d %H:%M:%S"))
                addtwodimdict(json_data, key, "video_file", str(query_video[i].video_file).replace("realVideo/", ""))
                addtwodimdict(json_data, key, "end_time", query_video[i].end_time.strftime("%Y-%m-%d %H:%M:%S"))
                addtwodimdict(json_data, key, "camera_name", query_video[i].camera_name)

            return JsonResponse(data=json_data, safe=False)

        else:
            return JsonResponse(data={"msg":"NoVideo"})

def videoAnalysis(request):
    username = request.session.get("username")
    if not username:
        return redirect(reverse("app:login"))

    return render(request,"basic_templates/videoanalysis.html")


def videoStreamPlay(request,camera_idx):
    username = request.session.get("username")
    if not username:
        return redirect(reverse("app:login"))

    if request.method == "GET":

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
    # 判断当前用户是否登录
    username = request.session.get("username")
    if not username:
        return redirect(reverse("app:login"))

    if request.method =="GET":

        return render(request, "basic_templates/configuration.html")

    elif request.method =="POST":
        # 获取前端系统参数信息
        videos_max_num = int(request.POST.get("capacity"))
        video_length = int(request.POST.get('length'))
        videos_fps = int(request.POST.get('fps'))
        #print(videos_max_num, video_length, videos_fps)
        frames_max_num = 60*video_length*videos_fps
        #print("videos_max_num:",videos_max_num,"frames_max_num:",frames_max_num, "videos_fps:",videos_fps)

        # system_info.setVideosFps(videos_fps=videos_fps)
        # system_info.setVideosMaxNum(videos_max_num=videos_max_num)
        # system_info.setFrameMaxNum(frames_max_num=frames_max_num)

        system_info.setSystemInfo(videos_max_num=videos_max_num, frames_max_num=frames_max_num, videos_fps=videos_fps)

        # 验证当前用户是否为管理员,普通用户不允许修改
        if check_user_email.checkAdmin(username):
            # 设置系统参数,并开启线程（该函数可保证已经开启则不允许重复开启,即不允许重复设置）
            startVideoCamera(system_info, video_obj, video_obj1, video_obj2)

        return JsonResponse(data ={'msg':"system setting success！"}, safe=False)


def systemInformation(request):
    if request.method == "GET":

        return render(request, "basic_templates/systeminformation.html", context=locals())

        # return render(request, "basic_templates/videolookback.html", context=locals())
    elif request.method == "POST":

        init_time = system_info.getInitTime()

        return JsonResponse(data=init_time,safe=False)

def signUp(request):
    if request.method == "GET":
        return render(request, "basic_templates/signup.html")

    elif request.method == "POST":
        user_name = request.POST.get("username")
        user_email = request.POST.get("email")
        invite_code = request.POST.get("invite_code")

        # if UserInfo.objects.filter(Q(user_name=user_name) | Q(user_email=user_email)).exists():
        #     return HttpResponse("youwenti")
        #
        # else:
        password = request.POST.get("password")

        user = UserInfo()  # 创建一个类的实例

        user.user_name = user_name
        user.user_email = user_email
        user.user_password = password

        if invite_code == "VSST":
            user.is_admin = True
        else:
            user.is_admin = False

        user.save()
        return redirect(reverse("app:login"))
        #return render(request, "basic_templates/login3.html")

def checkUser(requst):
    username = requst.GET.get("username")
    users = UserInfo.objects.filter(user_name = username)
    data = {
        "status":200,
        "msg": "user is only"
    }
    if users.exists():
       data["status"]=901
       data["msg"]="user already exist"
    else:
        pass
    return JsonResponse(data=data)

def checkEmail(request):
    email = request.GET.get("email")
    emails = UserInfo.objects.filter(user_email = email)
    data = {
        "status":200,
        "msg": "email is only"
    }
    if emails.exists():
       data["status"]=901
       data["msg"]="email already exist"
    else:
        pass
    return JsonResponse(data=data)

def aboutUs(request):

    return render(request, "basic_templates/aboutus.html")






