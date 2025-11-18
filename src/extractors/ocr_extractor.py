"""
题目获取模块
负责从图像中提取题目和选项
"""
from paddleocr import PaddleOCR
import numpy as np
from typing import List, Tuple, Union
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
            lang="ch",
            use_doc_orientation_classify=False, 
            use_doc_unwarping=False, 
            use_textline_orientation=False,
            ocr_version=ocr_version
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
        result = self.ocr.predict(img_array)
        
        for res in result:
            res.print()
            res.save_to_img("output")
            res.save_to_json("output")

        # 合并相近的文本框
        normalized_results = self._normalize_ocr_results(result)
        
        print(f"Normalized OCR Results: {normalized_results}")
        
        # 按Y坐标排序并合并同一行的文本
        sorted_results = self._sort_and_merge_lines(normalized_results)
        
        print(f"Sorted and Merged by Line: {sorted_results}")
        
        # 过滤选项标记并分离题目和选项
        filtered_results = self._filter_and_classify(sorted_results)
        
        print(f"Filtered Results: {filtered_results}")
        
        # 格式化题目
        question_body = self._format_question_v2(filtered_results)
        
        # 转换为兼容格式：[题目, 选项1, 选项2, ...]
        # 每个元素是 (bbox, text) 元组
        compatible_results = self._convert_to_compatible_format(filtered_results, sorted_results)
        
        return question_body, compatible_results

    def _convert_to_compatible_format(self, classified_results: dict, sorted_results: List) -> List:
        """将分类结果转换为与quiz_bot兼容的格式
        
        Args:
            classified_results: 包含question和options的字典
            sorted_results: 排序后的原始结果，用于获取bbox
            
        Returns:
            [(bbox, text), ...] 格式，第0个是题目，后续是选项
        """
        options = classified_results.get('options', [])
        
        # 找到每个选项对应的bbox
        result_list = []
        
        # 第一个元素：题目（使用第一个bbox作为占位）
        if sorted_results:
            result_list.append((sorted_results[0][0], classified_results.get('question', '')))
        
        # 后续元素：选项
        # 从sorted_results中找到包含选项文本的bbox
        for option_text in options:
            option_bbox = None
            # 在sorted_results中查找匹配的文本
            for bbox, text in sorted_results:
                if option_text in text or text in option_text:
                    option_bbox = bbox
                    break
            
            # 如果找不到对应的bbox，使用默认值
            if option_bbox is None and sorted_results:
                option_bbox = sorted_results[0][0]
            
            result_list.append((option_bbox, option_text))
        
        return result_list

    
    def _is_close(self, bbox1: List, bbox2: List, threshold: int = None) -> bool:
        """
        判断两个bbox是否垂直方向上足够接近，可以合并
        只有当两个框垂直排列（上下关系）且距离很近时才合并
        
        Args:
            bbox1: 第一个文本框坐标 [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            bbox2: 第二个文本框坐标
            threshold: 距离阈值
            
        Returns:
            是否可以合并
        """
        if threshold is None:
            threshold = self.merge_threshold
            
        # 计算bbox的上下边界和左右边界
        top1 = min(bbox1[0][1], bbox1[1][1])
        bottom1 = max(bbox1[2][1], bbox1[3][1])
        left1 = min(bbox1[0][0], bbox1[3][0])
        right1 = max(bbox1[1][0], bbox1[2][0])
        
        top2 = min(bbox2[0][1], bbox2[1][1])
        bottom2 = max(bbox2[2][1], bbox2[3][1])
        left2 = min(bbox2[0][0], bbox2[3][0])
        right2 = max(bbox2[1][0], bbox2[2][0])
        
        # 计算两个bbox的垂直距离
        if bottom1 < top2:
            vertical_distance = top2 - bottom1
        elif bottom2 < top1:
            vertical_distance = top1 - bottom2
        else:
            vertical_distance = 0  # 重叠的情况
        
        # 检查水平重叠度
        # 如果两个框在水平方向上没有重叠或重叠很少，说明它们是并排的，不应合并
        horizontal_overlap = min(right1, right2) - max(left1, left2)
        width1 = right1 - left1
        width2 = right2 - left2
        min_width = min(width1, width2)
        
        # 只有当水平重叠度超过较窄框宽度的50%时，才认为是垂直排列
        # 这样可以避免合并水平排列的文本框
        if horizontal_overlap < min_width * 0.5:
            return False
            
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
    
    def _sort_and_merge_lines(self, results: List) -> List:
        """按Y坐标排序，并合并同一行的文本框
        
        Args:
            results: OCR结果列表 [(bbox, text), ...]
            
        Returns:
            按行合并后的结果列表
        """
        if not results:
            return []
        
        # 按Y坐标（top）排序
        sorted_results = sorted(results, key=lambda x: min(x[0][0][1], x[0][1][1]))
        
        # 合并同一行的文本（Y坐标接近且水平排列）
        lines = []
        current_line = [sorted_results[0]]
        
        for i in range(1, len(sorted_results)):
            bbox, text = sorted_results[i]
            prev_bbox, prev_text = current_line[-1]
            
            # 计算Y坐标的中心
            y_center = (bbox[0][1] + bbox[2][1]) / 2
            prev_y_center = (prev_bbox[0][1] + prev_bbox[2][1]) / 2
            
            # 如果Y坐标差距小于30像素，认为是同一行
            if abs(y_center - prev_y_center) < 30:
                current_line.append((bbox, text))
            else:
                # 新行开始
                lines.append(current_line)
                current_line = [(bbox, text)]
        
        # 添加最后一行
        if current_line:
            lines.append(current_line)
        
        # 合并每一行的文本（按X坐标排序）
        merged_lines = []
        for line in lines:
            # 按X坐标排序
            line_sorted = sorted(line, key=lambda x: min(x[0][0][0], x[0][3][0]))
            
            # 合并该行的所有文本
            merged_text = ''.join([text for _, text in line_sorted])
            
            # 计算合并后的bbox
            all_points = [point for bbox, _ in line_sorted for point in bbox]
            x_coords = [p[0] for p in all_points]
            y_coords = [p[1] for p in all_points]
            merged_bbox = [
                [min(x_coords), min(y_coords)],
                [max(x_coords), min(y_coords)],
                [max(x_coords), max(y_coords)],
                [min(x_coords), max(y_coords)]
            ]
            
            merged_lines.append((merged_bbox, merged_text))
        
        return merged_lines
    
    def _filter_and_classify(self, results: List) -> dict:
        """过滤选项标记并分类题目和选项
        
        Args:
            results: 按行合并后的结果列表
            
        Returns:
            包含question和options的字典
        """
        if not results:
            return {'question': '', 'options': []}
        
        # 过滤掉单个字母的选项标记（A、B、C、D）
        filtered = []
        for bbox, text in results:
            # 去除空白
            text = text.strip()
            
            # 过滤空文本或纯字母文本
            if text and not (len(text) == 1 and text.isalpha()):
                filtered.append((bbox, text))
        
        if not filtered:
            return {'question': '', 'options': []}
        
        # 第一个文本块是题目，后续是选项
        # 但需要检查是否有多行题目（通过Y坐标判断）
        question_parts = [filtered[0]]
        option_start_idx = 1
        
        # 检查接下来的文本是否也属于题目部分
        # 如果前几行之间的间距较小，可能都是题目
        for i in range(1, len(filtered)):
            if i >= 3:  # 最多3行题目
                break
            
            prev_bbox = filtered[i-1][0]
            curr_bbox = filtered[i][0]
            
            # 计算垂直距离
            prev_bottom = max(prev_bbox[2][1], prev_bbox[3][1])
            curr_top = min(curr_bbox[0][1], curr_bbox[1][1])
            vertical_gap = curr_top - prev_bottom
            
            # 如果间距小于50像素，可能还是题目的一部分
            # 且文本不像选项（不以《开头或不包含常见选项特征）
            curr_text = filtered[i][1]
            if vertical_gap < 50 and not curr_text.startswith('《'):
                question_parts.append(filtered[i])
                option_start_idx = i + 1
            else:
                break
        
        # 合并题目文本
        question_text = ''.join([text for _, text in question_parts])
        
        # 剩余的是选项
        options = [text for _, text in filtered[option_start_idx:]]
        
        return {'question': question_text, 'options': options}
    
    def _format_question_v2(self, classified_results: dict) -> str:
        """格式化题目和选项
        
        Args:
            classified_results: 包含question和options的字典
            
        Returns:
            格式化的题目字符串
        """
        question = classified_results.get('question', '')
        options = classified_results.get('options', [])
        
        if not question:
            return ""
        
        formatted = f"<Question>{question}"
        
        for idx, option in enumerate(options, 1):
            formatted += f"\n<Option>{idx}. {option}"
        
        return formatted

    def _normalize_ocr_results(self, result: Union[List, Tuple]) -> List[Tuple[List, str]]:
        """兼容PaddleOCR 2.x与3.x的返回结果格式。

        PaddleOCR 2.x 返回 [[(bbox, (text, score)), ...]]
        PaddleOCR 3.x 返回 OCRResult 对象，数据在 res.json['res'] 中
        该方法将其统一为 [(bbox, text)] 的形式，方便后续合并。
        """

        if not result:
            return []

        normalized: List[Tuple[List, str]] = []

        # 处理 PaddleOCR 3.x 的预测结果对象
        # result 是一个列表，每个元素是一个预测结果对象
        for res_obj in result:
            # 检查是否是 OCRResult 对象（有 json 属性）
            if hasattr(res_obj, 'json') and isinstance(res_obj.json, dict):
                # 从 json 字典中获取实际的数据
                res_data = res_obj.json.get('res', {})
                
                rec_texts = res_data.get('rec_texts', [])
                rec_polys = res_data.get('rec_polys')
                rec_boxes = res_data.get('rec_boxes')
                
                # 优先使用 rec_polys
                if rec_texts and rec_polys is not None:
                    for text, poly in zip(rec_texts, rec_polys):
                        if text and poly is not None:
                            # 将 numpy 数组转换为列表
                            poly_list = poly.tolist() if hasattr(poly, 'tolist') else poly
                            normalized.append((poly_list, text))
                            
                # 否则使用 rec_boxes
                elif rec_texts and rec_boxes is not None:
                    for text, box in zip(rec_texts, rec_boxes):
                        if text and box is not None and len(box) == 4:
                            # 将 numpy 数组转换为列表
                            box_list = box.tolist() if hasattr(box, 'tolist') else box
                            x1, y1, x2, y2 = box_list
                            poly = [[int(x1), int(y1)], [int(x2), int(y1)], [int(x2), int(y2)], [int(x1), int(y2)]]
                            normalized.append((poly, text))
                            
            # 检查是否有 rec_texts 和 rec_polys 属性（直接属性访问）
            elif hasattr(res_obj, 'rec_texts') and hasattr(res_obj, 'rec_polys'):
                rec_texts = res_obj.rec_texts
                rec_polys = res_obj.rec_polys
                
                # 合并 texts 和 polys
                for text, poly in zip(rec_texts, rec_polys):
                    if text and poly is not None:
                        # 将 numpy 数组转换为列表
                        poly_list = poly.tolist() if hasattr(poly, 'tolist') else poly
                        normalized.append((poly_list, text))
                        
            # 检查是否有 rec_texts 和 rec_boxes 属性
            elif hasattr(res_obj, 'rec_texts') and hasattr(res_obj, 'rec_boxes'):
                rec_texts = res_obj.rec_texts
                rec_boxes = res_obj.rec_boxes
                
                # 将 rec_boxes [x1, y1, x2, y2] 转换为 poly [[x1,y1], [x2,y1], [x2,y2], [x1,y2]]
                for text, box in zip(rec_texts, rec_boxes):
                    if text and box is not None and len(box) == 4:
                        # 将 numpy 数组转换为列表
                        box_list = box.tolist() if hasattr(box, 'tolist') else box
                        x1, y1, x2, y2 = box_list
                        poly = [[int(x1), int(y1)], [int(x2), int(y1)], [int(x2), int(y2)], [int(x1), int(y2)]]
                        normalized.append((poly, text))
                        
            # 处理旧格式列表
            elif isinstance(res_obj, (list, tuple)):
                for item in res_obj:
                    bbox: List = []
                    text: str = ""

                    if isinstance(item, (list, tuple)) and len(item) >= 2:
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
