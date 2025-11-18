# 自动答题机器人 - 重构版

这是一个用于在安卓模拟器上自动获取题目并答题的软件,采用面向对象设计。

## 项目结构

```
bilibili_senior_llm/
├── main.py                   # 主程序入口
├── quiz_bot.py              # 答题机器人核心类
├── question_extractor.py    # 题目提取模块(OCR)
├── answer_generator.py      # 答案生成模块(LLM)
├── android_controller.py    # 安卓控制模块(截图+点击)
├── cap.py                   # [旧] 截图工具(已重构到android_controller)
├── llm.py                   # [旧] LLM调用(已重构到answer_generator)
└── main_old.py             # [旧] 原始主程序备份
```

## 核心类设计

### 1. QuestionExtractor (题目提取器)
负责从截图中提取题目和选项信息。

**主要功能:**
- 使用 PaddleOCR 识别文字
- 合并相近的文本框
- 格式化题目和选项

**关键方法:**
```python
extract_question(image) -> (question_body, ocr_results)
set_merge_threshold(threshold)  # 调整文本框合并阈值
```

### 2. AnswerGenerator (答案生成器)
负责调用LLM分析题目并给出答案。

**主要功能:**
- 调用 OpenAI API
- 解析LLM返回的答案
- 提取选项编号

**关键方法:**
```python
get_answer(question_body) -> answer_text
extract_option_number(answer) -> int
set_model(model)  # 更换LLM模型
```

### 3. AndroidController (安卓控制器)
负责控制安卓模拟器,包括截图和点击操作。

**主要功能:**
- 截取模拟器窗口
- 去除黑边并裁剪
- 图像二值化处理
- 模拟鼠标点击

**关键方法:**
```python
get_screenshot(save_debug) -> (image, coordinates)
click(x, y)  # 模拟点击
calculate_click_position(bbox, offset) -> (x, y)
set_crop_ratios(left, top, right, bottom)  # 调整截图区域
```

### 4. QuizBot (答题机器人)
协调所有模块完成自动答题流程。

**主要功能:**
- 整合三个核心模块
- 控制答题流程
- 异常处理和日志

**关键方法:**
```python
process_one_question() -> bool  # 处理一道题
run(max_questions)  # 运行机器人
set_debug_mode(enabled)  # 开启调试模式
```

## 使用方法

### 基本使用
```python
from quiz_bot import QuizBot

# 创建机器人实例
bot = QuizBot(
    window_title="BlueStacks App Player",
    model="gpt-4o"
)

# 运行(无限循环)
bot.run()
```

### 高级配置
```python
# 限制题目数量
bot.run(max_questions=10)

# 开启调试模式(保存截图)
bot.set_debug_mode(True)

# 调整点击延迟
bot.set_click_delay(2.0)

# 自定义截图区域
bot.set_crop_ratios(0.0, 0.2, 1.0, 0.7)

# 调整OCR合并阈值
bot.set_merge_threshold(30)
```

### PaddleOCR 3.x 配置

在 `config.yaml` 中通过 `ocr` 区块即可配置 PP-OCRv4 模型路径、GPU 等参数：

```yaml
ocr:
  det_model_dir: /path/to/ch_PP-OCRv4_det_infer
  rec_model_dir: /path/to/ch_PP-OCRv4_rec_infer
  cls_model_dir: /path/to/ch_ppocr_mobile_v2.0_cls_infer
  use_gpu: false
  ocr_version: PP-OCRv4
```

如需在代码内覆盖配置，可以直接实例化 `QuestionExtractor` 并注入：

```python
from src.extractors import QuestionExtractor
from src.core import QuizBot

bot = QuizBot()
bot.question_extractor = QuestionExtractor(ocr_version="PP-OCRv4", use_gpu=True)
```

## 依赖库

- paddlepaddle>=3.0.0: 深度学习框架
- paddleocr>=3.0.0: OCR文字识别
- openai: LLM接口
- PIL/Pillow: 图像处理
- numpy: 数组处理
- pygetwindow: 窗口管理
- pywin32: Windows API调用

## 工作流程

1. **截图** → AndroidController 获取模拟器窗口截图
2. **识别** → QuestionExtractor 使用OCR提取题目和选项
3. **分析** → AnswerGenerator 调用LLM获取答案
4. **点击** → AndroidController 计算位置并模拟点击
5. **等待** → 延迟后处理下一题

## 扩展性

### 添加新的题目提取方式
可以创建新的提取器类继承或实现类似接口:
```python
class UIParser:
    """解析UI层级结构获取题目"""
    def extract_question(self, ...):
        pass
```

### 添加其他LLM服务
可以扩展AnswerGenerator支持其他API:
```python
class AnswerGenerator:
    def __init__(self, provider="openai"):
        if provider == "openai":
            # OpenAI实现
        elif provider == "claude":
            # Claude实现
```

## 注意事项

1. 需要先配置 OpenAI API Key
2. 确保模拟器窗口标题正确
3. 可根据实际情况调整截图裁剪比例
4. OCR模型需要提前下载好

## 相比原版的改进

- ✅ 模块化设计,职责清晰
- ✅ 易于扩展和维护
- ✅ 配置灵活,参数可调
- ✅ 异常处理完善
- ✅ 代码可读性强
- ✅ 便于单元测试
