from openai import OpenAI
client = OpenAI()
def get_ans(questionBody):
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages= [
                {
                    "content": "- 你是一个通晓古今的百科全书，拥有丰富的学识和答题经验。现在需要你根据用户输入的问题 <Question> 以及选项 <Option> 选出一个最合适的选项 <Answer>，然后输出选项的内容。\n- 需要注意，你的答案仅能是从选项中选择，不能自由发挥。\n- 题目类型都是选择题，一部分是问题选项，另一部分需要你从选项中选出一个最合适的填补题目的空缺。题目的空缺会用连续的下划线__表示。\n- 你只需要回答你认为正确的选项，不需要做出任何解释。你的答案需要有理论依据，不可以回答虚构的答案。\n",
                    "role": "system"
                },
                {
                    "content": "<Question>最古老的文学体裁是什么？\n<Option>1. 诗歌\n<Option>2. 小说\n<Option>3. 散文\n",
                    "role": "user"
                },
                {
                    "content": "<Answer>1. 诗歌",
                    "role": "assistant"
                },
                {
                    "content": f'{questionBody}',
                    "role": "user"
                }
            ]
    )

    return completion.choices[0].message

print(get_ans('为你千千万万遍" 出自以下哪一部文学作品？\n<Option>《Flipped》\n<Option>《追风筝的人》\n<Option>《简爱》\n<Option>《我的天才女友》'))