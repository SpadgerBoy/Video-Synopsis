
'''
用于生成视频背景图
'''

import cv2
import numpy as np

def main(video_path, background_path):

    cap = cv2.VideoCapture(video_path)
    ret, privous_frames = cap.read()
    for i in range(300):
        ret, frame = cap.read()
        dst = cv2.addWeighted(frame, 1/(i+1), privous_frames, i/(i+1), 0)
        cv2.imwrite(background_path, dst)
        privous_frames = dst
        print('视频背景生成中: 已完成%.2f %%' % ((i+1)/3))

if __name__ == '__main__':
    video_path = './output/test.mp4'
    background_path = '../outputs/temp_files/background.jpg'

    main(video_path, background_path)
