'''
用于检测追踪的目标框是否合理，如果过小或过大就忽略
'''
def main(x, y, w, h, width, height):
    if w < 0:
        x = x + w
        w = -w
    if h < 0:
        y = y + h
        h = -h
    if x < 0:
        x = 0
    if y < 0:
        y = 0
    if x+w >= width:
        w = width-2-x
    if y+h >= height:
        h = height-2-y
    if w > 300 or h > 400 or w < 5 or h < 5:
        return 0,0,0,0
    return x,y,w,h