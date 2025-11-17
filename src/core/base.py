from abc import ABC, abstractmethod
from typing import Tuple, List
from PIL.Image import Image


class QuestionExtractorBase(ABC):
    """抽象基类：题目提取器"""

    @abstractmethod
    def extract_question(self, image: Image) -> Tuple[str, List]:
        """从图像中提取题目并返回格式化文本和OCR结果"""
        raise NotImplementedError()

    @abstractmethod
    def set_merge_threshold(self, threshold: int):
        """设置文本框合并阈值"""
        raise NotImplementedError()


class AnswerGeneratorBase(ABC):
    """抽象基类：答案生成器（LLM）"""

    @abstractmethod
    def get_answer(self, question_body: str) -> str:
        """根据格式化题目返回LLM的原始答案文本"""
        raise NotImplementedError()

    @abstractmethod
    def extract_option_number(self, answer: str) -> int:
        """从LLM返回文本中提取选项编号"""
        raise NotImplementedError()

    def set_model(self, model: str):
        """可选：更换模型实现"""
        raise NotImplementedError()

    def set_system_prompt(self, prompt: str):
        """可选：设置系统提示词"""
        raise NotImplementedError()


class AndroidControllerBase(ABC):
    """抽象基类：安卓/模拟器控制器"""

    @abstractmethod
    def get_screenshot(self, save_debug: bool = False) -> Tuple[Image, Tuple[int, int, int, int]]:
        """返回处理后的截图和绝对坐标"""
        raise NotImplementedError()

    @abstractmethod
    def click(self, x: int, y: int):
        """在屏幕上模拟一次点击"""
        raise NotImplementedError()

    @abstractmethod
    def calculate_click_position(self, bbox: list, offset: Tuple[int, int]) -> Tuple[int, int]:
        """根据OCR bbox 和偏移量计算点击坐标"""
        raise NotImplementedError()

    def set_crop_ratios(self, left: float, top: float, right: float, bottom: float):
        """可选：设置截图裁剪比例"""
        raise NotImplementedError()

    def set_bw_threshold(self, threshold: int):
        """可选：设置二值化阈值"""
        raise NotImplementedError()
