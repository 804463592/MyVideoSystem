from django.db import models
import django.utils.timezone as timezone


import os
import time
import uuid

def generate_video_path(instance,filename="1.mp4"):
      '''
      按照摄像头+日期+视频名的路径存储视频
      :param instance: 存储的数据库object对象
      :param filename: 将要存入的视频（文件）
      :return: 路径
      '''
      database_video_root_path ="realvideo"
      time_path =time.strftime("%Y年%m月%d日%H时%M分")

      #对文件进行重命名,避免重名
      #ext = filename.split('.')[-1]
      #filename = '{}.{}'.format(uuid.uuid4().hex[:10], ext)

      # return the whole path to the file
      return os.path.join(database_video_root_path,instance.camera_name,time_path,filename)

class VideoStorage(models.Model):

      video_id = models.AutoField(primary_key=True)

      camera_name =models.CharField(max_length=16)

      video_file =models.FileField(upload_to=generate_video_path)

      start_time =models.DateTimeField(verbose_name='开始时间',default=timezone.now)

      end_time =models.DateTimeField(verbose_name="结束时间",default=timezone.now)


class UserInfo(models.Model):
      user_name =models.CharField(max_length=32,unique=True)
      user_email = models.CharField(max_length=64,unique=True)
      user_password =models.CharField(max_length=32)
      user_icom = models.ImageField(upload_to="icon", default=u"/static/images/login_images/avtar.png", max_length=100)
      is_admin =models.BooleanField(null=False,default=False)

if __name__ =="__main__":
    #generate_video_path()
    pass
