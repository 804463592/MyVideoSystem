# import time
#
# curr  =time.strftime("%Y-%m-%d calender%w %H:%M:%S",time.localtime(time.time()))
#
# print(curr)
# import


# import sys, os
# import threading
#
#
# class mp4_to_H264():
#     def __init__(self):
#         pass
#
#     def convert_avi(self, input_file, output_file, ffmpeg_exec="ffmpeg"):
#         ffmpeg = '{ffmpeg} -y -i "{infile}" -c:v libx264 -strict -2 "{outfile}"'.format(ffmpeg=ffmpeg_exec,
#                                                                                         infile=input_file,
#                                                                                         outfile=output_file)
#         f = os.popen(ffmpeg)
#         ffmpegresult = f.readline()
#
#         # s = os.stat(output_file)
#         # fsize = s.st_size
#
#         return ffmpegresult
#
#     def convert_avi_to_webm(self, input_file, output_file, ffmpeg_exec="ffmpeg"):
#         return self.convert_avi(input_file, output_file, ffmpeg_exec="ffmpeg")
#
#     def convert_avi_to_mp4(self, input_file, output_file, ffmpeg_exec="ffmpeg"):
#         return self.convert_avi(input_file, output_file, ffmpeg_exec="ffmpeg")
#
#     def convert_to_avcmp4(self, input_file, output_file, ffmpeg_exec="ffmpeg"):
#         email = threading.Thread(target=self.convert_avi, args=(input_file, output_file, ffmpeg_exec,))
#         email.start()
#
#     def convert_byfile(self, from_path, to_path):
#         if not os.path.exists(from_path):
#             print("Sorry, you must create the directory for the output files first")
#         if not os.path.exists(os.path.dirname(to_path)):
#             os.makedirs(os.path.dirname(to_path), exist_ok=True)
#         directory, file_name = os.path.split(from_path)
#         raw_name, extension = os.path.splitext(file_name)
#         print("Converting ", from_path)
#         self.convert_avi_to_mp4(from_path, to_path)
#
#
# a = mp4_to_H264()
# from_path = '/media/lb/学习/最近学习/Django_project/MyVedioSystem/static/videoStorage/realVideo/20191128182516.mp4'
# to_path = '/home/1111.mp4'
# a.convert_byfile(from_path, to_path)

# import os
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

import redis
client =redis.Redis()
print(client.keys("*")[0].decode())

for key in client.keys():
    print(key.decode())

