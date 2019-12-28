
import os

class video_processer():

      def __init__(self,video_path ="/media/lb/学习/最近学习/Django_project/MyVedioSystem/static"):

          self.video_path =video_path

      def toH264(self,video_name ="video.avi"):

          output_name =video_name.replace("avi","mp4")

          origin_video = os.path.join(self.video_path, video_name)

          convert_video = os.path.join(self.video_path, output_name)

          cmdline = "source deactivate&&ffmpeg -i {} -vcodec h264 {}".format(origin_video,convert_video)
          #cmdline = "ffmpeg -i {} {}".format(origin_video, convert_video)

          flag = os.system(cmdline)

          if not flag:

              print("convert successfully!")

          else:

              print("false!")

if __name__ == "__main__":

        processer =video_processer()

        processer.toH264("video0.avi")



# video_path ="/media/lb/学习/最近学习/Django_project/MyVedioSystem/static"
# video_name ="video.avi"
#
# origin_video =os.path.join(video_path,video_name)
#
# convert_video =os.path.join(video_path,"optut_test.mp4")
#
# cmdline ="ffmpeg -i {} -vcodec h264 {}".format(origin_video,convert_video)
#
# flag =os.system(cmdline)
#
# if not flag:
#    print("convert successfully!")
# else:
#     print("false!")
