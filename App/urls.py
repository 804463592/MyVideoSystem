from django.urls import path,re_path

from App import views

urlpatterns =[

    #登录和登出
    path("login/",views.login,name ='login'),
    path("logout/",views.logout,name ='logout'),

    #path("videoviewer/",views.videoViewer,name ='videoviewer'),
    #path("videoviewer1/",views.videoViewer1,name ='videoviewer1'),
    #path("videoviewer2/", views.videoViewer2, name='videoviewer2'),

    path("videosquare/", views.videoSquare, name="videoSquare"),

    #以下三种方式是几乎等效的
    #re_path(r'^videoviewer/(\d+)/(\d+)/$', views.videoViewer, name='videoviewer'),
    #re_path(r'^videoviewer/([0-9]{1})/([0-9]{1})/$', views.videoViewer, name='videoviewer'),
    re_path(r'^videoviewer/(?P<camera_idx>[0-9]{1})/(?P<is_playing>[0-9]{1})/$', views.videoViewer,name ='videoviewer'),

    re_path(r'^videosquare/videostreamplay/(\d+)/$',views.videoStreamPlay,name ="videostreamplay"),


    path("videolookback/", views.videoLookBack, name="videoLookback"),
    path("videolookback/videoplay/", views.videoPlay, name="videoPlay"),

    path("videoanalysis/", views.videoAnalysis, name="videoanalysis"),

    #系统配置和信息
    path("configuration/", views.configuration, name="configuration"),
    path("systeminformation/", views.systemInformation, name="systeminformation"),

    #注册和关于
    path("signup/",views.signup,name = "signup"),
    path("aboutus/",views.aboutUs,name ="aboutus"),


    #下面的是没有用的
    path("savevideo/",views.saveVideo,name ="savevideo"),

    path("testfile/",views.testFile),

    path("testvideo/",views.testVideo),

    path("queryvideo/",views.queryVideo),

    path("checkuser/", views.check_user),

    path("checkemail/", views.check_email),

]