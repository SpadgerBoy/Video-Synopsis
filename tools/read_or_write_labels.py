import os
import fileinput
'''
    将列表信息生成labels文件
    参数：path是labels的存放路径，lists是存放labels元素的列表'''
def write(path, lists):
    f = open(path, 'w+')
    for x in lists:
        for index in range(len(x)):
            if index < len(x)-1:
                f.write(str(x[index]) + ',')
            else:
                f.write(str(x[index]) + '\n')
    f.close()
    print(path + ' are written!')

'''
    将文件信息读取生成列表
    参数：path是labels的存放路径'''
def read(path):
    lists = []
    i = 0
    for line in fileinput.input(path):
        lists.append([])
        for x in line.split(","):
            lists[i].append(int(x))
        i += 1
    return lists