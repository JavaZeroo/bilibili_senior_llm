"""
ADB控制器模块
通过adb命令控制安卓设备截图和点击
"""
import subprocess
import tempfile
import os
from typing import Tuple, Optional
from PIL import Image
from src.core.base import AndroidControllerBase
from src.utils.adb_helper import ADBHelper

class ADBController(AndroidControllerBase):
    """通过adb控制安卓设备截图和点击"""
    def __init__(self, adb_path: str = "adb", device_id: Optional[str] = None, config: dict = None, auto_setup: bool = True):
        """
        初始化 ADB 控制器
        
        Args:
            adb_path: ADB 可执行文件路径
            device_id: 设备 ID，None 表示自动选择
            config: 配置字典
            auto_setup: 是否自动设置 ADB 环境（下载、检测设备等）
        """
        # 从 config 中读取截图和二值化设置（如果提供）
        if config is None:
            config = {}
        screenshot_cfg = config.get("screenshot", {})
        self.crop_ratios = tuple(screenshot_cfg.get("crop_ratios", [0.0, 0.2, 1.0, 0.7]))
        self.bw_threshold = screenshot_cfg.get("bw_threshold", 200)
        
        # 如果启用自动设置
        if auto_setup:
            helper = ADBHelper()
            adb_path_resolved, device_id_resolved = helper.ensure_adb_ready(auto_select_device=True)
            
            if adb_path_resolved is None:
                raise RuntimeError("ADB 环境设置失败")
            
            self.adb_path = adb_path_resolved
            self.device_id = device_id_resolved if device_id is None else device_id
        else:
            self.adb_path = adb_path
            self.device_id = device_id

    def _adb_cmd(self, args):
        cmd = [self.adb_path]
        if self.device_id:
            cmd += ["-s", self.device_id]
        cmd += args
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result

    def get_screenshot(self, save_debug: bool = False) -> Tuple[Image.Image, Tuple[int, int, int, int]]:
        """通过adb截图并返回PIL图像和坐标"""
        with tempfile.TemporaryDirectory() as tmpdir:
            remote_path = "/sdcard/screen.png"
            local_path = os.path.join(tmpdir, "screen.png")
            # 截图
            self._adb_cmd(["shell", "screencap", "-p", remote_path])
            # 拉取到本地
            self._adb_cmd(["pull", remote_path, local_path])
            # 删除远程文件
            self._adb_cmd(["shell", "rm", remote_path])
            # 打开图片
            img = Image.open(local_path)
            width, height = img.width, img.height
            # 按比例裁剪
            left_ratio, top_ratio, right_ratio, bottom_ratio = self.crop_ratios
            left = int(left_ratio * width)
            top = int(top_ratio * height)
            right = int(right_ratio * width)
            bottom = int(bottom_ratio * height)
            cropped_img = img.crop((left, top, right, bottom))
            # 二值化
            gray_img = cropped_img.convert("L")
            binary_img = gray_img.point(lambda x: 255 if x > self.bw_threshold else 0, mode='1')
            final_img = binary_img.convert("RGB")
            print(f"{save_debug=}")
            if save_debug:
                final_img.save("adb_final_img.jpg")
            # 返回裁剪区域的绝对坐标
            return final_img, (left, top, right, bottom)

    def click(self, x: int, y: int):
        """通过adb模拟点击"""
        self._adb_cmd(["shell", "input", "tap", str(x), str(y)])

    def calculate_click_position(self, bbox: list, offset: Tuple[int, int]) -> Tuple[int, int]:
        """计算点击位置（OCR bbox中心点 + 裁剪偏移）"""
        x = (bbox[0][0] + bbox[2][0]) // 2 + offset[0]
        y = (bbox[0][1] + bbox[2][1]) // 2 + offset[1]
        return int(x), int(y)

    def set_crop_ratios(self, left: float, top: float, right: float, bottom: float):
        self.crop_ratios = (left, top, right, bottom)

    def set_bw_threshold(self, threshold: int):
        self.bw_threshold = threshold
