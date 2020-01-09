from django.http import HttpResponse, StreamingHttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
import os

def object_detection(request):
    video_url_1 = "/static/video/reserch/目标检测.mp4"

    return render(request,"aboutus_templates/object_detection.html",context=locals())

def target_tracking(request):
    video_url_1 = "/static/video/reserch/目标跟踪.mp4"

    return render(request,"aboutus_templates/target_tracking.html",context=locals())

def re_identification(request):
    video_url_1 = "/static/video/reserch/re-identification.mp4"
    video_url_2 = "/static/video/reserch/重识别.mp4"

    return render(request,"aboutus_templates/re_identification.html",context=locals())

def abnormal_detection(request):
    video_url_1 = "/static/video/reserch/人流过线统计.mp4"
    video_url_2 = "/static/video/reserch/停车场围界.mp4"
    video_url_3 = "/static/video/reserch/物体搬移.mp4"
    video_url_4 = "/static/video/reserch/遗留物检测.mp4"

    return render(request,"aboutus_templates/abnormal_detection.html",context=locals())

def density_estimation(request):
    video_url_1 = "/static/video/reserch/人数估计模块录制.mp4"

    return render(request,"aboutus_templates/density_estimation.html",context=locals())

def video_defog(request):
    video_url_1 = "/static/video/reserch/video-defog.mp4"

    return render(request,"aboutus_templates/video_defog.html",context=locals())



def project_1(request):

    return render(request,"aboutus_templates/project_1.html",context=locals())

def project_2(request):
    video_url_1 = "/static/video/project_2/光启-固定背景人数.mp4"
    video_url_2 = "/static/video/project_2/光启-固定-异常-自拍.mp4"
    return render(request,"aboutus_templates/project_2.html",context=locals())

def project_3(request):
    video_url_1 = "/static/video/project_3/Abnormal-detection.mp4"
    video_url_2 = "/static/video/project_3/people-density.mp4"
    return render(request,"aboutus_templates/project_3.html",context=locals())

def project_4(request):
    video_url_1 = "/static/video/project_4/emp.mp4"
    video_url_2 = "/static/video/project_4/multi_object.mp4"
    video_url_3 = "/static/video/project_4/single_object.mp4"
    return render(request,"aboutus_templates/project_4.html",context=locals())



def members(request):

    return render(request,"aboutus_templates/members.html",context=locals())

def activities(request):

    return render(request,"aboutus_templates/activities.html",context=locals())
