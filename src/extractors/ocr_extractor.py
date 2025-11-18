"""
题目获取模块
负责从图像中提取题目和选项
"""
from paddleocr import PaddleOCR
import numpy as np
from typing import List, Sequence, Tuple, Union
from PIL import Image
from src.core.base import QuestionExtractorBase


class QuestionExtractor(QuestionExtractorBase):
    """题目提取器 - 使用OCR技术从截图中提取题目和选项"""
    
    def __init__(self, ocr_version: str = "PP-OCRv4"):
        """
        初始化OCR模型
        
        Args:
            ocr_version: 使用的PPOCR模型版本 (如 "PP-OCRv3" / "PP-OCRv4")
        """
        self.ocr = PaddleOCR(
            use_angle_cls=True,
            lang="ch",
            ocr_version=ocr_version,
        )
        self.merge_threshold = 20  # 合并文本框的距离阈值
    
    def extract_question(self, image: Image.Image) -> Tuple[str, List]:
        """
        从图像中提取题目和选项
        
        Args:
            image: PIL图像对象
            
        Returns:
            (question_body, ocr_results): 格式化的题目文本和OCR原始结果
        """
        # 转换为numpy数组
        img_array = np.array(image)
        
        # OCR识别
        result = self.ocr.ocr(img_array, det=True, rec=True, cls=True)

        # 合并相近的文本框
        normalized_results = self._normalize_ocr_results(result)
        merged_results = self._merge_ocr_results(normalized_results)
        
        # 格式化题目
        question_body = self._format_question(merged_results)
        
        return question_body, merged_results
    
    def _is_close(self, bbox1: List, bbox2: List, threshold: int = None) -> bool:
        """
        判断两个bbox是否垂直方向上足够接近，可以合并
        
        Args:
            bbox1: 第一个文本框坐标 [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            bbox2: 第二个文本框坐标
            threshold: 距离阈值
            
        Returns:
            是否可以合并
        """
        if threshold is None:
            threshold = self.merge_threshold
            
        # 计算bbox的上下边界
        top1 = min(bbox1[0][1], bbox1[1][1])
        bottom1 = max(bbox1[2][1], bbox1[3][1])
        top2 = min(bbox2[0][1], bbox2[1][1])
        bottom2 = max(bbox2[2][1], bbox2[3][1])
        
        # 计算两个bbox的垂直距离
        if bottom1 < top2:
            vertical_distance = top2 - bottom1
        elif bottom2 < top1:
            vertical_distance = top1 - bottom2
        else:
            vertical_distance = 0  # 重叠的情况
            
        return vertical_distance < threshold
    
    def _merge_boxes(self, box1: List, box2: List) -> List:
        """
        合并两个bbox，返回合并后的bbox
        
        Args:
            box1: 第一个文本框坐标
            box2: 第二个文本框坐标
            
        Returns:
            合并后的文本框坐标
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
    
    def _merge_ocr_results(self, results: List, threshold: int = None) -> List:
        """
        根据bbox的距离合并OCR结果
        
        Args:
            results: OCR原始结果
            threshold: 合并阈值
            
        Returns:
            合并后的结果列表
        """
        if not results or len(results) == 0:
            return []
            
        if threshold is None:
            threshold = self.merge_threshold
            
        merged_results = []
        current_box, current_text = results[0][0], results[0][1]

        for i in range(1, len(results)):
            bbox, text = results[i][0], results[i][1]
            
            # 检查当前bbox是否与下一个bbox接近
            if self._is_close(current_box, bbox, threshold):
                # 如果接近，则合并文本和bbox
                current_text += text
                current_box = self._merge_boxes(current_box, bbox)
            else:
                # 如果不接近，则将当前结果保存，并更新为新的bbox和文本
                merged_results.append((current_box, current_text))
                current_box, current_text = bbox, text
        
        # 添加最后一个结果
        merged_results.append((current_box, current_text))
        return merged_results
    
    def _format_question(self, merged_results: List) -> str:
        """
        将OCR结果格式化为题目文本
        
        Args:
            merged_results: 合并后的OCR结果
            
        Returns:
            格式化的题目字符串
        """
        if not merged_results:
            return ""
            
        question_body = ""
        for idx, line in enumerate(merged_results):
            text = line[1]
            if idx == 0:
                question_body += f"<Question>{text}"
            else:
                question_body += f"\n<Option>{str(idx)}. {text}"
        
        return question_body
    
    def set_merge_threshold(self, threshold: int):
        """设置文本框合并的距离阈值"""
        self.merge_threshold = threshold

    def _normalize_ocr_results(self, result: Union[List, Tuple]) -> List[Tuple[List, str]]:
        """兼容PaddleOCR 2.x与3.x的返回结果格式。

        PaddleOCR 2.x 返回 [[(bbox, (text, score)), ...]]
        PaddleOCR 3.x 返回 [[{'text': str, 'confidence': float, 'text_region': [...]}]] 或类似结构。
        该方法将其统一为 [(bbox, text)] 的形式，方便后续合并。
        """

        if not result:
            return []

        # PaddleOCR通常会为每张图像返回一个列表
        if isinstance(result, (list, tuple)) and result:
            first_entry = result[0]
            if isinstance(first_entry, (list, tuple)):
                candidate: Sequence = first_entry
            else:
                candidate = result
        else:
            candidate = []

        normalized: List[Tuple[List, str]] = []

        for item in candidate:
            bbox: List = []
            text: str = ""

            if isinstance(item, (list, tuple)):
                # 旧格式 (bbox, (text, score))
                bbox = item[0]
                if isinstance(item[1], (list, tuple)):
                    text = item[1][0]
                else:
                    text = str(item[1])
            elif isinstance(item, dict):
                bbox = item.get("text_region") or item.get("points") or item.get("bbox")
                text = item.get("text") or item.get("transcription") or ""
            else:
                continue

            if bbox and text is not None:
                normalized.append((bbox, text))

        return normalized
