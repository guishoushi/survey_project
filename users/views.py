import json, os

from django.core.files.storage import default_storage
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import date, timedelta, timezone

from django.views.generic import UpdateView

from .models import UserProfile, Habit, CheckIn, Badge, BadgeRecords
from .forms import UserRegistrationForm, UserLoginForm, ProfileForm


class UserRegistrationView(View):
    """用户注册视图"""

    def get(self, request):
        form = UserRegistrationForm()
        return render(request, 'register.html', {'form': form})

    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '注册成功！')
            return redirect('user_dashboard')
        return render(request, 'register.html', {'form': form})


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
                'unlocked': unlocked,  # 是否解锁,
                'habit_name': badge.habit.name,  # 勋章对应的习惯名称
            })
        # 渲染报告信息
        # 获取用户总打卡次数
        total_punches = CheckIn.objects.filter(user=request.user).values_list('total_checkins', flat=True)
        # 获取用户解锁徽章的总数
        total_badges = BadgeRecords.objects.filter(user=request.user).count()
        # 计算用户打卡进度的完成率
        finish_ratio = 0
        record_list = CheckIn.objects.filter(user=request.user)
        if record_list:

            for checkin in record_list:
                finish_ratio += checkin.streak / sum(Habit.objects.all().values_list('goal', flat=True)) * 100

            finish_ratio = round(finish_ratio, 2)
        else:
            record_list = [1, ]

        # 计算用户的等级
        if finish_ratio >= 95:
            level = 'A+ 卓越'
        elif finish_ratio >= 85:
            level = 'A 优秀'
        elif finish_ratio >= 75:
            level = 'B 达标'
        elif finish_ratio >= 65:
            level = 'C 发展中'
        else:
            level = 'D 未达标'

        # 渲染用户排行榜
        user_ranking = UserProfile.objects.all()[:3]
        user_list = []
        for user in user_ranking:
            if user.checkins.all().values_list('streak', flat=True):
                completion_rate = round(sum(user.checkins.all().values_list('streak', flat=True)) / sum(
                    Habit.objects.all().values_list('goal', flat=True)) * 100, 2)
                level = 'A+ 卓越' if completion_rate >= 95 else 'A 优秀' if completion_rate >= 85 else 'B 达标' if completion_rate >= 75 else 'C 发展中' if completion_rate >= 65 else 'D 未达标'

                user_list.append({
                    'username': user.username,
                    'streak': max(user.checkins.all().values_list('streak', flat=True)),
                    'total_number': sum(user.checkins.all().values_list('total_checkins', flat=True)),
                    'unlocked_badge_count': BadgeRecords.objects.filter(user=user).count(),
                    'completion_rate': completion_rate,
                    'level': level,
                })
            else:
                user_list.append({
                    'username': user.username,
                    'streak': 0,
                    'total_number': 0,
                    'unlocked_badge_count': 0,
                    'completion_rate': 0,
                    'level': 'D 未达标'
                })

        def sort_users(users):
            return sorted(users, key=lambda x: (
                -x['completion_rate'],  # 完成率降序（高的在前）
                -x['streak'],  # 连续打卡天数降序
                -x['unlocked_badge_count'],  # 解锁徽章数量降序
                -x['total_number'],  # 总任务数量降序
                x['username']  # 用户名升序
            ))

        # 排序并打印结果
        sorted_users = sort_users(user_list)
        context = {
            'habits': user_habit_data,
            'today_checkins': today_checkins,
            'badges': badges_list,
            'total_punches': sum(total_punches),
            'total_badges': total_badges,
            'finish_ratio': finish_ratio,
            'level': level,
            'user_ranking': sorted_users
        }

        return render(request, self.template_name, context=context)

    def check_and_award_badges(self, user):
        """检查并授予用户徽章"""
        checkin = CheckIn.objects.filter(user=user)
        badges = Badge.objects.all()
        for check in checkin:  # 遍历每个用户的打卡记录
            for badge in badges.filter(habit=check.habit):
                if check.streak >= badge.required_days and not BadgeRecords.objects.filter(badge=badge,
                                                                                           user=user).first():
                    BadgeRecords.objects.create(badge=badge, user=user, unlocked=True)


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


