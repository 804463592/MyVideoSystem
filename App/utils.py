import cv2
import threading
import time
import os
import re

from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from App.models import VideoStorage
from App.models import UserInfo

from datetime import datetime
from threading import Thread  # 创建线程的模块
from queue import Queue
from queue import Empty


#from opencv_yolov3.yolo import yolov3_detect

class VideoProcesser(object):

    def __init__(self,video_path="./static/transferStation",system_info=None,**kargs):

        super(VideoProcesser, self).__init__(**kargs)

        self.video_path = video_path
        #也可以使用相对路径, ./中,点不可缺少
        #self.video_path ="./static"

        if system_info is not None:
           self.videos_max_num =system_info.getVideosMaxNum()
           print("videos_max_num:",self.videos_max_num)
        else:
            self.videos_max_num =20

    def setVideosMaxNum(self,system_info):

        if system_info is not None:
            self.videos_max_num = system_info.getVideosMaxNum()
            print("set videos_max_num:", self.videos_max_num)
        else:
            self.videos_max_num = 20

    def checkPath(self,camera_name ="camera0"):
        for root, dirs, names in os.walk(self.video_path):
            for name in names:
                #分离文件名与扩展名
                ext = os.path.splitext(name)[1]

                #取前缀,辨别摄像头
                prefix = name.split('_',-1)[0]

                #print('prefix:',prefix)
                if prefix == camera_name and (ext == '.mp4' or ext =='.avi'):
                    fromdir = os.path.join(root,name)
                    print("即将删除中转路径下的残余视频：",fromdir)
                    if os.path.exists(fromdir):
                        os.remove(fromdir)

    def delEmptyDir(self,path):
        '''
        删除所有空文件夹
        :return:
        '''
        for (root, dirs, files) in os.walk(path):
            for item in dirs:
                dir = os.path.join(root, item)
                try:
                    os.rmdir(dir)  # os.rmdir() 方法用于删除指定路径的目录。仅当这文件夹是空的才可以, 否则, 抛出OSError。
                    print("删除空文件夹："+dir)
                except Exception as e:
                    print('Exception', e)

    def toH264(self,video_name="camera0_video.avi",delete_oringinal_video =False):
        """
        调用ffmpeg进行转码输出h264的mp4视频,输出路径和文件名均不变
        :param video_name: 处理的输入流视频名字，路径默认
        """
        output_name = video_name.replace("avi", "mp4")
        origin_video = os.path.join(self.video_path, video_name)
        convert_video = os.path.join(self.video_path, output_name)

        #使用base环境的ffmpeg,Django环境里的ffmpeg缺乏h264模块,装了半天也没装上,只能用base环境的了！！！
        cmdline = "source deactivate&&ffmpeg -i {} -vcodec h264 {}".format(origin_video, convert_video)
        #cmdline = "ffmpeg -i {} -vcodec h264 {}".format(origin_video, convert_video)

        #cmdline = "ffmpeg -i {} {}".format(origin_video, convert_video) #默认也会转成h264的

        #执行命令行
        flag = os.system(cmdline)
        if not flag:
            print("convert to h264 successfully!")
            #删除原avi视频
            if delete_oringinal_video and os.path.exists(origin_video):
                try:
                   fd =os.remove(origin_video)
                   print("fd:{},已删除{}".format(fd,origin_video))
                except NotImplementedError as e:
                    print("删除{}错误,出现{}！".format(origin_video,e))
            return True,output_name
        else:
            print("Fail to convert the video to h264!")
            return False,video_name

    def saveToDB(self,video_name,camera_name,start_time,end_time):
        """
        将转换后的h264视频存入数据库(存储时,需要考虑视频覆盖的问题)
        :param video_name:视频名字
        :return: None
        """
        video_path =os.path.join(self.video_path,video_name)
        current_time = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
        #存入数据库中的视频命名,注意，current_time并不代表视频开始时间
        front_path = "{}_{}.{}".format(camera_name,current_time, "mp4")
        #还可以这样使用uuid模块产生命名：
        # ext = filename.split('.')[-1]
        # filename = '{}.{}'.format(uuid.uuid4().hex[:10], ext)
        print(front_path)

        #二进制流
        f = BytesIO()

        #读取成视频流
        # file_object = open('./static/video1.mp4', "rb")
        file_object = open(video_path, "rb")
        try:
            all_the_bytes = file_object.read()
        finally:
            file_object.close()

        #写入二进制流f
        f.write(all_the_bytes)
        #格式转换
        video_loaded = InMemoryUploadedFile(f, None, front_path, "video/mpeg", len(all_the_bytes), None, None)

        #video_num =VideoStorage.objects.all().count()
        #以应对多摄像头的情况,所以需要对各自摄像头视频的数量进行统计
        video_num = VideoStorage.objects.filter(camera_name=camera_name).count()

        print("videos_max_num:", self.videos_max_num)
        if video_num<self.videos_max_num:
            VideoStorage.objects.create(camera_name=camera_name,video_file=video_loaded,start_time=start_time,end_time=end_time)
        else:
            #将新的视频,覆盖最老的视频
            earliest_video =VideoStorage.objects.all().order_by("start_time").first()

            #获取最早的时间,目前只想到这种先排序再查找的做法,因为好像无法直接查最早的时间？？？
            earliest_video_id = earliest_video.video_id

            # 这里虽然视频数据更新了,但是原来的视频还在,因此需要手动删除。另外删除视频后,还可能出现空文件夹,这也需要我们删除
            remove_video_path =earliest_video.video_file.path
            if os.path.exists(remove_video_path):
                print("删除{}！".format(remove_video_path))
                os.remove(remove_video_path)

            #TODO：清除空文件夹

            #这里主键设为了start_time,而因为要更新主键,对obj使用save()会导致orm找不到原来的对象,因而会新建一条数据。但是不知道为什么存进去的视频路径，没有前缀realVideo？
            #改成下面这样，将video_id设为主键,从而不更新主键,存储的视频路径还是没有前缀？？？
            #VideoStorage.objects.filter(video_id=earliest_video_id).update(camera_name=camera_name,video_file=video_loaded,start_time=start_time,end_time=end_time)

            #为什么这样存储的视频就有前缀了？？？
            update_obj=VideoStorage.objects.get(video_id=earliest_video_id)
            update_obj.camera_name =camera_name
            update_obj.video_file =video_loaded
            update_obj.start_time =start_time
            update_obj.end_time =end_time
            update_obj.save()

        #删除原始的mp4视频
        #self.delOriginVideo(video_name)
        video_path = os.path.join(self.video_path, video_name)
        if os.path.exists(video_path):
            os.remove(video_path)
            print("删除视频{}成功！".format(video_path))
        else:
            print("删除视频{video}时,{video}不存在！".format(video=video_path))
        self.delEmptyDir(os.path.join("./static/videoStorage/realvideo",camera_name))

