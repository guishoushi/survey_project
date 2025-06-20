from django.conf import settings
from .models import Question
from .generate_prompt import gen_prompt


def analyze_responses(answers):
    """
    格式化问卷答案并发送给AI进行分析
    """
    prompt = "请分析以下问卷回答并给出反馈：\n\n"

    for question_id, answer in answers.items():
        question = Question.objects.get(id=question_id.replace('q_', ''))
        prompt += f"问题: {question.text}\n回答: {answer}\n\n"

    prompt += "请总结用户的整体情况并提供改进建议:"

    return gen_prompt(prompt)