class RankingListView(LoginRequiredMixin, View):
    template_name = 'ranking.html'

    def get(self, request):
        # 渲染用户排行榜
        user_ranking = UserProfile.objects.all()
        user_list = []
        for user in user_ranking:
            if user.checkins.all().values_list('streak', flat=True):
                completion_rate = round(
                    sum(user.checkins.all().values_list('streak', flat=True)) / sum(
                        Habit.objects.all().values_list('goal', flat=True)) * 100, 2)
                level = 'A+ 卓越' if completion_rate >= 95 else 'A 优秀' if completion_rate >= 85 else 'B 达标' if completion_rate >= 75 else 'C 发展中' if completion_rate >= 65 else 'D 未达标'
                user_list.append({
                    'username': user.username,
                    'streak': max(user.checkins.all().values_list('streak', flat=True)),
                    'total_number': sum(user.checkins.all().values_list('total_checkins', flat=True)),
                    'unlocked_badge_count': BadgeRecords.objects.filter(user=user).count(),
                    'completion_rate': completion_rate,
                    'level': level
                })
            else:
                user_list.append({
                    'username': user.username,
                    'streak': 0,
                    'total_number': 0,
                    'unlocked_badge_count': 0,
                    'completion_rate': 0,
                    'level': 'D 未达标'
                })

        def sort_users(users):
            return sorted(users, key=lambda x: (
                -x['completion_rate'],  # 完成率降序（高的在前）
                -x['streak'],  # 连续打卡天数降序
                -x['unlocked_badge_count'],  # 解锁徽章数量降序
                -x['total_number'],  # 总任务数量降序
                x['username']  # 用户名升序
            ))

        # 排序并打印结果
        sorted_users = sort_users(user_list)

        # 查询进7天的打卡人数趋势
        # 1. 获取日期范围
        end_date = date.today()
        start_date = end_date - timedelta(days=6)  # 过去7天（包括今天）

        # 2. 查询并聚合数据
        daily_users = (
            CheckIn.objects
            .filter(date__range=[start_date, end_date])
            .values('date')  # 按日期分组
            .annotate(count=Count('user_id', distinct=True))  # 统计独立用户数
            .order_by('date')
        )

        # 3. 构建结果字典
        result_dict = {entry['date']: entry['count'] for entry in daily_users}

        # 4. 补全缺失日期（可选）
        full_trend = {'date': [], 'count': []}
        for i in range(7):
            current_date = start_date + timedelta(days=i)
            full_trend['date'].append(current_date.strftime('%m-%d'))
            full_trend['count'].append(result_dict.get(current_date, 0))  # 无数据则返回0

        context = {
            'user_ranking': sorted_users,
            'trend': full_trend,
        }
        return render(request, self.template_name, context=context)


class BadgeListView(LoginRequiredMixin, View):
    """
    BadgeListView类继承自LoginRequiredMixin和View类，表示该视图需要登录才能访问。
    """
    template_name = 'badges.html'

    def get(self, request):
        # 渲染勋章的逻辑
        badges_list = []
        # 遍历所有的勋章
        for badge in Badge.objects.all():
            badge_record = BadgeRecords.objects.filter(badge=badge, user=request.user).first()
            if badge_record:
                unlocked = badge_record.unlocked
                unlock_time = badge_record.unlocked_at.strftime('%Y-%m-%d')
            else:
                unlocked = False
                unlock_time = None
            badges_list.append({
                'name': badge.name,  # 名称
                'icon': badge.icon.url,  # 图标
                'description': badge.description,  # 描述
                'required_days': badge.required_days,  # 所需天数解锁
                'unlocked': unlocked,  # 是否解锁,
                'habit_name': badge.habit.name,  # 勋章对应的习惯名称,
                'unlock_time': unlock_time,  # 解锁时间,
                'days_until_unlock': badge.required_days - (record.streak if (
                    record := CheckIn.objects.filter(user=request.user, habit=badge.habit).first()) else 0),
                # 使用三元表达式处理记录存在/不存在的情况，还需要多少天解锁
            })
            # 统计解锁与未解锁数量
        unlocked_count = sum(1 for badge in badges_list if badge['unlocked'])
        locked_count = sum(1 for badge in badges_list if not badge['unlocked'])
        context = {
            'badges': badges_list,
            'user': request.user,
            'unlocked_count': unlocked_count,
            'locked_count': locked_count,
            'completion_rate': round(unlocked_count / len(badges_list) * 100, 2),
        }
        return render(request, self.template_name, context=context)


