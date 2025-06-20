import json

from django.core.files.locks import unlock
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import date, timedelta
from .models import UserProfile, Habit, CheckIn, Badge, BadgeRecords
from .forms import UserRegistrationForm, UserLoginForm, HabitForm, CheckInForm


class UserLoginView(View):
    """用户登录视图"""
    template_name = 'login.html'
    form_class = UserLoginForm

    def get(self, request):
        """
        处理GET请求以显示用户登录表单或重定向已认证的用户。

        如果用户已经通过身份验证，则重定向到用户仪表板页面。
        否则，创建一个新的登录表单实例，并将其渲染到模板中以供显示。

        参数:
        - request: HttpRequest对象，包含用户发起的请求信息。

        返回:
        - 如果用户已认证，返回到用户仪表板页面的HttpResponseRedirect对象。
        - 如果用户未认证，返回一个渲染了登录表单的HttpResponse对象。
        """
        # 检查用户是否已经通过身份验证
        if request.user.is_authenticated:
            # 如果用户已认证，重定向到用户仪表板页面
            return redirect('user_dashboard')

        # 创建一个新的登录表单实例
        form = self.form_class()

        # 渲染登录表单到模板中并返回
        return render(request, self.template_name, {'form': form, 'user': request.user})

    def post(self, request):
        """
        处理POST请求的函数，用于用户登录验证。

        参数:
        - request: HttpRequest对象，包含用户的POST请求信息。

        返回:
        - 如果用户成功登录，重定向到'user_dashboard'页面。
        - 如果登录失败或表单数据无效，则重新渲染登录页面，包含表单数据。
        """
        # 创建表单实例，用POST数据填充
        form = self.form_class(data=request.POST)

        # 验证表单数据是否有效
        if form.is_valid():
            # 从表单数据中提取用户名和密码
            phone = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            # 使用提取的用户名和密码验证用户
            user = authenticate(phone=phone, password=password)

            # 如果用户存在且验证通过
            if user is not None:
                # 执行登录操作
                login(request, user)
                # 显示欢迎消息
                messages.success(request, f'欢迎回来，{user.username}！')
                # 重定向到用户仪表盘页面
                return redirect('user_dashboard')
            else:
                # 如果用户验证失败，显示错误消息
                messages.error(request, '手机号或密码错误')

        # 如果表单数据无效或用户验证失败，重新渲染登录页面
        return render(request, self.template_name, {'form': form})


class UserLogoutView(View):
    """用户登出视图"""

    def get(self, request):
        """
        处理用户退出登录的请求。

        这个方法首先调用django的logout函数来清除用户的登录信息，然后通过messages框架
        向用户发送一条成功退出登录的消息，最后重定向用户到登录页面。

        参数:
        - request: HttpRequest对象，包含了用户退出登录的请求信息。

        返回:
        - 重定向到登录页面的HttpResponseRedirect对象。
        """
        # 清除用户的登录信息，实现退出登录的功能
        logout(request)

        # 使用messages框架记录用户成功退出登录的消息
        messages.success(request, '你已成功退出登录。')

        # 重定向用户到登录页面
        return redirect('user_login')


class UserDashboardView(LoginRequiredMixin, View):
    """用户仪表盘视图"""
    template_name = 'dashboard.html'

    def get(self, request):
        # 获取管理员添加的所有活跃习惯
        habits = Habit.objects.filter(is_active=True)

        # 获取用户今日的打卡情况
        today_checkins = CheckIn.objects.filter(user=request.user, date=date.today())
        today_id_list = today_checkins.values_list('habit_id', flat=True)

        # 检查并授予用户徽章
        self.check_and_award_badges(request.user)

        # 构建用户特定的习惯数据
        user_habit_data = []
        for habit in habits:
            #  获取用户打卡的记录
            user_check_in_records = CheckIn.objects.filter(user=request.user, habit=habit).first()
            if user_check_in_records:
                streak = user_check_in_records.streak  # 获取用户特定的连续天数
            else:
                streak = 0
            checkin = habit.checkins.filter(user=request.user).first()
            if checkin:
                total_checkins = checkin.total_checkins
            else:
                total_checkins = 0
            user_habit_data.append({
                'id': habit.id,
                'name': habit.name,
                'icon': habit.icon.url,
                'streak': streak,  # 使用用户特定的连续天数
                'goal': habit.goal,
                'progress': int(streak / habit.goal * 100) if habit.goal > 0 else 0,
                'todayDone': habit.id in today_id_list,
                'total_checkins': total_checkins,
            })

        # 渲染勋章的逻辑
        badges_list = []
        # 遍历所有的勋章
        for badge in Badge.objects.all():
            badge_record = BadgeRecords.objects.filter(badge=badge, user=request.user).first()
            if badge_record:
                unlocked = badge_record.unlocked
            else:
                unlocked = False

            badges_list.append({
                'name': badge.name,  # 名称
                'icon': badge.icon.url,  # 图标
                'description': badge.description,  # 描述
                'required_days': badge.required_days,  # 所需天数解锁
                'unlocked': unlocked, # 有可能会出现为None的现象
            })
        context = {
            'habits': user_habit_data,
            'today_checkins': today_checkins,
            'badges': badges_list,
        }

        return render(request, self.template_name, context=context)

    def check_and_award_badges(self, user):
        """检查并授予用户徽章"""
        badges = Badge.objects.all()
        for badge in badges:
            if user.habit_streak >= badge.required_days and badge not in user.badges.all():
                user.badges.add(badge)
                user.save()
                messages.success(user, f"恭喜！你获得了徽章：{badge.name}")


class CheckInCreateView(LoginRequiredMixin, View):

    def post(self, request):
        """
        处理用户提交的打卡请求。
        这个方法首先获取用户提交的表单数据，然后根据数据创建或更新用户的打卡记录。
        如果用户已经对这个习惯打过卡，则更新打卡记录的日期为当前日期。
        如果用户没有打过卡，则创建一个新的打卡记录。
        最后，重定向用户到用户仪表盘页面。
        参数:
        - request: HttpRequest对象，包含了用户提交的表单数据。
        返回:
        - 重定向到用户仪表盘页面的HttpResponseRedirect对象。
        """
        # 获取用户提交的表单数据

        habit_id = json.loads(request.body.decode('utf-8')).get('habit_id')
        habit = Habit.objects.filter(id=habit_id).first()  # 获取对应的习惯对象

        # 检查用户是否有这个习惯的打卡记录
        checkin = CheckIn.objects.filter(user=request.user, habit=habit).first()
        if checkin:
            # 如果用户今天已经对这个习惯打过卡，则不能再次打卡
            if habit.is_checked_in_today(request.user):
                messages.error(request, '今日已成功打卡！')
                return JsonResponse({'message': '今日已成功打卡！'}, status=400)
            else:
                # 如果用户昨天没有打卡，则重置连续打卡的天数
                if checkin.date != date.today() - timedelta(days=1):
                    checkin.streak = 1

                else:
                    checkin.streak += 1
                    checkin.total_checkins += 1
                checkin.save()
                return JsonResponse({'message': '打卡成功！'}, status=200)
        else:
            # 说明没有这个习惯，用户第一次打卡这个习惯
            CheckIn.objects.create(user=request.user, habit=habit, date=date.today(), streak=1, total_checkins=1)
            return JsonResponse({'message': '打卡成功！'}, status=200)
