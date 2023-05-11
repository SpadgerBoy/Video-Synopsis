
'''
用于视频——图片，以及图片——视频的转换
'''
import os
import cv2
from PIL import Image

# 将视频的每一帧保存为图片
def video2images(video_path, frames_path):
    # 逐帧读取图片
    cap = cv2.VideoCapture(video_path)
    frame_num = 0
    while True:
        ret, frame = cap.read()
        if ret:
            pass
        else:
            break
        frame_num += 1
        frame_name = str(frame_num).zfill(5)
        cv2.imwrite(frames_path + frame_name + '.jpg', frame)

# 将多张图片合成为视频
def images2video(image_path, video_path):

    # 获取图片路径下面的所有图片名称
    image_names = os.listdir(image_path)
    # 对提取到的图片名称进行排序
    image_names.sort(key=lambda n: int(n[:-4]))
    # 设置写入格式
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    # 设置每秒帧数
    fps = 30
    # 读取第一个图片获取大小尺寸，因为需要转换成视频的图片大小尺寸是一样的
    image = Image.open(image_path + image_names[0])
    # 初始化媒体写入对象
    videowriter = cv2.VideoWriter(video_path, fourcc, fps, image.size)
    # 遍历图片，将每张图片加入视频当中
    for index in range(len(image_names)):
        image_name = image_names[index]
        img = cv2.imread(os.path.join(image_path, image_name))
        videowriter.write(img)
        print('已合并 : ' + str(index) + '/' + str(len(image_names)))
    # 释放媒体写入对象
    videowriter.release()
    print('视频合并完成！')
