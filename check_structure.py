"""
快速启动脚本
用于演示和测试项目结构
"""

def show_project_structure():
    """显示项目结构"""
    print("=" * 60)
    print("📦 自动答题机器人 v2.0 - 项目结构")
    print("=" * 60)
    print()
    print("📁 src/")
    print("  ├── 📁 core/          - 核心模块")
    print("  │   ├── base.py       - 抽象基类")
    print("  │   └── quiz_bot.py   - 主应用类")
    print("  │")
    print("  ├── 📁 extractors/    - 题目提取器")
    print("  │   └── ocr_extractor.py")
    print("  │")
    print("  ├── 📁 generators/    - 答案生成器")
    print("  │   └── openai_generator.py")
    print("  │")
    print("  └── 📁 controllers/   - 设备控制器")
    print("      └── bluestack_controller.py")
    print()
    print("📁 docs/              - 文档")
    print("📁 legacy/            - 旧代码备份")
    print("📄 main.py            - 程序入口")
    print()
    print("=" * 60)


def check_imports():
    """检查导入是否正常"""
    print("\n🔍 检查模块导入...")
    print()
    
    try:
        from src.core.base import (
            QuestionExtractorBase, 
            AnswerGeneratorBase, 
            AndroidControllerBase
        )
        print("✅ 基类导入成功")
    except Exception as e:
        print(f"❌ 基类导入失败: {e}")
        return False
    
    try:
        from src.extractors import QuestionExtractor
        print("✅ QuestionExtractor 导入成功")
    except Exception as e:
        print(f"❌ QuestionExtractor 导入失败: {e}")
        return False
    
    try:
        from src.generators import AnswerGenerator
        print("✅ AnswerGenerator 导入成功")
    except Exception as e:
        print(f"❌ AnswerGenerator 导入失败: {e}")
        return False
    
    try:
        from src.controllers import AndroidController
        print("✅ AndroidController 导入成功")
    except Exception as e:
        print(f"❌ AndroidController 导入失败: {e}")
        return False
    
    try:
        from src.core import QuizBot
        print("✅ QuizBot 导入成功")
    except Exception as e:
        print(f"❌ QuizBot 导入失败: {e}")
        return False
    
    print()
    print("🎉 所有模块导入测试通过！")
    return True


def show_usage_example():
    """显示使用示例"""
    print("\n📖 使用示例:")
    print("=" * 60)
    print("""
from src.core import QuizBot

# 基本使用
bot = QuizBot(
    window_title="BlueStacks App Player",
    model="gpt-4o"
)
bot.run()

# 高级配置
bot.set_debug_mode(True)
bot.set_click_delay(2.0)
bot.set_crop_ratios(0.0, 0.2, 1.0, 0.7)
bot.run(max_questions=10)

# 自定义实现
from your_module import CustomExtractor
bot.question_extractor = CustomExtractor()
bot.run()
""")
    print("=" * 60)


def main():
    """主函数"""
    show_project_structure()
    
    # 检查导入
    imports_ok = check_imports()
    
    if imports_ok:
        show_usage_example()
        print("\n✨ 项目结构重构完成！")
        print("💡 运行 'python main.py' 启动答题机器人")
    else:
        print("\n⚠️  请先安装依赖: pip install -r requirements.txt")
    
    print()


if __name__ == "__main__":
    main()