class VideoInfo(object):
    '''
    用于保存视频信息的类
    1.获取视频名称
    2.获取开始时间
    3.获取结束时间
    4.获取摄像机名称
    '''
    def __init__(self,camera_name,video_name,start_time,end_time):
        self.video_name =video_name
        self.start_time =start_time
        self.end_time =end_time
        self.camera_name =camera_name

    def getVideoName(self):
        return self.video_name

    def getStartTime(self):
        return self.start_time

    def getEndTime(self):
        return self.end_time

    def getCameraName(self):
        return self.camera_name

class VideoCamera(VideoProcesser):
    def __init__(self,camera_idx =0,camera_address =None,camera_type ="usb",system_info =None,**kargs):

        # VideoProcesser.__init__()
        super(VideoCamera, self).__init__(system_info=system_info,**kargs)

        #无论usb还是ip,均采用序号给摄像头命名
        self.camera_name = "camera{}".format(camera_idx)

        #摄像头类型,"usb"或者"ip"
        self.camera_type =camera_type

        # 打开摄像头， 0代表笔记本内置摄像头
        if self.camera_type=="usb" and camera_address is None:
            self.cap = cv2.VideoCapture(camera_idx)
        elif self.camera_type=="ip" and camera_address is not None:
            self.cap =cv2.VideoCapture(camera_address)
        else:
            raise ValueError #传入的值不对

        # 初始化视频录制环境
        self.is_record = False
        self.out = None
        self.is_play =True

        # 视频录制线程
        self.recordingThread = None

        #表示当前帧的周期,先假设每段视频存400帧
        self.current_frame_num =0

        if system_info is not None:
            self.frames_max_num =system_info.getFramesMaxNum()#400
            self.videos_fps =system_info.getVideosFps()
        else:
            self.frames_max_num = 400
            self.videos_fps = 20

        self.video_id = 0
        #self.video_name ="video0.avi"
        self.video_name ="{}_{}.avi".format(self.camera_name,time.strftime("%Y%m%d%H%M%S", time.localtime(time.time())))

        #self.video_processer = VideoProcesser()
        #记录每段视频的起始时间,以及结束时间
        self.start_time = datetime.now()
        self.end_time =datetime.now()

        #视频处理任务队列
        self.queue =Queue(maxsize=5)

        # frame的队列
        self.save_frame_queue = Queue(maxsize=100)
        self.play_frame_queue =Queue(maxsize=3)

        print("initialize camera{}:frames_max_num:{},video_fps:{}".format(self.camera_name, self.frames_max_num,
                                                                      self.videos_fps))
    # 退出程序释放摄像头
    def __del__(self):
        self.cap.release()

    def setFramesMaxNumAndFps(self,system_info=None):
        if system_info is not None:
            self.frames_max_num =system_info.getFramesMaxNum()
            self.videos_fps =system_info.getVideosFps()
            print("set camera{}:frames_max_num:{},video_fps:{}".format(self.camera_name, self.frames_max_num,
                                                                              self.videos_fps))
        else:
            self.frames_max_num = 400
            self.videos_fps = 20

    def saveFrameProducer(self,frame,current_datetime):
        '''
        这里是生产者模型
        :param frame:
        :param current_datetime:
        :return:
        '''

        if self.current_frame_num == 0:
            self.start_time = current_datetime

        if self.current_frame_num < self.frames_max_num:
            self.current_frame_num += 1

            #ret, jpeg = cv2.imencode('.jpg', frame)
            if self.out == None:
                #fourcc = cv2.VideoWriter_fourcc(*'MJPG')
                #fourcc = cv2.VideoWriter_fourcc('I', '4', '2', '0')
                #fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
                # 获取摄像头的视频流，然后保存到本地
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                if self.camera_type=="usb":
                    self.out = cv2.VideoWriter('./static/transferStation/{}'.format(self.video_name), fourcc, self.videos_fps,
                                            (640, 480))  #usb摄像头的形状
                elif self.camera_type =="ip":
                    self.out = cv2.VideoWriter('./static/transferStation/{}'.format(self.video_name), fourcc, self.videos_fps,
                                           (1920,1080))   #形状问题啊,又作死了！！！

            self.out.write(frame)

        else:
            # 当前视频结束,记录当前视频结束时间
            self.end_time = current_datetime

            # 前一个视频录制结束,开始向队列中添加该视频的处理任务
            video_info = VideoInfo(video_name=self.video_name, camera_name=self.camera_name,
                                   start_time=self.start_time, end_time=self.end_time)
            self.queue.put(video_info)

            # 这里产生一个新的视频名字
            current_video = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
            self.video_name = "{}_{}.avi".format(self.camera_name,current_video)
            print("video_name:", self.video_name)

            # 当前帧归零,记录视频起始时间
            self.current_frame_num = 0

            # 释放资源，针对下一个视频则再重新生成即可
            if self.out != None:
                self.out.release()
                self.out = None

    def saveFrameQueueProducer(self,thread_name ="save_frame_queue_thread"):
        '''
        这里是生产者模型
        :return:None
        '''
        print(thread_name+"start!")

        while True:
            try:
                frame_info =self.save_frame_queue.get()
                if frame_info:
                    frame =frame_info.getFrame()
                    current_time =frame_info.getCurrentTime()
                    self.saveFrameProducer(frame, current_time)
            except Empty as e:
                print("the frame.queue is empty!,Error:{}".format(e))

    def videoHandler(self,consumer_thread_name):
        while True:
            # #if not self.queue.empty():  #empty不是线程安全的,不能这么写,当queue里面只有一个任务,多个线程同时取任务,总有取不到任务的
            #     #从队列中获取任务
            #     video_info = self.queue.get()
            #     if video_info:
            #        ......
            try:
                #从队列中获取任务
                video_info = self.queue.get()
                if video_info:

                    # 获得相关信息
                    video_name = video_info.getVideoName()
                    camera_name = video_info.getCameraName()
                    start_time = video_info.getStartTime()
                    end_time = video_info.getEndTime()

                    #检查路径下,是否有对应摄像头的,残留的mp4 #这样做会删除到正在读写的视频
                    #self.checkPath(camera_name)

                    # 转换avi视频为h264格式(采用多线程,否则会阻塞主程序,影响主程序存储视频，造成视频段不完全连续！！！)
                    success,output_video_name=self.toH264(video_name,delete_oringinal_video=True)
                    # 转换成功,则存入数据库并删除掉原始视频
                    if success:
                       self.saveToDB(output_video_name, camera_name, start_time,end_time)
                       print("{} consuming {} and saving to database!".format(consumer_thread_name, video_name))

            except Empty:
                   print("queue is empty！")

    def startConsumerThread(self,n=2):
        '''
        :param n: 线程数量
        :return: None
        '''
        #只检查一次,不要在videoHandler中不停的检查（那样会删除到正在读写的视频）
        self.checkPath(self.camera_name)

        print("initialize camera{}:frames_max_num:{},video_fps:{}".format(self.camera_name, self.frames_max_num,
                                                                          self.videos_fps))
        # 开启一定数量的消费者线程
        for i in range(n):
            thread_name ="{}-ConsumerThread-{}".format(self.camera_name,i)
            Thread(target=self.videoHandler, args=(thread_name,)).start()
            print(thread_name + " start!")

