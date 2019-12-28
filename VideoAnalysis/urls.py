from django.urls import path

from VideoAnalysis import views

urlpatterns =[

path("objectdetection_realtime/",views.objectDetection_realtime,name ='objectdetection_realtime'),

path("objectdetection_playback/",views.objectDetection_playback,name ='objectdetection_playback'),

path("objectdetection_playback/",views.objectDetection_playback,name ='objectdetection_playback'),

]