class UserProfileView(LoginRequiredMixin, View):
    template_name = 'profile.html'

    def get(self, request):
        # 获取用户信息
        user = request.user
        # 获取用户习惯列表
        habits = CheckIn.objects.filter(user=user)
        # 获取用户打卡记录列表
        checkins = user.checkins.all()
        # 获取用户解锁的徽章列表
        badges = user.badge_records.all()

        # 计算用户打卡进度的完成率
        finish_ratio = 0
        record_list = CheckIn.objects.filter(user=user)
        if record_list:
            for checkin in record_list:
                finish_ratio += checkin.streak / sum(Habit.objects.all().values_list('goal', flat=True)) * 100
            finish_ratio = round(finish_ratio, 2)  # 渲染用户信息
        context = {
            'user': user,
            'habits': habits,
            'checkins': checkins,
            'badges': badges,
            'finish_ratio': finish_ratio,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        pass


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = ProfileForm
    template_name = 'profile.html'
    success_url = reverse_lazy('user_profile')

    def get_object(self, queryset=None):
        """获取当前登录用户"""
        return self.request.user

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        """处理表单验证成功的情况"""
        self.object = form.save()

        # 如果请求是AJAX，返回JSON响应
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'username': self.object.username,
                'avatar_url': self.object.avatar.url if self.object.avatar else '/static/images/default_avatar.png',
                'bio': self.object.bio,
                'message': '账户信息已成功更新！'
            })
        # 否则正常重定向
        return super().form_valid(form)

    def form_invalid(self, form):
        """处理表单验证失败的情况"""
        # 如果请求是AJAX，返回带有错误信息的JSON响应
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # 转换表单错误为字段名:错误信息的字典
            errors = {field: list(error_list)[0] for field, error_list in form.errors.items()}
            return JsonResponse({'success': False, 'errors': errors})

        # 否则正常处理表单错误
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        """添加上下文数据"""
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        # 添加CSRF令牌到上下文
        context['csrf_token'] = self.request.COOKIES.get('csrftoken', '')
        # 连续打卡次数
        attendance_records = CheckIn.objects.filter(user=self.request.user).values_list('streak', flat=True)
        context['streak'] = max(attendance_records) if attendance_records else 0
        # 总打卡次数
        total_punch_card = CheckIn.objects.filter(user=self.request.user).values_list('total_checkins', flat=True)
        context['total_checkins'] = max(total_punch_card) if total_punch_card else 0
        # 解锁的徽章数量
        unlocked_badge_count = BadgeRecords.objects.filter(user=self.request.user)
        context['unlocked_badge_count'] = unlocked_badge_count.count()
        # 渲染勋章的逻辑
        badges_list = []
        # 遍历所有的勋章
        for badge in Badge.objects.all():
            badge_record = BadgeRecords.objects.filter(badge=badge, user=self.request.user).first()
            if badge_record:
                unlocked = badge_record.unlocked
                unlock_time = badge_record.unlocked_at.strftime('%Y-%m-%d')
            else:
                unlocked = False
                unlock_time = None
            badges_list.append({
                'name': badge.name,  # 名称
                'icon': badge.icon.url,  # 图标
                'description': badge.description,  # 描述
                'required_days': badge.required_days,  # 所需天数解锁
                'unlocked': unlocked,  # 是否解锁,
                'habit_name': badge.habit.name,  # 勋章对应的习惯名称,
                'unlock_time': unlock_time,  # 解锁时间,
                'days_until_unlock': badge.required_days - (record.streak if (
                    record := CheckIn.objects.filter(user=self.request.user, habit=badge.habit).first()) else 0),
                # 使用三元表达式处理记录存在/不存在的情况，还需要多少天解锁
            })
        context['badges_list'] = badges_list
        return context