class FrameInfo(object):
    '''
    1.获取帧
    2.获取当前时间
    '''
    def __init__(self,frame,current_time):
        super(FrameInfo,self).__init__()
        self.frame =frame
        self.current_time =current_time
    def getFrame(self):
        return self.frame
    def getCurrentTime(self):
        return self.current_time

class VideoManager(VideoCamera,threading.Thread):
    def __init__(self,camera_idx =0,camera_address =None,camera_type ="usb",system_info=None):
        """
        之所以要将类VideoCamera再包装为VideoManager的原因是,
          (1)使用yield需要一个全局的global_frame,也即一个类似全局变量的东西,但是如果声明为全局变量,则对每个摄像头都要声明一个全局变量,不如使用类再包装一下
        　(2)实现对视频存储以及实时播放的统一管理,并且保证,不会同时存在两个camera对象对同一个摄像头调用read方法（考虑到网络摄像头传输也需要带宽,
        　　　对同一个摄像头重复读取数据,也是需要开销的）
        :param cameraIdx:摄像机编号
        :param camera_address：网络摄像头IP地址
        """
        #print("MRO:",self.__class__.mro())

        #threading.Thread.__init__(self)
        super(VideoManager, self).__init__(camera_idx =camera_idx,camera_address =camera_address,camera_type =camera_type,system_info=system_info)

        self.global_frame =None
        #self.video_camera=VideoCamera(camera_idx=camera_idx,camera_address =camera_address)
        self.camera_index =camera_idx
        self.camera_address =camera_address

        #该帧是视频实时播放,以及保存视频时共用的帧
        _, self.frame = self.cap.read()

        self.current_datetime =datetime.now()

        #代表是否是第一次启动
        self.first_flag =True
        #当前摄像机是否播放
        self.is_running =True

    def putTimeOnFrame(self,frame):
        # 颜色,BGR
        text_color = 0, 0, 240
        # 获取当前时间,并视频显示
        week = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        current_time = time.strftime("%Y-%m-%d {} %H:%M:%S".format(week[int(time.strftime("%w"))]),
                                     time.localtime(time.time()))
        cv2.putText(frame, current_time, (50, 50), cv2.FONT_HERSHEY_COMPLEX, 0.7, text_color, 1)
        cv2.putText(frame, "camera{}".format(self.camera_index), (480, 50), cv2.FONT_HERSHEY_COMPLEX, 0.7, text_color,1)
        return frame

    def run(self):
        #先开启avi视频消费者线程等待
        self.startConsumerThread()
        #开启帧消费者线程（同时也是avi视频的生产者）
        Thread(target=self.saveFrameQueueProducer).start()

        # 默认情况下,系统一开始就要开启线程运行就需要保存视频
        n=2
        while self.cap.isOpened() and self.is_running:
                n+=1
                time.sleep(0.01)
                # ret,frame =self.video_camera.cap.read()
                ret, frame = self.cap.read()
                current_datetime = datetime.now()

                #网络IP摄像头有可能出现类似[h264 @ 000001d641122200] error while decoding MB 36 106, bytestream -7
                # h264的传输断流,花屏问题,网上的解决方案包括扩大缓冲区,以及c语言队列比较等方案;
                #我这里采取重新初始化摄像头
                if not ret:
                    if self.camera_type is "ip":
                        print("Something goes wrong with the IPCamera!")
                        st =time.time()

                        #self.cap.release() #这句不能要！！！
                        self.cap =cv2.VideoCapture(self.camera_address)
                        print(self.camera_address)
                        #self.cap.open(self.camera_address)

                        restart,frame = self.cap.read()
                        current_datetime = datetime.now()
                        self.current_datetime =current_datetime

                        if restart:
                           print("Success to reinitialize IPCamera!,time to restart the videocapture:{}s".format(time.time()-st))
                else:

                    if self.camera_type =="usb":
                        frame =self.putTimeOnFrame(frame)

                    self.current_datetime =current_datetime
                    # 之所以共用帧,是因为如果视频实时播放和保存视频是各自取的帧,会导致卡顿
                    #self.frame =frame

                    #采用队列看起来是比上面共用帧更好的方式,但是要注意这里的put是可以阻塞的，
                    #也就是说,当你忘了开启消费者线程的时候,队列满了的时候,代码会阻塞在这里,导致后面的队列里面没有视频
                    #所以在这里不一定是更好的方式！！！
                    # self.save_frame_queue.put(FrameInfo(frame,current_datetime))

                    #因为前端处理视频帧的能力比较有限,所以放入帧的时候抽帧处理,这里也有可能阻塞？？？那怎么办,
                    # 如果还是不想用全局帧self.frame =frame,那么需要判断是否已满
                    if n%3 ==0 and not self.play_frame_queue.full():

                        self.play_frame_queue.put(FrameInfo(frame,current_datetime))

                    # if n % 3 == 0:
                    #     self.frame =frame

                    #调用常规的,一个avi视频,开一个子线程
                    #self.saveFrame(frame,current_datetime)

                    #开启队列+avi视频生产者线程
                    #self.saveFrameProducer(self.frame, self.current_datetime)

                if n is 200:
                    n =0

    # 获取视频流
    def videoStream(self):
        #self.frame是共用的,并且有线程在不断地更新self.frame
        while self.cap.isOpened() and self.is_running:
            #该while true循环,仅仅在调用videoStream时循环

            #time.sleep(0.01) #处理延迟时长至少在0.005秒以上

            #frame =self.frame
            try:
                frame_info =self.play_frame_queue.get()
                if frame_info:
                    frame =frame_info.getFrame()

                    #frame =yolov3_detect(frame)

                    ret, jpeg = cv2.imencode('.jpg',frame)
                    if ret:
                       frame = jpeg.tobytes()
                       # 不断显示每一镇
                       if frame is not None:
                           self.global_frame = frame
                           yield (b'--frame\r\n'
                                  b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
                       else:
                           yield (b'--frame\r\n'
                                  b'Content-Type: image/jpeg\r\n\r\n' + self.global_frame + b'\r\n\r\n')
                    else:
                        #若没有下一帧就无法显示。
                       yield (b'--frame\r\n'
                              b'Content-Type: image/jpeg\r\n\r\n' + self.global_frame + b'\r\n\r\n')

            except Empty as e:
                print("Exception:",e)

    def getVideoPoster(self):
        '''
        每个封面的展示,只传输视频的一帧作为封面
        :return:video_poster
        '''
        is_playing =True

        while self.cap.isOpened() and self.is_running:
            #该while循环,仅仅在调用getVideoPoster时循环
            time.sleep(0.02) #处理延迟时长至少在0.005秒以上

            #frame =self.frame
            try:
                frame_info =self.play_frame_queue.get()
                if frame_info:
                    frame =frame_info.getFrame()
                    ret, jpeg = cv2.imencode('.jpg',frame)

                    if ret and is_playing:
                       frame = jpeg.tobytes()

                       is_playing =False
                       if frame is not None:
                           self.global_frame = frame
                           yield (b'--frame\r\n'
                                  b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
                       else:
                           yield (b'--frame\r\n'
                                  b'Content-Type: image/jpeg\r\n\r\n' + self.global_frame + b'\r\n\r\n')
                    else:
                       yield (b'--frame\r\n'
                              b'Content-Type: image/jpeg\r\n\r\n' + self.global_frame + b'\r\n\r\n')
            except Empty as e:
                print("Exception:",e)


    # #以下方法暂时未调用
    # def startPlay(self):
    #     if self.is_running:
    #         print("正在播放！")
    #     self.is_running =True
    #
    # def stopPlay(self):
    #     if not self.is_running:
    #         print("已经停止播放！")
    #     self.is_running =False

class SystemInfo(object):

   '''
    保存系统信息的类,考虑系统信息存入数据库中
   '''
   def __init__(self,videos_max_num =20,frames_max_num=600,videos_fps =20):
      super(SystemInfo,self).__init__()

      #系统开启的时间
      self.init_time =datetime.now()

      #每个是系统所允许每个摄像头的最大视频数量
      self.videos_max_num =self.clamp(videos_max_num,10,30)

      #每段视频的帧数
      self.frames_max_num =self.clamp(frames_max_num,500,2000)

      #视频的帧率
      self.videos_fps =self.clamp(videos_fps,15,50)

   #夹紧函数,保证系统信息里的内容在一定范围内。
   def clamp(self,value,low,high):
       if value > high:
           value = high
       elif value < low:
           value = low
       return value

   #获取系统开启时间的函数
   def getInitTime(self):

       return self.init_time

   #获取系统信息
   def getVideosMaxNum(self):

       return self.videos_max_num

   def getFramesMaxNum(self):

       return self.frames_max_num

   def getVideosFps(self):

       return self.videos_fps

   #设置系统信息
   def setVideosMaxNum(self,videos_max_num):

       self.videos_max_num =self.clamp(videos_max_num,10,30)

   def setFrameMaxNum(self,frames_max_num):

       self.frames_max_num =self.clamp(frames_max_num,500,2000)

   def setVideosFps(self,videos_fps):

       self.videos_fps =self.clamp(videos_fps,15,50)

   def setSystemInfo(self,videos_max_num =20,frames_max_num=600,videos_fps =20):

       self.setVideosMaxNum(videos_max_num)
       self.setFrameMaxNum(frames_max_num)
       self.setVideosFps(videos_fps)

class CheckUserEmail(object):
    def __init__(self):
        super(CheckUserEmail,self).__init__()

    def checkName(self,user_name):
        '''
        验证用户名是否重名
        :param user_name:用户名
        :return:布尔变量
        '''
        if UserInfo.objects.filter(user_name=user_name).exists():
            return True
        else:
            return False

    def checkEmail(self,user_email):
         '''
         验证邮箱是否重复
         :param user_email:邮箱
         :return:bool变量
         '''
         if UserInfo.objects.filter(user_email=user_email).exists():
             return False
         else:
             return True

    def matchName(self,name_or_email):
        '''
        如果是邮箱,匹配用户名,否则直接返回
        :param name_or_email: 用户名或者邮箱
        :return: None或者用户名
        '''
        if re.match(r'^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$', name_or_email):
            user_object =UserInfo.objects.filter(user_email=name_or_email)
            if user_object.exists():
                return user_object.first().user_name
            else:
                return None
        else:
            return name_or_email

    def checkAdmin(self,user_name):
        '''
        验证用户是否是管理员,不需要验证密码（因为用户名是session中取出来的,没有存密码,且前面已经验证密码）
        :param user_name: 用户名
        :param pass_word: 密码
        :return: 布尔变量
        '''
        user_object =UserInfo.objects.filter(user_name=user_name)
        if user_object.exists() and user_object.first().is_admin:
            return True
        else:
            return False

    def checkNamePassword(self,user_name,pass_word):
        '''
        验证用户名和密码是否对应
        :param user_name:输入的用户名
        :param pass_word:输入的密码
        :return:boolean变量
        '''
        user_object =UserInfo.objects.filter(user_name=user_name)

        if user_object.exists() and user_object.first().user_password == pass_word:
            return True
        else:
            return False

