# 自动答题机器人 v2.0

一个用于在安卓模拟器上自动获取题目并答题的智能机器人，采用模块化面向对象设计。

## ✨ 特性

- 🎯 **模块化设计** - 清晰的目录结构，易于维护和扩展
- 🔧 **可插拔架构** - 基于抽象基类，支持自定义实现
- 🤖 **智能识别** - 使用OCR技术提取题目
- 🧠 **AI答题** - 集成OpenAI GPT模型分析题目
- 🖱️ **自动控制** - 自动截图和模拟点击

## 📁 项目结构

```
bilibili_senior_llm/
├── main.py                    # 主程序入口
├── README.md                  # 项目说明
├── LICENSE                    # 许可证
├── .gitignore                 # Git忽略配置
│
├── src/                       # 源代码目录
│   ├── __init__.py
│   │
│   ├── core/                  # 核心模块
│   │   ├── __init__.py
│   │   ├── base.py           # 抽象基类定义
│   │   └── quiz_bot.py       # 答题机器人主类
│   │
│   ├── extractors/            # 题目提取器
│   │   ├── __init__.py
│   │   └── ocr_extractor.py  # OCR提取器实现
│   │
│   ├── generators/            # 答案生成器
│   │   ├── __init__.py
│   │   └── openai_generator.py  # OpenAI生成器实现
│   │
│   └── controllers/           # 控制器
│       ├── __init__.py
│       └── bluestack_controller.py  # BlueStacks控制器实现
│
├── docs/                      # 文档目录
│   ├── README_NEW.md         # 详细使用文档
│   └── ARCHITECTURE.md       # 架构设计文档
│
└── legacy/                    # 旧代码备份
    ├── main_old.py           # 旧版主程序
    ├── cap.py                # 旧版截图工具
    ├── llm.py                # 旧版LLM调用
    └── README_v1.md          # 旧版README
```

## 🏗️ 架构设计

### 核心抽象基类

项目定义了三个核心抽象基类，确保可扩展性：

1. **QuestionExtractorBase** - 题目提取器基类
   - 定义题目提取接口
   - 当前实现：OCR提取器

2. **AnswerGeneratorBase** - 答案生成器基类
   - 定义答案生成接口
   - 当前实现：OpenAI生成器

3. **AndroidControllerBase** - 控制器基类
   - 定义设备控制接口
   - 当前实现：BlueStacks控制器

### 工作流程

```
1. 截图 → BlueStackController.get_screenshot()
2. 识别 → OCRExtractor.extract_question()
3. 分析 → OpenAIGenerator.get_answer()
4. 点击 → BlueStackController.click()
```

## 🚀 快速开始

### 安装依赖

```bash
pip install "paddlepaddle>=3.0.0" "paddleocr>=3.0.0" openai pillow numpy pygetwindow pywin32
```

### 基本使用

```python
from src.core import QuizBot

# 创建机器人实例
bot = QuizBot(
    window_title="BlueStacks App Player",
    model="gpt-4o"
)

# 运行
bot.run()
```

### 配置PaddleOCR 3.x

`config.yaml` 中新增了 `ocr` 区块，可以直接配置 PaddleOCR 3.x/PP-OCRv4 的路径和参数：

```yaml
ocr:
  det_model_dir: /path/to/ch_PP-OCRv4_det_infer
  rec_model_dir: /path/to/ch_PP-OCRv4_rec_infer
  cls_model_dir: /path/to/ch_ppocr_mobile_v2.0_cls_infer
  use_gpu: true
  show_log: false
  ocr_version: PP-OCRv4
```

也可以在代码中直接构造自定义的 `QuestionExtractor`：

```python
from src.extractors import QuestionExtractor

question_extractor = QuestionExtractor(
    det_model_dir="/path/to/det",
    rec_model_dir="/path/to/rec",
    cls_model_dir="/path/to/cls",
    ocr_version="PP-OCRv4",
    use_gpu=True,
)
```

### 运行主程序

```bash
python main.py
```

## 🔧 自定义扩展

### 添加新的题目提取器

```python
from src.core.base import QuestionExtractorBase

class UIParserExtractor(QuestionExtractorBase):
    """使用UI解析获取题目"""
    
    def extract_question(self, image):
        # 实现你的逻辑
        pass
    
    def set_merge_threshold(self, threshold):
        pass
```

### 添加新的答案生成器

```python
from src.core.base import AnswerGeneratorBase

class ClaudeGenerator(AnswerGeneratorBase):
    """使用Claude模型生成答案"""
    
    def get_answer(self, question_body):
        # 实现你的逻辑
        pass
    
    def extract_option_number(self, answer):
        pass
```

### 添加新的控制器

```python
from src.core.base import AndroidControllerBase

class ADBController(AndroidControllerBase):
    """使用ADB直接控制设备"""
    
    def get_screenshot(self, save_debug=False):
        # 实现你的逻辑
        pass
    
    def click(self, x, y):
        pass
    
    def calculate_click_position(self, bbox, offset):
        pass
```

### 使用自定义实现

```python
from src.core import QuizBot
from your_module import UIParserExtractor, ClaudeGenerator

# 创建自定义实例
bot = QuizBot()

# 替换为自定义实现
bot.question_extractor = UIParserExtractor()
bot.answer_generator = ClaudeGenerator()

bot.run()
```

## ⚙️ 配置选项

```python
# 调试模式（保存截图）
bot.set_debug_mode(True)

# 点击延迟（秒）
bot.set_click_delay(2.0)

# 截图裁剪比例 (左, 上, 右, 下)
bot.set_crop_ratios(0.0, 0.2, 1.0, 0.7)

# OCR文本框合并阈值
bot.set_merge_threshold(30)

# 限制题目数量
bot.run(max_questions=10)
```

## 📚 详细文档

- [详细使用文档](docs/README_NEW.md)
- [架构设计说明](docs/ARCHITECTURE.md)

## 🛠️ 技术栈

- **OCR**: PaddleOCR
- **LLM**: OpenAI GPT-4
- **图像处理**: Pillow, NumPy
- **窗口控制**: PyGetWindow, PyWin32
- **语言**: Python 3.8+

## 📝 版本历史

### v2.0.0 (当前版本)
- ✅ 完全重构为模块化架构
- ✅ 添加抽象基类支持扩展
- ✅ 清晰的目录结构
- ✅ 更好的命名和文档

### v1.0.0
- 基础功能实现
- OCR识别和LLM答题

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## ⚠️ 注意事项

1. 需要配置 OpenAI API Key（环境变量或代码中设置）
2. 确保模拟器窗口标题正确
3. 根据实际情况调整截图裁剪比例
4. OCR模型需要提前下载

## 📮 联系方式

如有问题，请提交Issue或联系项目维护者。
