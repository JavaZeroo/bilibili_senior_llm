# 项目结构说明

## 📂 目录结构详解

```
bilibili_senior_llm/
│
├── 📄 main.py                          # 主程序入口
│   └─ 功能：启动答题机器人
│
├── 📁 src/                             # 源代码根目录
│   │
│   ├── 📁 core/                        # 核心模块（不可替换）
│   │   ├── base.py                    # 抽象基类定义
│   │   │   ├── QuestionExtractorBase  # 题目提取器抽象基类
│   │   │   ├── AnswerGeneratorBase    # 答案生成器抽象基类
│   │   │   └── AndroidControllerBase  # 控制器抽象基类
│   │   │
│   │   └── quiz_bot.py                # 答题机器人主类
│   │       └── QuizBot                # 协调所有模块的核心类
│   │
│   ├── 📁 extractors/                  # 题目提取器（可替换）
│   │   └── ocr_extractor.py           # OCR实现
│   │       └── QuestionExtractor      # 使用PaddleOCR提取题目
│   │
│   ├── 📁 generators/                  # 答案生成器（可替换）
│   │   └── openai_generator.py        # OpenAI实现
│   │       └── AnswerGenerator        # 使用GPT生成答案
│   │
│   └── 📁 controllers/                 # 设备控制器（可替换）
│       └── bluestack_controller.py    # BlueStacks实现
│           └── AndroidController      # 控制BlueStacks模拟器
│
├── 📁 docs/                            # 文档目录
│   ├── README_NEW.md                  # 详细使用文档
│   └── ARCHITECTURE.md                # 架构设计文档
│
└── 📁 legacy/                          # 旧代码备份
    ├── main_old.py                    # v1.0主程序
    ├── cap.py                         # v1.0截图工具
    ├── llm.py                         # v1.0 LLM调用
    └── README_v1.md                   # v1.0说明文档
```

## 🔄 模块依赖关系

```
main.py
  └─→ src.core.QuizBot
        ├─→ src.core.base.QuestionExtractorBase (抽象)
        │     └─→ src.extractors.QuestionExtractor (实现)
        │
        ├─→ src.core.base.AnswerGeneratorBase (抽象)
        │     └─→ src.generators.AnswerGenerator (实现)
        │
        └─→ src.core.base.AndroidControllerBase (抽象)
              └─→ src.controllers.AndroidController (实现)
```

## 📦 各模块职责

### core/ - 核心模块
**不可替换的基础框架**

- `base.py`: 定义所有抽象接口
  - 确保扩展模块遵循统一接口
  - 提供类型约束和文档
  
- `quiz_bot.py`: 主业务逻辑
  - 协调各个模块工作
  - 处理答题流程
  - 异常处理和日志

### extractors/ - 题目提取器
**可替换：实现不同的题目获取方式**

当前实现：
- `ocr_extractor.py`: 使用OCR识别屏幕文字

可能的扩展：
- `ui_parser_extractor.py`: 解析UI层级结构
- `api_extractor.py`: 通过API获取题目
- `screenshot_analyzer.py`: 深度学习图像分析

### generators/ - 答案生成器
**可替换：使用不同的LLM服务**

当前实现：
- `openai_generator.py`: 使用OpenAI GPT模型

可能的扩展：
- `claude_generator.py`: 使用Anthropic Claude
- `local_llm_generator.py`: 使用本地大模型
- `ensemble_generator.py`: 集成多个模型投票

### controllers/ - 设备控制器
**可替换：支持不同的设备/模拟器**

当前实现：
- `bluestack_controller.py`: 控制BlueStacks模拟器

可能的扩展：
- `adb_controller.py`: 使用ADB直接控制
- `nox_controller.py`: 支持夜神模拟器
- `mumu_controller.py`: 支持MuMu模拟器
- `real_device_controller.py`: 控制真实设备

## 🎯 设计原则

### 1. 单一职责原则 (SRP)
每个类只负责一个功能领域：
- Extractor 只负责提取题目
- Generator 只负责生成答案
- Controller 只负责设备控制

### 2. 开闭原则 (OCP)
对扩展开放，对修改关闭：
- 通过继承基类添加新实现
- 不需要修改核心代码

### 3. 里氏替换原则 (LSP)
子类可以替换父类：
- 所有实现都遵循基类接口
- QuizBot 通过基类类型引用

### 4. 依赖倒置原则 (DIP)
依赖抽象而非具体实现：
- QuizBot 依赖抽象基类
- 具体实现可以随意替换

## 🔧 扩展指南

### 添加新的提取器

1. 在 `src/extractors/` 创建新文件
2. 继承 `QuestionExtractorBase`
3. 实现所有抽象方法
4. 在 `__init__.py` 中导出

示例：
```python
# src/extractors/ui_parser_extractor.py
from src.core.base import QuestionExtractorBase

class UIParserExtractor(QuestionExtractorBase):
    def extract_question(self, image):
        # 你的实现
        pass
    
    def set_merge_threshold(self, threshold):
        pass
```

### 添加新的生成器

1. 在 `src/generators/` 创建新文件
2. 继承 `AnswerGeneratorBase`
3. 实现所有抽象方法
4. 在 `__init__.py` 中导出

### 添加新的控制器

1. 在 `src/controllers/` 创建新文件
2. 继承 `AndroidControllerBase`
3. 实现所有抽象方法
4. 在 `__init__.py` 中导出

## 📝 命名规范

### 文件命名
- 小写字母 + 下划线: `ocr_extractor.py`
- 描述性名称，体现实现方式

### 类命名
- 大驼峰: `QuestionExtractor`
- 以功能词结尾: `Extractor`, `Generator`, `Controller`

### 目录命名
- 小写字母
- 复数形式: `extractors`, `generators`, `controllers`
- 表示同类模块集合

## 🔍 文件查找指南

### 我想修改...

**题目识别逻辑** → `src/extractors/ocr_extractor.py`

**LLM提示词** → `src/generators/openai_generator.py`

**截图/点击逻辑** → `src/controllers/bluestack_controller.py`

**整体流程** → `src/core/quiz_bot.py`

**接口定义** → `src/core/base.py`

**程序入口** → `main.py`

## 📊 模块复杂度

```
简单 ←──────────────────────→ 复杂

main.py (10行)
  ↓
quiz_bot.py (150行)
  ↓
base.py (70行) - 纯接口定义
  ↓
ocr_extractor.py (180行) - OCR + 文本处理
openai_generator.py (120行) - API调用 + 解析
bluestack_controller.py (290行) - Win32 API + 图像处理
```

## 🎓 学习路径

1. **入门** → 阅读 `main.py` 和 `README.md`
2. **理解流程** → 查看 `quiz_bot.py`
3. **了解接口** → 阅读 `base.py`
4. **深入实现** → 研究各个实现类
5. **自定义扩展** → 继承基类实现新功能

## 💡 最佳实践

### ✅ 推荐
- 通过 `__init__.py` 导入模块
- 依赖注入而非硬编码
- 每个类单独测试
- 使用类型注解

### ❌ 避免
- 跨层级直接导入
- 在基类中添加具体实现
- 修改核心模块接口
- 循环依赖
