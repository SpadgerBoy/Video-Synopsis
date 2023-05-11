from tools import change_labels, drow_boxes, generate_background, video_frames as vf
import object_tracker
import get_new_trajectorys
import merge_ROI

if __name__ == '__main__':

    path1 = './outputs/temp_files/labels1_original.txt'
    path2 = './outputs/temp_files/labels2_old_trajectorys.txt'
    path3 = './outputs/temp_files/labels3-new_trajectorys.txt'
    path4 = './outputs/temp_files/labels4_final.txt'

    steps_path = './outputs/temp_files/steps.txt'   #存储新轨迹中的步长

    video_path = './outputs/test.mp4'
    new_video_path = './outputs/demo.mp4'
    new_video_boxes_path = './outputs/demo_with_boxes.mp4'

    background_path = './outputs/temp_files/background.jpg'

    old_frames_path = './outputs/frames/old_frames/'
    old_frames_boxes_path = './outputs/frames/old_frames+boxes/'
    new_frames_path = './outputs/frames/new_frames/'
    new_frames_boxes_path = './outputs/frames/new_frames+boxes/'

    threshold = 1
    '''参数threshold代表我们能够容忍的轨迹重合的阈值，可以手动调整。
    如果我们可以接受两个轨迹只在1帧中有重合，那么阈值可以设置为1；
    而如果我们不希望两个轨迹发生任何重合，那么阈值可以设置为0'''


    # 多目标检测+跟踪，并且生成初始的labels1_original.txt
    object_tracker.main()

    # 将labels1_original.txt转换为labels2_old_trajectorys.txt
    print('转换生成新的标签labels2:')
    change_labels.frame2trajectory(path1, path2)

    # 计算轨迹重合度，把重合度不高的人员集中在一帧图像上，生成新的labels3_new_trajectorys.txt
    print('计算轨迹重合度，把重合度不高的人员集中在一帧图像上:')
    get_new_trajectorys.main(path2, path3, steps_path, threshold)

    # 将labels3_new_trajectorys.txt 转换为新视频所需要的labels4_final.txt
    print('转换生成新的标签labels4:')
    change_labels.trajectory2frame(path3, path4, steps_path)

    # 构建多帧融合的背景视频
    print('生成背景图片:')
    generate_background.main(video_path, background_path)

    # 将原视频分为帧
    vf.video2images(video_path, old_frames_path)

    # 从原始视频中进行特定区域的抠图, 泊松融合,最终形成融合浓缩视频
    print('通过泊松融合将ROI与背景图片融合形成新的帧:')
    merge_ROI.main(old_frames_path, new_frames_path, background_path, path4)

    '''
    画出new_frames中每一帧的检测框，然后合并成视频'''
    # 画出每帧中的目标框
    #drow_boxes.in_new_images(new_frames_path, path4, new_frames_boxes_path)
            # drow_boxes.in_old_images(old_frames_path, path1, old_frames_boxes_path)
    # 将新的帧合并为视频
    #vf.images2video(new_frames_boxes_path, new_video_boxes_path)

    '''
    也可以先将new_frames合并成视频，再画出视频中每一帧的检测框
    这种方式速度更快'''
    # 将新的帧合并为视频
    vf.images2video(new_frames_path, new_video_path)
    # 画出新视频中的每一帧的检测框
    drow_boxes.in_video(new_video_path, path4, new_video_boxes_path)
