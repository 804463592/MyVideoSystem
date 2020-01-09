from django.urls import path

from AboutUs import views

urlpatterns =[

    path("object_detection/",views.object_detection,name='object_detection'),
    path("target_tracking/",views.target_tracking,name='target_tracking'),
    path("re_identification/",views.re_identification,name='re_identification'),
    path("abnormal_detection/",views.abnormal_detection,name='abnormal_detection'),
    path("density_estimation/",views.density_estimation,name='density_estimation'),
    path("video_defog/",views.video_defog,name='video_defog'),

    path("project_1/", views.project_1, name='project_1'),
    path("project_2/", views.project_2, name='project_2'),
    path("project_3/", views.project_3, name='project_3'),
    path("project_4/", views.project_4, name='project_4'),

    path("members/", views.members, name='members'),
    path("activities/", views.activities, name='activities'),





]

