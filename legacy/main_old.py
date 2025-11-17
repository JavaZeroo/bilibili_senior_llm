from paddleocr import PaddleOCR
import numpy as np
from cap import get_screenshot
from llm import get_ans
import ctypes
import time


# 加载 OCR 模型
ocr = PaddleOCR(
    use_angle_cls=True,
    lang="ch",
    det_model_dir="det_model_dir",
    rec_model_dir="rec_model_dir",
    cls_model_dir="cls_model_dir",
)

def is_close(bbox1, bbox2, threshold=10):
    """
    判断两个 bbox 是否垂直方向上足够接近，可以合并。
    bbox 格式：[[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
    """
    # 计算 bbox 的上下边界
    top1, bottom1 = min(bbox1[0][1], bbox1[1][1]), max(bbox1[2][1], bbox1[3][1])
    top2, bottom2 = min(bbox2[0][1], bbox2[1][1]), max(bbox2[2][1], bbox2[3][1])
    
    # 计算两个 bbox 的垂直距离
    if bottom1 < top2:
        vertical_distance = top2 - bottom1
    elif bottom2 < top1:
        vertical_distance = top1 - bottom2
    else:
        vertical_distance = 0  # 重叠的情况
    return vertical_distance < threshold

def merge_boxes(box1, box2):
    """
    合并两个 bbox，返回合并后的 bbox。
    """
    x_coords = [point[0] for point in box1 + box2]
    y_coords = [point[1] for point in box1 + box2]
    
    merged_box = [
        [min(x_coords), min(y_coords)],
        [max(x_coords), min(y_coords)],
        [max(x_coords), max(y_coords)],
        [min(x_coords), max(y_coords)]
    ]
    return merged_box

def merge_ocr_results(results, threshold=20):
    """
    根据 bbox 的距离合并 OCR 结果。
    """
    merged_results = []
    current_box, current_text = results[0][0], results[0][1][0]

    for i in range(1, len(results)):
        bbox, text = results[i][0], results[i][1][0]

        # 检查当前 bbox 是否与下一个 bbox 接近
        if is_close(current_box, bbox, threshold):
            # 如果接近，则合并文本和 bbox
            current_text += text
            current_box = merge_boxes(current_box, bbox)
        else:
            # 如果不接近，则将当前结果保存，并更新为新的 bbox 和文本
            merged_results.append((current_box, current_text))
            current_box, current_text = bbox, text

    # 添加最后一个结果
    merged_results.append((current_box, current_text))
    return merged_results

while True:
    screenshot, (absolute_left, absolute_top, absolute_right, absolute_bottom) = get_screenshot("BlueStacks App Player")
    img_array = np.array(
        screenshot
    )  # 还记得上面截图得到的 screenshot 嘛，在这里被转化成了 numpy 数组
    result = ocr.ocr(img_array)  # OCR 识别
    result = merge_ocr_results(result[0])
    # print(result)
    questionBody = ""
    for idx, line in enumerate(result):
        text = line[1]
        if idx == 0:
            questionBody += f"<Question>{text}"
        else:
            boxes = line[0]
            questionBody += f"\n<Option>{str(idx)}. {text}"
    print(questionBody)
    final_selection = int(get_ans(questionBody).content.split(".")[0][-1])
    # final_selection = 4
    print(f"最终选择: {final_selection}")

    def get_click_position(selection):
        """
        根据选择题选项，返回点击位置。
        """
        # 选项相对位置
        select_rel_pos = result[selection][0]
        x = (select_rel_pos[0][0] + select_rel_pos[2][0]) // 2 + absolute_left
        y = (select_rel_pos[0][1] + select_rel_pos[2][1]) // 2 + absolute_top
        
        return int(x), int(y)

    click_x, click_y = get_click_position(final_selection)

    print(f"点击位置: ({click_x}, {click_y})")

    # 设置 Windows API 函数的参数类型
    SetCursorPos = ctypes.windll.user32.SetCursorPos
    SetCursorPos.argtypes = [ctypes.c_int, ctypes.c_int]

    mouse_event = ctypes.windll.user32.mouse_event
    mouse_event.argtypes = [ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong]

    def click(x, y):
        """
        模拟鼠标在屏幕上的点击
        """
        # 移动鼠标到指定坐标 (x, y)
        SetCursorPos(x, y)
        
        # 模拟鼠标左键按下和释放
        mouse_event(2, 0, 0, 0, 0)  # 左键按下
        mouse_event(4, 0, 0, 0, 0)  # 左键释放
        
        SetCursorPos(0, 0)

        
    click(click_x, click_y)
    time.sleep(1.5)
