'''
此文件用于计算轨迹重合度，
'''

from tools import read_or_write_labels

'''
boxes_detect:
比较两个目标框是否有重合的部分
'''
def boxes_detect(box1, box2):
    min_x1, min_y1, max_x1, max_y1 = box1[0], box1[1], box1[0]+box1[2], box1[1]+box1[2]
    min_x2, min_y2, max_x2, max_y2 = box2[0], box2[1], box2[0]+box2[2], box2[1]+box2[2]

    # 没有冲突
    if max_x1<min_x2 or max_y1<min_y2 or min_x1>max_x2 or max_y2 <min_y1:
        return 0     # 没有冲突
    else:
        return 1     # 有冲突


'''
collision_detect:
参数: tra1,tra2为两个target的轨迹； step是步长，即将轨迹tra2提前step帧
意义: 将轨迹tra2的提前step帧后，检测轨迹tra1与tra2是否有轨迹冲突
'''
def collision_detect(tra1, tra2, step):

    k = 0  # k用于记录两个轨迹发生冲突的帧数
    # 分别获取两个target的轨迹
    for index1 in range(len(tra1)):
        if index1 % 5 == 1:
            for index2 in range(len(tra2)):
                if index2 % 5 == 1:
                    # 如果两目标出现在同一帧中，检查是否冲突：
                    if tra1[index1] == (tra2[index2]-step):
                        box1 = [tra1[index1+1], tra1[index1+2], tra1[index1+3], tra1[index1+4]]
                        box2 = [tra2[index2+1], tra2[index2+3], tra2[index2+3], tra2[index2+4]]
                        flag = boxes_detect(box1, box2)
                        if flag == 1:
                            k += 1
    return k

# 获取new_trajectory
def old2new_trajectory(old_trajectory, step):
    tra = old_trajectory
    for index in range(len(tra)):
        if index % 5 == 1:
            tra[index] = tra[index] - step
    return tra

'''
参数threshold代表我们能够容忍的轨迹重合的阈值，
如果我们可以接受两个轨迹只在1帧中有重合，那么阈值可以设置为1；
而如果我们不希望两个轨迹发生任何重合，那么阈值可以设置为0'''
def main(path2, path3, steps_path, threshold):
    # 每次target首次在视频中出现的帧号
    first_frame = []
    # 原视频中每个target的轨迹
    old_trajectorys = []
    # 用于记录每个target的新轨迹，能记录入该列表的轨迹都要经过冲突检测
    new_trajectorys = []
    # 用于记录新轨迹中每个target向前移动了多少帧
    step_lists = []

    old_trajectorys = read_or_write_labels.read(path2)

    for lists in old_trajectorys:
        first_frame.append(lists[1])
        if int(lists[1]) == 1:
            new_trajectorys.append(lists)
            step_lists.append([lists[0], 0])

    # 去除first_frame中的重复元素
    a = dict.fromkeys(first_frame)
    b = list(a.keys())
    first_frame = sorted(b)
    print('\nfirst_frame:')
    print(first_frame)

    total_record = 0    #记录总轨迹重合的总数
    print('\nnew trajectorys:')
    for x in first_frame:
        if x == 1:
            continue
        for old_trajectory in old_trajectorys:
            # 找出所有初始帧为x的轨迹
            if old_trajectory[1] == x:
                if_success = 0  #用于记录是否能够找到不发生冲突的step，如果必然发生冲突，那么取冲突数最少的情况
                step = x - 1
                min_record = [100000, 0]  # min_record记录最少冲突数，以及对应的step，如果冲突不可避免，那就选择冲突最少的情况
                while step:
                    record = 0  # record 是与一条new_trajectory的冲突数
                    record_all = 0  #record_all是与所有new_trajectory冲突数
                    num = 0     #记录与多少轨迹冲突数符合阈值
                    flags = 0   #找到冲突数符合阈值的step时直接跳出

                    # 每一step都要与new_trajectorys中的轨迹挨个比较，观察是否冲突
                    for new_trajectory in new_trajectorys:
                        if flags == 1:  # 如果与前面的new_tra发生冲突，那么不必再与后面的new_tra比较，直接修改step从头开始比较
                            continue
                        record = collision_detect(new_trajectory, old_trajectory, step)
                        record_all += record
                        if record <= threshold: # 冲突数符合阈值，接受
                            num += 1
                            record_all += record
                        else:   # 冲突帧数较多，调整step，跳出循环，继续比较
                            flags = 1  #step不符合要求
                    if num ==  len(new_trajectorys):        # 存在合适的新轨迹
                        new_trajectory = old2new_trajectory(old_trajectory, step)
                        new_trajectorys.append(new_trajectory)
                        step_lists.append([new_trajectory[0], step])
                        print(new_trajectory)
                        print('step = '+ str(step), ', collision_num = '+ str(record_all))
                        if len(new_trajectory)>11:
                            total_record += record_all
                        if_success = 1
                        step = 0
                    else:
                        if min_record[0] > record_all:
                            min_record[0] = record_all
                            min_record[1] = step
                        step -= 1

                # 如果必然发生冲突，那么取冲突数最少的情况
                if if_success == 0:
                    step = min_record[1]
                    print('step = '+ str(step), ', collision_num = '+ str(min_record[0]))
                    new_trajectory = old2new_trajectory(old_trajectory, step)
                    new_trajectorys.append(new_trajectory)
                    if len(new_trajectory) > 11:
                        total_record +=  min_record[0]
                    step_lists.append([new_trajectory[0], step])
                    print(new_trajectory)
    # 输出轨迹总重合数
    print('total_record:', total_record)

    # 输出总检测数
    total_boxes = 0
    for traj in new_trajectorys:
        total_boxes += traj[1]
    print('total boxes:', total_boxes)

    # 过滤掉新轨迹中一些只存在一两帧轨迹的target
    tra = []
    for traj in new_trajectorys:
        if len(traj) > 11:
            tra.append(traj)



    # 将step_lists与new_trajectorys[]对应，滤去轨迹< 11的step
    print('\nstep_lists:')
    print(step_lists)
    steps = []
    for lists in step_lists:
        for traj in tra:
            if lists[0] == traj[0]:
                steps.append(lists[1])
    print(steps)

    f = open(steps_path, 'w+')
    for index in range(len(steps)):
        if index < len(steps) - 1:
            f.write(str(steps[index]) + ',')
        else:
            f.write(str(steps[index]) + '\n')
    f.close()
    print(steps_path + ' are written!')

    # 将new_labels列表中的信息写入labels3_new_trajectorys.txt
    read_or_write_labels.write(path3, tra)


if __name__ == '__main__':

    path1 = './outputs/temp_files/labels1_original.txt'
    path2 = './outputs/temp_files/labels2_old_trajectorys.txt'
    path3 = './outputs/temp_files/labels3-new_trajectorys.txt'
    path4 = './outputs/temp_files/labels4_final.txt'
    steps_path = './outputs/temp_files/steps.txt'

    threshold = 1
    main(path2, path3, steps_path, threshold)