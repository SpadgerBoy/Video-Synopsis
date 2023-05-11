import os
import cv2
import numpy as np
from tools import filter_box
from PIL import Image
import fileinput
from tools import read_or_write_labels
'''
根据labels在视频中画boxes
'''
def in_video(video_path, labels_path, output_path):

    # 读取labels
    '''labels = []
    i = 0
    for line in fileinput.input(labels_path):
        labels.append([])
        for x in line.split(","):
            labels[i].append(int(x))
        i += 1'''

    labels = read_or_write_labels.read(labels_path)

    vid = cv2.VideoCapture(video_path)

    width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(vid.get(cv2.CAP_PROP_FPS))
    codec = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, codec, fps, (width, height))

    frame_num=0
    while True:
        ret, frame = vid.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame)
        else:
            print('目标框标注完成！.')
            break

        frame_num += 1
        print('已标注：'+ str(frame_num) + '帧')
        for label in labels:
            if label[0] == frame_num:
                # print(frame_num)
                for index in range(len(label)):
                    if index % 6 == 2 :
                        id,x,y,w,h = label[index+1], label[index+2], label[index+3], label[index+4], label[index+5]
                        x, y, w, h = filter_box.main(x, y, w, h, width, height)
                        if w > 0 and h > 0:
                            # print(x, y, x + w, y + h)
                            # 目标框
                            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                            # 目标类别框，-1为填充整个框
                            cv2.rectangle(frame, (x, y - 30), (x + (len('person') + len(str(id))) * 17, y), (255, 0, 0),-1)
                            cv2.putText(frame, "person-" + str(id), (x, y - 10), 0, 0.75, (255, 255, 255), 2)

                result = np.asarray(frame)
                result = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                out.write(result)

'''
根据labels在图片上画boxes
'''
def in_new_images(imgs_path, labels_path, output_path):

    # 读取labels
    labels = []
    i = 0
    for line in fileinput.input(labels_path):
        labels.append([])
        for x in line.split(","):
            labels[i].append(int(x))
        i += 1

    # 获取所有图片
    images_list = []
    filenames = os.listdir(imgs_path)
    for filename in filenames:
        a = os.path.join(imgs_path, filename)
        images_list.append(a)

    img_num = 0
    for image in images_list:
        img = cv2.imread(image)
        height, width, _ = img.shape
        img_num += 1
        for label in labels:
            if label[0] == img_num:
                for index in range(len(label)):
                    if index % 6 == 2:
                        id, x, y, w, h = label[index + 1], label[index + 2], label[index + 3], label[index + 4], label[
                            index + 5]
                        x, y, w, h = filter_box.main(x, y, w, h, width, height)
                        if w > 0 and h > 0:
                            # print(x, y, x + w, y + h)
                            # 目标框
                            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
                            # 目标类别框，-1为填充整个框
                            cv2.rectangle(img, (x, y - 30), (x + (len('person') + len(str(id))) * 17, y), (255, 0, 0),
                                          -1)
                            cv2.putText(img, "person-" + str(id), (x, y - 10), 0, 0.75, (255, 255, 255), 2)

            new_img_path = output_path + "/" + filenames[img_num-1]
            cv2.imwrite(new_img_path, img)

def in_old_images(imgs_path, labels_path, output_path):

    # 读取labels
    labels = read_or_write_labels.read(labels_path)

    # 获取所有图片
    images_list = []
    filenames = os.listdir(imgs_path)
    for filename in filenames:
        a = os.path.join(imgs_path, filename)
        images_list.append(a)

    img_num = 0
    for image in images_list:
        img = cv2.imread(image)
        height, width, _ = img.shape
        img_num += 1
        for label in labels:
            if label[0] == img_num:
                for index in range(len(label)):
                    if index % 5 == 2:
                        id, x, y, w, h = label[index], label[index + 1], label[index + 2], label[index + 3], label[index + 4]
                        x, y, w, h = filter_box.main(x, y, w, h, width, height)
                        if w > 0 and h > 0:
                            # print(x, y, x + w, y + h)
                            # 目标框
                            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
                            # 目标类别框，-1为填充整个框
                            cv2.rectangle(img, (x, y - 30), (x + (len('person') + len(str(id))) * 17, y), (255, 0, 0),-1)
                            cv2.putText(img, "person-" + str(id), (x, y - 10), 0, 0.75, (255, 255, 255), 2)

            new_img_path = output_path + "/" + filenames[img_num-1]
            cv2.imwrite(new_img_path, img)

