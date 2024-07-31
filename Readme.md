

本代码库实现视频浓缩功能，将视频不同时间段出现的人物浓缩在较短的时间内。

This code library implements video condensation function, which condenses characters that appear in different time periods of the video in a relatively short amount of time.

1. You need to first obtain "yolov4. weights" and place it in the "./data" folder.

​		Then run:

```bash
python save_model.py
```

​	The "./checkpoints" folder will be generated.

2. run

```
python main.py
```

All intermediate files and final condensed videos will be generated in the "./outputs" folder.








Original video:

<video src="outputs/test.mp4"></video>



demo：（The file is located in the output folder）

```
<video src="outputs/demo_with_boxes.mp4"></video>
```



The first frame of the original video：

![image-20240731145023044](outputs/test_0001.jpg)

The first frame of the new video：

![image-20240731145043638](outputs/demo_0001.jpg)

It is evident that the first frame of the new video contains the following additional targets: person-40 (appearing in frame 227 of the original video), person-43 (appearing in frame 293 of the original video), person-16 (appearing in frame 8 of the original video), person-35 (appearing in frame 207 of the original video), and person-15 (appearing in frame 6 of the original video) with only half of its legs in the upper right corner.
