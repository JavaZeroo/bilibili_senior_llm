import pygetwindow as gw
from PIL import Image
import numpy as np
import win32gui
import win32ui
import win32con
import win32api
import ctypes

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Windows 8.1 及以上版本
except AttributeError:
    ctypes.windll.user32.SetProcessDPIAware()  # 适用于 Windows 7

# 获取窗口 DPI 缩放比例
def get_window_dpi(hwnd):
    """
    获取指定窗口的 DPI 缩放系数
    """
    try:
        # Windows 10 (version 1607) 及更高版本支持 GetDpiForWindow
        dpi = ctypes.windll.user32.GetDpiForWindow(hwnd)
    except AttributeError:
        # 使用系统默认 DPI
        dpi = ctypes.windll.user32.GetDeviceCaps(win32gui.GetDC(0), 88)  # 88 是 LOGPIXELSX 的常量
    return dpi / 96.0

def capture_window(hwnd):
    """
    截取窗口内容，包括边框和标题栏。
    """
    # 获取 DPI 缩放系数
    dpi_scale = get_window_dpi(hwnd)
    
    # 获取窗口的左、上、右、下位置
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    #
    # 调整坐标以考虑 DPI 缩放
    left = int(left * dpi_scale)
    top = int(top * dpi_scale)
    right = int(right * dpi_scale)
    bottom = int(bottom * dpi_scale)
    
    width = right - left
    height = bottom - top

    # 获取窗口设备上下文
    hwnd_dc = win32gui.GetWindowDC(hwnd)
    mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
    save_dc = mfc_dc.CreateCompatibleDC()

    # 创建位图对象
    bitmap = win32ui.CreateBitmap()
    bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
    save_dc.SelectObject(bitmap)

    # 截取整个窗口
    save_dc.BitBlt((0, 0), (width, height), mfc_dc, (0, 0), win32con.SRCCOPY)

    # 保存截图
    bmp_info = bitmap.GetInfo()
    bmp_str = bitmap.GetBitmapBits(True)
    img = Image.frombuffer("RGB", (bmp_info["bmWidth"], bmp_info["bmHeight"]), bmp_str, "raw", "BGRX", 0, 1)

    # 释放资源
    win32gui.DeleteObject(bitmap.GetHandle())
    save_dc.DeleteDC()
    mfc_dc.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwnd_dc)

    return img, (left, top, right, bottom)


def remove_black_borders(img):
    """
    自动裁剪图像中的黑边，并返回裁剪后的图像和相对坐标。
    """
    # 将图像转换为 NumPy 数组
    img_np = np.array(img)
    
    # 检测非黑色区域
    mask = np.any(img_np != [0, 0, 0], axis=-1)
    coords = np.argwhere(mask)
    if coords.size == 0:
        return img, (0, 0, img.width, img.height)  # 如果没有内容，返回原图

    # 获取裁剪区域的边界
    y_min, x_min = coords.min(axis=0)
    y_max, x_max = coords.max(axis=0)

    # 裁剪图像
    cropped_img = img.crop((x_min, y_min, x_max + 1, y_max + 1))
    return cropped_img, (x_min, y_min, x_max + 1, y_max + 1)


def crop_image_by_ratio(img, crop_ratios):
    """
    根据比例裁剪图像。
    """
    left_ratio, top_ratio, right_ratio, bottom_ratio = crop_ratios

    width, height = img.width, img.height
    left = int(left_ratio * width)
    top = int(top_ratio * height)
    right = int(right_ratio * width)
    bottom = int(bottom_ratio * height)

    cropped_img = img.crop((left, top, right, bottom))
    return cropped_img, (left, top, right, bottom)

def convert_to_black_and_white(img, threshold=128):
    """
    将图像转换为黑白，并进行二值化处理。
    """
    # 转换为灰度图像
    gray_img = img.convert("L")
    
    # 二值化处理
    binary_img = gray_img.point(lambda x: 255 if x > threshold else 0, mode='1')
    return binary_img.convert("RGB")

def get_screenshot(titile="BlueStacks App Player"):
    window_list = gw.getWindowsWithTitle(titile)
    if window_list:
        window = window_list[0]
        hwnd = window._hWnd

        # 截取窗口
        screenshot, (win_left, win_top, win_right, win_bottom) = capture_window(hwnd)
        screenshot.save("screenshot.jpg")

        # 第一步：自动去除黑边
        no_border_img, (black_left, black_top, black_right, black_bottom) = remove_black_borders(screenshot)
        no_border_img.save("no_border_img.jpg")

        custom_crop_ratios = (0.0, 0.2, 1.0, 0.7)  # 按比例裁剪 (左, 上, 右, 下)
        final_img, (crop_left, crop_top, crop_right, crop_bottom) = crop_image_by_ratio(no_border_img, custom_crop_ratios)
        final_img = convert_to_black_and_white(final_img, threshold=200)

        # 计算裁剪区域相对于屏幕的绝对坐标
        absolute_left = win_left + black_left + crop_left
        absolute_top = win_top + black_top + crop_top
        absolute_right = win_left + black_left + crop_right
        absolute_bottom = win_top + black_top + crop_bottom
        final_img.save("screensfinal_imghot.jpg")
        return final_img, (absolute_left, absolute_top, absolute_right, absolute_bottom)
        # # 保存最终裁剪后的图像

        # print(f"最终裁剪后的绝对坐标: 左上({absolute_left}, {absolute_top}), 右下({absolute_right}, {absolute_bottom})")

if __name__ == '__main__':
    screenshot, (absolute_left, absolute_top, absolute_right, absolute_bottom) = get_screenshot("BlueStacks App Player")
    screenshot.show()