"""
答题机器人主应用
协调各个模块完成自动答题
"""
import time
from typing import Optional
from src.extractors import QuestionExtractor
from src.generators import AnswerGenerator
from src.controllers import AndroidController
from src.core.base import QuestionExtractorBase, AnswerGeneratorBase, AndroidControllerBase
from src.controllers.adb_controller import ADBController
from src.core import config as cfg_loader


class QuizBot:
    """答题机器人 - 协调所有模块完成自动答题"""
    
    def __init__(self, 
                 window_title: str = "BlueStacks App Player",
                 model: str = "gpt-4o",
                 api_key: Optional[str] = None,
                 config_path: Optional[str] = None):
        """
        初始化答题机器人
        
        Args:
            window_title: 模拟器窗口标题
            model: LLM模型名称
            api_key: OpenAI API密钥
        """
        # 读取配置（合并默认）
        self.config = cfg_loader.load_config(config_path)

        # 初始化三个核心模块（通过基类注入实现可替换性）
        self.question_extractor: QuestionExtractorBase = QuestionExtractor()
        self.answer_generator: AnswerGeneratorBase = AnswerGenerator(model=self.config.get("llm", {}).get("model", model), api_key=self.config.get("llm", {}).get("api_key", api_key))

        # 根据配置选择控制器实现（adb 或 bluestacks）
        controller_type = self.config.get("controller", {}).get("type", "adb")
        if controller_type == "adb":
            adb_cfg = self.config.get("adb", {})
            self.android_controller: AndroidControllerBase = ADBController(adb_path=adb_cfg.get("adb_path", "adb"), device_id=adb_cfg.get("device_id", None), config=self.config)
        else:
            # bluetacks controller still accepts window_title
            self.android_controller: AndroidControllerBase = AndroidController(window_title=window_title)
        
        # 应用级配置
        app_cfg = self.config.get("app", {})
        self.click_delay = app_cfg.get("click_delay", 1.5)
        self.debug_mode = app_cfg.get("debug_mode", False)
    
    def process_one_question(self) -> bool:
        """
        处理一道题目
        
        Returns:
            是否成功处理
        """
        try:
            # 1. 截图
            print("正在截图...")
            screenshot, (abs_left, abs_top, abs_right, abs_bottom) = \
                self.android_controller.get_screenshot(save_debug=self.debug_mode)
            
            # 2. 提取题目
            print("正在识别题目...")
            question_body, ocr_results = self.question_extractor.extract_question(screenshot)
            print(f"\n识别到的题目:\n{question_body}\n")
            
            if not ocr_results or len(ocr_results) < 2:
                print("未识别到有效题目和选项")
                return False
            
            # 3. 获取答案
            print("正在调用LLM分析...")
            answer_text = self.answer_generator.get_answer(question_body)
            option_number = self.answer_generator.extract_option_number(answer_text)
            print(f"LLM答案: {answer_text}")
            print(f"最终选择: 选项 {option_number}")
            
            # 4. 计算点击位置
            if option_number < 1 or option_number > len(ocr_results):
                print(f"选项编号 {option_number} 超出范围")
                return False
            
            # OCR结果中第0个是题目,从第1个开始是选项
            selected_bbox = ocr_results[option_number][0]
            click_x, click_y = self.android_controller.calculate_click_position(
                selected_bbox, 
                (abs_left, abs_top)
            )
            
            # 5. 执行点击
            print(f"点击位置: ({click_x}, {click_y})")
            self.android_controller.click(click_x, click_y)
            
            # 6. 等待下一题
            time.sleep(self.click_delay)
            
            return True
            
        except Exception as e:
            print(f"处理题目时出错: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run(self, max_questions: Optional[int] = None):
        """
        运行答题机器人
        
        Args:
            max_questions: 最多处理的题目数量,None表示无限循环
        """
        print("=" * 50)
        print("答题机器人启动")
        print("=" * 50)
        
        question_count = 0
        success_count = 0
        
        try:
            while True:
                # 检查是否达到最大题目数
                if max_questions is not None and question_count >= max_questions:
                    break
                
                question_count += 1
                print(f"\n{'='*50}")
                print(f"正在处理第 {question_count} 题")
                print('='*50)
                
                success = self.process_one_question()
                if success:
                    success_count += 1
                
        except KeyboardInterrupt:
            print("\n\n用户中断")
        except Exception as e:
            print(f"\n\n程序异常: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print("\n" + "=" * 50)
            print("答题机器人停止")
            print(f"共处理 {question_count} 题,成功 {success_count} 题")
            print("=" * 50)
    
    def set_debug_mode(self, enabled: bool):
        """设置调试模式"""
        self.debug_mode = enabled
    
    def set_click_delay(self, delay: float):
        """设置点击后等待时间"""
        self.click_delay = delay
    
    def set_crop_ratios(self, left: float, top: float, right: float, bottom: float):
        """设置截图裁剪比例"""
        self.android_controller.set_crop_ratios(left, top, right, bottom)
    
    def set_merge_threshold(self, threshold: int):
        """设置OCR文本框合并阈值"""
        self.question_extractor.set_merge_threshold(threshold)
