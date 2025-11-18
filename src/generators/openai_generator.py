"""
答案生成模块
负责调用LLM获取题目答案
"""
from openai import OpenAI
from typing import Optional
from src.core.base import AnswerGeneratorBase


class AnswerGenerator(AnswerGeneratorBase):
    """答案生成器 - 使用LLM分析题目并给出答案"""
    
    def __init__(self, model: str = "gpt-4o", api_key: Optional[str] = None, 
                 base_url: Optional[str] = None):
        """
        初始化答案生成器
        
        Args:
            model: 使用的模型名称
            api_key: API密钥，如果为None则使用环境变量
            base_url: 自定义API端点 (如 https://api.deepseek.com/v1)
        """
        # 初始化客户端配置
        client_kwargs = {}
        if api_key:
            client_kwargs['api_key'] = api_key
        if base_url:
            client_kwargs['base_url'] = base_url
            
        self.client = OpenAI(**client_kwargs)
        self.model = model
        
        # 系统提示词
        self.system_prompt = (
            "- 你是一个通晓古今的百科全书,拥有丰富的学识和答题经验。"
            "现在需要你根据用户输入的问题 <Question> 以及选项 <Option> "
            "选出一个最合适的选项 <Answer>,然后输出选项的内容。\n"
            "- 需要注意,你的答案仅能是从选项中选择,不能自由发挥。\n"
            "- 题目类型都是选择题,一部分是问题选项,另一部分需要你从选项中"
            "选出一个最合适的填补题目的空缺。题目的空缺会用连续的下划线__表示。\n"
            "- 你只需要回答你认为正确的选项,不需要做出任何解释。"
            "你的答案需要有理论依据,不可以回答虚构的答案。\n"
        )
        
        # 示例对话
        self.example_question = (
            "<Question>最古老的文学体裁是什么?\n"
            "<Option>1. 诗歌\n"
            "<Option>2. 小说\n"
            "<Option>3. 散文\n"
        )
        self.example_answer = "<Answer>1. 诗歌"
    
    def get_answer(self, question_body: str) -> str:
        """
        获取题目答案
        
        Args:
            question_body: 格式化的题目字符串
            
        Returns:
            LLM返回的答案文本
        """
        messages = [
            {
                "content": self.system_prompt,
                "role": "system"
            },
            {
                "content": self.example_question,
                "role": "user"
            },
            {
                "content": self.example_answer,
                "role": "assistant"
            },
            {
                "content": question_body,
                "role": "user"
            }
        ]
        
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        
        return completion.choices[0].message.content
    
    def extract_option_number(self, answer: str) -> int:
        """
        从答案中提取选项编号
        
        Args:
            answer: LLM返回的答案字符串
            
        Returns:
            选项编号 (1, 2, 3, 4...)
        """
        try:
            # 尝试从答案中提取数字
            # 格式如: "<Answer>1. 诗歌" 或 "1" 或 "选项1"
            import re
            numbers = re.findall(r'\d+', answer)
            if numbers:
                return int(numbers[0])
            else:
                raise ValueError(f"无法从答案中提取选项编号: {answer}")
        except Exception as e:
            print(f"提取选项编号失败: {e}")
            return 1  # 默认返回选项1
    
    def set_model(self, model: str):
        """更改使用的模型"""
        self.model = model
    
    def set_system_prompt(self, prompt: str):
        """自定义系统提示词"""
        self.system_prompt = prompt
