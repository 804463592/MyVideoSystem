
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, StreamingHttpResponse, JsonResponse
from datetime import datetime
from App.models import VideoStorage

# Create your views here.
def objectDetection_realtime(request):

    return render(request,"analysis_templates/objectdetection_realtime.html")

def objectDetection_playback(request):
    username = request.session.get("username")
    if not username:
        return redirect(reverse("app:login"))

    def addtwodimdict(thedict, key_a, key_b, val):
        if key_a in thedict:
            thedict[key_a].update({key_b: val})
        else:
            thedict.update({key_a: {key_b: val}})

    if request.method =="GET":
        return render(request, "analysis_templates/objectdetection_playback.html", context=locals())

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