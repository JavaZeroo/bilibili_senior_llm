"""
自动答题机器人主程序
使用重构后的面向对象架构
"""
from src.core import QuizBot


def main():
    """主函数"""
    # 创建答题机器人实例
    bot = QuizBot(
        window_title="BlueStacks App Player",  # 模拟器窗口标题
        model="gpt-4o",  # LLM模型
        api_key=None  # 使用环境变量中的API密钥
    )
    
    # 可选配置
    
    # 如果需要调整截图区域,可以设置裁剪比例 (左, 上, 右, 下)
    # bot.set_crop_ratios(0.0, 0.2, 1.0, 0.7)
    
    # 如果OCR识别效果不好,可以调整文本框合并阈值
    # bot.set_merge_threshold(20)
    
    # 运行答题机器人
    # 参数max_questions可以限制题目数量,None表示无限循环
    bot.run(max_questions=100)


if __name__ == "__main__":
    main()
