"""
项目架构说明

本项目采用面向对象设计,将功能划分为三个核心类和一个协调类。

架构图:
┌─────────────────────────────────────────────────────────┐
│                      QuizBot                             │
│                   (答题机器人主类)                        │
│  - 协调各个模块                                          │
│  - 控制整体流程                                          │
│  - 异常处理                                              │
└────────┬────────────────┬────────────────┬──────────────┘
         │                │                │
         │                │                │
         ▼                ▼                ▼
┌────────────────┐ ┌────────────────┐ ┌────────────────┐
│ Question       │ │ Answer         │ │ Android        │
│ Extractor      │ │ Generator      │ │ Controller     │
│                │ │                │ │                │
│ 题目提取器     │ │ 答案生成器     │ │ 安卓控制器     │
├────────────────┤ ├────────────────┤ ├────────────────┤
│- OCR识别       │ │- 调用LLM       │ │- 截图          │
│- 文本合并      │ │- 解析答案      │ │- 点击          │
│- 格式化输出    │ │- 提取选项      │ │- 坐标计算      │
└────────────────┘ └────────────────┘ └────────────────┘

数据流:
1. 截图 → AndroidController.get_screenshot()
   └─> 返回处理后的图像和坐标信息

2. 识别 → QuestionExtractor.extract_question(image)
   └─> 返回格式化的题目文本和OCR结果

3. 分析 → AnswerGenerator.get_answer(question_body)
   └─> 返回LLM答案和选项编号

4. 点击 → AndroidController.click(x, y)
   └─> 模拟鼠标点击选项

优势:
1. 单一职责原则 - 每个类只负责一个功能
2. 开闭原则 - 易于扩展新功能(如UI解析、其他LLM等)
3. 依赖倒置 - 高层模块不依赖低层实现细节
4. 可测试性 - 每个模块可独立测试
5. 可维护性 - 代码清晰,易于理解和修改

扩展方向:
1. QuestionExtractor 可扩展为:
   - OCRExtractor (当前实现)
   - UIParserExtractor (解析UI层级)
   - ScreenshotAnalyzer (深度学习识别)

2. AnswerGenerator 可扩展为:
   - OpenAIGenerator (当前实现)
   - ClaudeGenerator
   - LocalLLMGenerator

3. AndroidController 可扩展为:
   - 支持多种模拟器
   - ADB直接控制
   - 虚拟输入设备
"""
