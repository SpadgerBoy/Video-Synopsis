import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import time
import tensorflow as tf

import core.utils as utils
from tensorflow.python.saved_model import tag_constants
from core.config import cfg
from PIL import Image
import cv2
import numpy as np
import matplotlib.pyplot as plt

# deep sort imports
from deep_sort import preprocessing, nn_matching
from deep_sort.detection import Detection
from deep_sort.tracker import Tracker
from tools import generate_detections as gdet, filter_box, read_or_write_labels


def main():
    framework = 'tf'
    weight = './checkpoints/yolov4-416'
    input_size = 416
    model = 'yolov4'
    video_path = './outputs/test.mp4'
    outputs = './outputs/temp_files/detect.avi'
    label_path = './outputs/temp_files/labels1_original.txt'
    tiny = False
    output_format = 'XVID'
    iou = 0.45
    score = 0.50

    # Definition of the parameters
    max_cosine_distance = 0.4
    nn_budget = None
    nms_max_overlap = 1.0
    
    # initialize deep sort
    model_filename = 'model_data/mars-small128.pb'
    encoder = gdet.create_box_encoder(model_filename, batch_size=1)
    # calculate cosine distance metric
    metric = nn_matching.NearestNeighborDistanceMetric("cosine", max_cosine_distance, nn_budget)
    # initialize tracker
    tracker = Tracker(metric)


    # load tf model if flag is set
    saved_model_loaded = tf.saved_model.load(weight, tags=[tag_constants.SERVING])
    infer = saved_model_loaded.signatures['serving_default']

    # begin video capture
    vid = cv2.VideoCapture(video_path)

    out = None
    # get video ready to save locally
    if outputs:
        # by default VideoCapture returns float instead of int
        width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(width, height)
        fps = int(vid.get(cv2.CAP_PROP_FPS))
        codec = cv2.VideoWriter_fourcc(*output_format)
        out = cv2.VideoWriter(outputs, codec, fps, (width, height))

    frame_num = 0
    labels = [] # 用于存放label
    # while video is running
    while True:
        return_value, frame = vid.read()
        if return_value:
            labels.append([])
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame)
        else:
            print('Video has ended !')
            break
        frame_num +=1
        print('Frame #: ', frame_num)
        frame_size = frame.shape[:2]    # w,h
        image_data = cv2.resize(frame, (input_size, input_size))
        image_data = image_data / 255.
        image_data = image_data[np.newaxis, ...].astype(np.float32)
        start_time = time.time()

        # run detections on tflite if flag is set

        batch_data = tf.constant(image_data)
        pred_bbox = infer(batch_data)
        for key, value in pred_bbox.items():
            boxes = value[:, :, 0:4]
            pred_conf = value[:, :, 4:]

        boxes, scores, classes, valid_detections = tf.image.combined_non_max_suppression(
            boxes=tf.reshape(boxes, (tf.shape(boxes)[0], -1, 1, 4)),
            scores=tf.reshape(
                pred_conf, (tf.shape(pred_conf)[0], -1, tf.shape(pred_conf)[-1])),
            max_output_size_per_class=50,
            max_total_size=50,
            iou_threshold=iou,
            score_threshold=score
        )

        # convert data to numpy arrays and slice out unused elements
        # 将数据转换为numpy数组并分割出未使用的元素
        num_objects = valid_detections.numpy()[0]
        bboxes = boxes.numpy()[0]
        bboxes = bboxes[0:int(num_objects)]
        scores = scores.numpy()[0]
        scores = scores[0:int(num_objects)]
        classes = classes.numpy()[0]
        classes = classes[0:int(num_objects)]

        #  格式化边界框: format bounding boxes from normalized ymin, xmin, ymax, xmax ---> xmin, ymin, width, height
        original_h, original_w, _ = frame.shape
        bboxes = utils.format_boxes(bboxes, original_h, original_w)

        # store all predictions in one parameter for simplicity when calling functions
        # 在调用函数时，为了简单起见，将所有预测存储在一个参数中
        pred_bbox = [bboxes, scores, classes, num_objects]

        # read in all class names from config
        class_names = utils.read_class_names(cfg.YOLO.CLASSES)

        # by default allow all classes in .names file
        # 默认情况下，允许.names文件中的所有类
        allowed_classes = list(class_names.values())
        
        # custom allowed classes (uncomment line below to customize tracker for only people)
        allowed_classes = ['person']

        # loop through objects and use class index to get class name, allow only classes in allowed_classes list
        # 循环遍历对象并使用类索引获取类名，只允许allowed_classes列表中的类
        names = []
        deleted_indx = []
        for i in range(num_objects):
            class_indx = int(classes[i])
            class_name = class_names[class_indx]
            if class_name not in allowed_classes:
                deleted_indx.append(i)
            else:
                names.append(class_name)
        names = np.array(names)

        # delete detections that are not in allowed_classes
        # 删除不在allowed_classes中的检测
        bboxes = np.delete(bboxes, deleted_indx, axis=0)
        scores = np.delete(scores, deleted_indx, axis=0)

        # encode yolo detections and feed to tracker
        # 对yolo检测进行编码并反馈给跟踪器
        features = encoder(frame, bboxes)
        detections = [Detection(bbox, score, class_name, feature) for bbox, score, class_name, feature in zip(bboxes, scores, names, features)]

        #initialize color map 初始化颜色映射
        cmap = plt.get_cmap('tab20b')
        colors = [cmap(i)[:3] for i in np.linspace(0, 1, 20)]

        # run non-maxima supression 运行非最大值抑制
        boxs = np.array([d.tlwh for d in detections])
        scores = np.array([d.confidence for d in detections])
        classes = np.array([d.class_name for d in detections])
        indices = preprocessing.non_max_suppression(boxs, classes, nms_max_overlap, scores)
        detections = [detections[i] for i in indices]       

        # Call the tracker
        tracker.predict()
        tracker.update(detections)

        labels[frame_num-1].append(frame_num)    # 向labels中写入帧号
        # update tracks
        for track in tracker.tracks:
            # 前两帧的轨迹被忽略
            #if not track.is_confirmed() or track.time_since_update > 1:
                # continue
            bbox = track.to_tlbr()
            class_name = track.get_class()

            # draw bbox on screen
            color = colors[int(track.track_id) % len(colors)]
            color = [i * 255 for i in color]
            # 目标框
            cv2.rectangle(frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), color, 2)
            # 目标类别框，-1为填充整个框
            cv2.rectangle(frame, (int(bbox[0]), int(bbox[1]-30)),
                          (int(bbox[0])+(len(class_name)+len(str(track.track_id)))*17, int(bbox[1])), color, -1)
            cv2.putText(frame, class_name + "-" + str(track.track_id),(int(bbox[0]), int(bbox[1]-10)),0, 0.75, (255,255,255),2)

            x, y, w, h = int(bbox[0]), int(bbox[1]), int(bbox[2]) - int(bbox[0]), int(bbox[3]) - int(bbox[1])
            x,y,w,h = filter_box.main(x, y, w, h, width, height)
            if w >= 0 and h >= 0:
                labels[frame_num-1].extend([track.track_id, x, y, w, h])    # 向labels中写入当前帧中目标信息(n,x,y,w,h)

        # calculate frames per second of running detections
        fps = 1.0 / (time.time() - start_time)
        print("FPS: %.2f" % fps)
        result = np.asarray(frame)
        result = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # save video file
        out.write(result)

    # 该帧中的目标数
    for x in labels:
        target_num = len(x) // 5
        x.insert(1, target_num)

    # 将列表labels中的信息写入labels.txt
    read_or_write_labels.write(label_path, labels)


if __name__ == '__main__':
    main()

