from django.urls import path

from VideoAnalysis import views

urlpatterns =[

path("objectdetection_realtime/",views.objectDetection_realtime,name ='objectdetection_realtime'),


]

