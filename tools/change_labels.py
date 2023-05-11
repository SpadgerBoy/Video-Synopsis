'''
此文件将原始标签重新组织形成新的标签，即将任务1的labels转换为任务2的labels
'''
import fileinput
from tools import read_or_write_labels

'''
frame2trajectory:用于将labels形式为每frame一行改为每target一行，即将帧改为轨迹'''
def frame2trajectory(old_path, new_path):

    old_labels = []
    new_labels = []
    id_lists = []

    i = 0
    for line in fileinput.input(old_path):
        old_labels.append([])
        for x in line.split(","):
            old_labels[i].append(int(x))
        i += 1

    # 输出总检测数
    total_boxes = 0
    for old_label in old_labels:
        total_boxes += old_label[1]
    print('total_boxes:',total_boxes)

    for i in range(len(old_labels)):
        for j in range(len(old_labels[i])):

            if j % 5 == 2:
                id = old_labels[i][j]  # track_id

                flag = -1
                for id_index in range(len(id_lists)):
                    if id == id_lists[id_index]:
                        flag = id_index

                if flag == -1:  # 每出现一个新的id增加一个新的列
                    id_lists.append(id)
                    new_labels.append([])
                    new_labels[len(id_lists) - 1].append(id)
                    new_labels[flag].extend((old_labels[i][0], old_labels[i][j + 1], old_labels[i][j + 2],
                                             old_labels[i][j + 3], old_labels[i][j + 4]))
                else:
                    new_labels[flag].extend((old_labels[i][0], old_labels[i][j + 1], old_labels[i][j + 2],
                                             old_labels[i][j + 3], old_labels[i][j + 4]))

    # 将new_labels列表中的信息写入labels.txt
    read_or_write_labels.write(new_path, new_labels)

'''
trajectory2frame(: 用于将labels形式为每target一行改为每frame一行，即将轨迹改为帧'''
def trajectory2frame(old_path, new_path, steps_path):

    old_labels = []
    new_labels = []
    frame_lists = []
    step_lists = []

    i = 0
    for line in fileinput.input(steps_path):
        for x in line.split(","):
            step_lists.append(int(x))
        i += 1

    i = 0
    for line in fileinput.input(old_path):
        old_labels.append([])
        for x in line.split(","):
            old_labels[i].append(int(x))
        i += 1


    for i in range(len(old_labels)):
        for j in range(len(old_labels[i])):

            if j % 5 == 1:
                frame = old_labels[i][j]  # 帧号

                flag = -1
                for index in range(len(frame_lists)):
                    if frame == frame_lists[index]:
                        flag = index

                if flag == -1:  # 每出现一个新的frame增加一个新的列
                    frame_lists.append(frame)
                    new_labels.append([])
                    new_labels[len(frame_lists) - 1].append(frame)
                    new_labels[flag].extend((old_labels[i][j] + step_lists[i], old_labels[i][0],
                                             old_labels[i][j + 1], old_labels[i][j + 2],
                                             old_labels[i][j + 3], old_labels[i][j + 4]))
                else:
                    new_labels[flag].extend((old_labels[i][j] + step_lists[i], old_labels[i][0],
                                             old_labels[i][j + 1], old_labels[i][j + 2],
                                             old_labels[i][j + 3], old_labels[i][j + 4]))

    # 输出正确检测数
    correct_boxes = 0
    for list in new_labels:
        target_num = len(list) // 6
        correct_boxes += target_num
        list.insert(1, target_num)
    print('correct_boxes:', correct_boxes)

    # 将new_labels列表中的信息写入labels.txt
    read_or_write_labels.write(new_path, new_labels)

if __name__ == '__main__':

    old_path = '../outputs/temp_files/labels1_original.txt'
    new_path = '../outputs/temp_files/labels2_old_trajectorys.txt'
    frame2trajectory(old_path, new_path)

    old_path = './outputs/labels3-new_trajectorys.txt'
    new_path = './outputs/labels4_final.txt'
    # trajectory2frame(old_path, new_path, steps)
