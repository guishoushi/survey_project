# quiz/views.py
import json
import os.path

from django.http.response import StreamingHttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CampEnrollmentForm

from .models import Question
from .utility.generate_prompt import gen_prompt


def quiz_view(request):
    # 获取所有题目及其选项
    questions = Question.objects.prefetch_related('options').all()

    # 将问题转换为前端需要的格式
    quiz_data = []
    for question in questions:
        quiz_data.append({
            'id': question.id,
            'question': question.question_text,
            'options': [
                {'text': opt.option_text, 'is_correct': opt.is_correct}
                for opt in question.options.all()
            ],
            'explanation': question.explanation
        })

    return render(request, 'index.html', {'quiz_data': json.dumps(quiz_data)})


def report_view(request):
    # 处理用户提交的答案
    if request.method == 'POST':
        user_answers = str(json.loads(request.body))
        # 在这里处理用户答案，例如保存到数据库或进行分析
        print(f'{os.path.dirname(__file__)}/course_info.txt')
        with open(f'{os.path.dirname(__file__)}/utility/2025夏令营招生一本通.txt', 'r', encoding='utf-8') as f:
            course_info = f.read()
        prompt = f'''你是一个专家，请根据用户提交的问卷回答，并结合我们的课程资料给家长推荐适合孩子的课程，介绍哪些课程能够解决孩子的问题：
这是课程资料：
{course_info}
这是用户提交的问卷：
{user_answers}'''

        return StreamingHttpResponse(gen_prompt(prompt), content_type="text/plain")
    return None




def camp_enrollment(request):
    if request.method == 'POST':
        form = CampEnrollmentForm(request.POST)
        if form.is_valid():
            enrollment = form.save()
            messages.success(request, '夏令营报名信息已成功提交！')
            return redirect('https://www.xdxialingying.com/wintercamp/')
    else:
        form = CampEnrollmentForm()

    return render(request, 'enrollment.html', {'form': form})
