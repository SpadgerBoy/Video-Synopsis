
import cv2
import numpy as np
from tools import filter_box, read_or_write_labels


# 取出每一帧的ROI，并通过泊松融合到背景图中
def main(old_frames_path, new_frames_path, background_path, labels_path):

    labels = read_or_write_labels.read(labels_path)

    #读取背景图片
    background = cv2.imread(background_path)

    print('视频共' + str(len(labels)) + '帧：')

    for label in labels:
        print('merge ROI : ' + str(label[0]) + '/' + str(len(labels)))
        exist_flag = 0
        for index in range(len(label)):
            if index % 6 == 2 :
                frame_num = str(label[index]).zfill(5)
                frame_name = str(label[0]).zfill(5)
                img_path = old_frames_path + frame_num + '.jpg'
                img = cv2.imread(img_path)

                id, x, y, w, h = label[index + 1], label[index + 2], label[index + 3], label[index + 4], label[
                    index + 5]
                # mask
                img_mask = np.zeros(img.shape, img.dtype)
                poly = np.array([[x, y], [x + w, y], [x + w, y + h], [x, y + h]], np.int32)
                cv2.fillPoly(img_mask, [poly], (255, 255, 255))

                center = (int((2 * x + w) / 2), int((2 * y + h) / 2))

                # 泊松融合.
                if exist_flag == 0:  # cv2.NORMAL_CLONE, cv2.MIXED_CLONE
                    output = cv2.seamlessClone(img, background, img_mask, center, cv2.NORMAL_CLONE)
                    cv2.imwrite(new_frames_path + frame_name + '.jpg', output)
                    exist_flag = 1

                if exist_flag == 1:
                    dst = cv2.imread(new_frames_path + frame_name + '.jpg')
                    output = cv2.seamlessClone(img, dst, img_mask, center, cv2.NORMAL_CLONE)
                    cv2.imwrite(new_frames_path + frame_name + '.jpg', output)


if __name__ == '__main__':
    background_path = './outputs/temp_files/background.jpg'
    labels_path = './outputs/temp_files/labels4_final.txt'
    old_frames_path = './outputs/frames/old_frames/'
    new_frames_path = './outputs/frames/new_frames/'

    main(old_frames_path, new_frames_path, background_path, labels_path)

