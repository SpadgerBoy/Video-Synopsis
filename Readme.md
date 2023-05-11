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

Function preview can be found in the "./outputs" folder.

<video src="./outputs/1-test.mp4"></video>
<video src="./outputs/3-demo_with_boxes.mp4"></video>
