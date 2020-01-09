"""MyVedioSystem URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

#以下三条新增
from django.views import static
from django.conf import settings
from django.conf.urls import url  #其实就是以前的re_path

from App import views

urlpatterns = [

    path('admin/', admin.site.urls),

    path('',include(("App.urls",'App'),namespace='app')),

    path('videoanalysis/',include(("VideoAnalysis.urls","VideoAnalysis"),namespace='app/videoanalysis')),

    #如果使用Django的web部署,则新增
    #url(r'^static/(?P<path>.*)$', static.serve,{'document_root': settings.STATIC_ROOT}, name='static'),

    path('aboutus/',include(("AboutUs.urls","AboutUs"),namespace='aboutus')),

    # 定义首页路由,Django按照顺序匹配路由,因此这个首页路由必须放在最后
    #path('',views.login),
    path('',views.aboutUs),
    #url(r'^$', views.login),

]
