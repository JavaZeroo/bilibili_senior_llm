"""
安卓控制模块
负责控制安卓模拟器,包括截图、点击等操作
"""
import pygetwindow as gw
from PIL import Image
import numpy as np
import win32gui
import win32ui
import win32con
import ctypes
from typing import Tuple
from src.core.base import AndroidControllerBase
from src.core import config as cfg_loader


class AndroidController(AndroidControllerBase):
    """安卓模拟器控制器 - 负责截图和模拟点击"""
    
    def __init__(self, window_title: str = "BlueStacks App Player"):
        """初始化控制器

        支持通过全局配置覆盖默认截图和二值化设置。如果在 `config.yaml` 中设置
        `screenshot` 字段，本类会自动读取并使用。
        """
        self.window_title = window_title
        self.dpi_scale = 1.0

        # 设置DPI感知
        self._set_dpi_awareness()

        # 尝试从配置读取截图参数
        cfg = cfg_loader.load_config()
        screenshot_cfg = cfg.get("screenshot", {})
        self.crop_ratios = tuple(screenshot_cfg.get("crop_ratios", [0.0, 0.2, 1.0, 0.7]))
        self.bw_threshold = screenshot_cfg.get("bw_threshold", 200)
    
    def _set_dpi_awareness(self):
        """设置DPI感知"""
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Windows 8.1+
        except AttributeError:
            ctypes.windll.user32.SetProcessDPIAware()  # Windows 7
    
    def _get_window_dpi(self, hwnd: int) -> float:
        """
        获取指定窗口的DPI缩放系数
        
        Args:
            hwnd: 窗口句柄
            
        Returns:
            DPI缩放系数
        """
        try:
            dpi = ctypes.windll.user32.GetDpiForWindow(hwnd)
        except AttributeError:
            dpi = ctypes.windll.user32.GetDeviceCaps(win32gui.GetDC(0), 88)
        return dpi / 96.0
    
    def _capture_window(self, hwnd: int) -> Tuple[Image.Image, Tuple[int, int, int, int]]:
        """
        截取窗口内容
        
        Args:
            hwnd: 窗口句柄
            
        Returns:
            (截图, (左, 上, 右, 下)坐标)
        """
        # 获取DPI缩放系数
        self.dpi_scale = self._get_window_dpi(hwnd)
        
        # 获取窗口位置
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        
        # 调整坐标以考虑DPI缩放
        left = int(left * self.dpi_scale)
        top = int(top * self.dpi_scale)
        right = int(right * self.dpi_scale)
        bottom = int(bottom * self.dpi_scale)
        
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
        img = Image.frombuffer(
            "RGB", 
            (bmp_info["bmWidth"], bmp_info["bmHeight"]), 
            bmp_str, 
            "raw", 
            "BGRX", 
            0, 
            1
        )
        
        # 释放资源
        win32gui.DeleteObject(bitmap.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwnd_dc)
        
        return img, (left, top, right, bottom)
    
    def _remove_black_borders(self, img: Image.Image) -> Tuple[Image.Image, Tuple[int, int, int, int]]:
        """
        自动裁剪图像中的黑边
        
        Args:
            img: 输入图像
            
        Returns:
            (裁剪后的图像, (左, 上, 右, 下)相对坐标)
        """
        img_np = np.array(img)
        
        # 检测非黑色区域
        mask = np.any(img_np != [0, 0, 0], axis=-1)
        coords = np.argwhere(mask)
        
        if coords.size == 0:
            return img, (0, 0, img.width, img.height)
        
        # 获取裁剪区域的边界
        y_min, x_min = coords.min(axis=0)
        y_max, x_max = coords.max(axis=0)
        
        # 裁剪图像
        cropped_img = img.crop((x_min, y_min, x_max + 1, y_max + 1))
        return cropped_img, (x_min, y_min, x_max + 1, y_max + 1)
    
    def _crop_image_by_ratio(self, img: Image.Image, crop_ratios: Tuple[float, float, float, float]) -> Tuple[Image.Image, Tuple[int, int, int, int]]:
        """
        根据比例裁剪图像
        
        Args:
            img: 输入图像
            crop_ratios: (左, 上, 右, 下)比例
            
        Returns:
            (裁剪后的图像, (左, 上, 右, 下)相对坐标)
        """
        left_ratio, top_ratio, right_ratio, bottom_ratio = crop_ratios
        
        width, height = img.width, img.height
        left = int(left_ratio * width)
        top = int(top_ratio * height)
        right = int(right_ratio * width)
        bottom = int(bottom_ratio * height)
        
        cropped_img = img.crop((left, top, right, bottom))
        return cropped_img, (left, top, right, bottom)
    
    def _convert_to_black_and_white(self, img: Image.Image, threshold: int = None) -> Image.Image:
        """
        将图像转换为黑白并二值化
        
        Args:
            img: 输入图像
            threshold: 二值化阈值
            
        Returns:
            处理后的图像
        """
        if threshold is None:
            threshold = self.bw_threshold
            
        # 转换为灰度图像
        gray_img = img.convert("L")
        
        # 二值化处理
        binary_img = gray_img.point(lambda x: 255 if x > threshold else 0, mode='1')
        return binary_img.convert("RGB")
    
    def get_screenshot(self, save_debug: bool = False) -> Tuple[Image.Image, Tuple[int, int, int, int]]:
        """
        获取模拟器截图
        
        Args:
            save_debug: 是否保存调试图片
            
        Returns:
            (处理后的截图, (左, 上, 右, 下)绝对坐标)
        """
        # 查找窗口
        window_list = gw.getWindowsWithTitle(self.window_title)
        if not window_list:
            raise Exception(f"未找到窗口: {self.window_title}")
        
        window = window_list[0]
        hwnd = window._hWnd
        
        # 截取窗口
        screenshot, (win_left, win_top, win_right, win_bottom) = self._capture_window(hwnd)
        if save_debug:
            screenshot.save("screenshot.jpg")
        
        # 去除黑边
        no_border_img, (black_left, black_top, black_right, black_bottom) = self._remove_black_borders(screenshot)
        if save_debug:
            no_border_img.save("no_border_img.jpg")
        
        # 按比例裁剪
        final_img, (crop_left, crop_top, crop_right, crop_bottom) = self._crop_image_by_ratio(
            no_border_img, 
            self.crop_ratios
        )
        
        # 转换为黑白
        final_img = self._convert_to_black_and_white(final_img)
        if save_debug:
            final_img.save("final_img.jpg")
        
        # 计算裁剪区域相对于屏幕的绝对坐标
        absolute_left = win_left + black_left + crop_left
        absolute_top = win_top + black_top + crop_top
        absolute_right = win_left + black_left + crop_right
        absolute_bottom = win_top + black_top + crop_bottom
        
        return final_img, (absolute_left, absolute_top, absolute_right, absolute_bottom)
    
    def click(self, x: int, y: int):
        """
        模拟鼠标点击
        
        Args:
            x: 屏幕X坐标
            y: 屏幕Y坐标
        """
        # 设置Windows API函数的参数类型
        SetCursorPos = ctypes.windll.user32.SetCursorPos
        SetCursorPos.argtypes = [ctypes.c_int, ctypes.c_int]
        
        mouse_event = ctypes.windll.user32.mouse_event
        mouse_event.argtypes = [ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong]
        
        # 移动鼠标到指定坐标
        SetCursorPos(x, y)
        
        # 模拟鼠标左键按下和释放
        mouse_event(2, 0, 0, 0, 0)  # 左键按下
        mouse_event(4, 0, 0, 0, 0)  # 左键释放
        
        # 移回原位
        SetCursorPos(0, 0)
    
    def calculate_click_position(self, bbox: list, offset: Tuple[int, int]) -> Tuple[int, int]:
        """
        计算点击位置
        
        Args:
            bbox: OCR识别的文本框坐标 [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            offset: 偏移量 (left, top)
            
        Returns:
            (x, y) 绝对屏幕坐标
        """
        # 计算bbox中心点
        x = (bbox[0][0] + bbox[2][0]) // 2 + offset[0]
        y = (bbox[0][1] + bbox[2][1]) // 2 + offset[1]
        
        return int(x), int(y)
    
    def set_crop_ratios(self, left: float, top: float, right: float, bottom: float):
        """设置截图裁剪比例"""
        self.crop_ratios = (left, top, right, bottom)
    
    def set_bw_threshold(self, threshold: int):
        """设置二值化阈值"""
        self.bw_threshold = threshold
