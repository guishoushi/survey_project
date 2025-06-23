from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class UserProfile(AbstractUser):
    """自定义用户模型"""
    phone = models.CharField(_("手机号"), max_length=11, unique=True, help_text=_("必填。11位手机号码"),
                             error_messages={'unique': _("该手机号已被注册。")})
    avatar = models.ImageField(_("头像"), upload_to='avatars/', blank=True, default='avatars/default.png')
    bio = models.TextField(_("个人简介"), blank=True, max_length=500)
    badges = models.ManyToManyField('Badge', verbose_name=_("成就徽章"), blank=True)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = _("用户")
        verbose_name_plural = _("用户")


class Habit(models.Model):
    """习惯模型"""
    name = models.CharField(_("习惯名称"), max_length=50)
    icon = models.ImageField(_("习惯图标"), upload_to='habits/', blank=True, default='habits/default.png')
    created_at = models.DateTimeField(_("创建时间"), auto_now_add=True)
    goal = models.IntegerField(_("目标坚持天数"), default=21)
    is_active = models.BooleanField(_("是否活跃"), default=True)

    def is_checked_in_today(self, user):
        """
        检查当前用户今天是否已对该习惯打卡

        参数:
        user: 执行检查的用户对象，用于确定是哪个用户的打卡记录

        返回:
        如果用户今天已经对这个习惯打过卡，返回True；否则返回False
        """
        # 获取当前日期，只考虑日期部分，不包括时间
        today = timezone.now().date()
        # 检查是否存在属于当前用户且日期为今天的打卡记录
        return self.checkins.filter(
            user=user,
            date=today
        ).exists()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("习惯")
        verbose_name_plural = _("习惯")


class CheckIn(models.Model):
    """打卡记录模型"""
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name="checkins", verbose_name=_("习惯"))
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="checkins", verbose_name=_("用户"))
    streak = models.IntegerField(_("当前连续打卡"), default=0)
    total_checkins = models.IntegerField(_("总打卡次数"), default=0)
    date = models.DateField(_("打卡日期"), auto_now=True)
    note = models.TextField(_("打卡备注"), blank=True, max_length=200)
    created_at = models.DateTimeField(_("记录时间"), auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} 的 {self.habit.name} 打卡记录"

    class Meta:
        verbose_name = _("习惯记录")
        verbose_name_plural = _("习惯记录")
        unique_together = ('habit', 'user', 'date')


class Badge(models.Model):
    """成就徽章模型"""
    name = models.CharField(_("徽章名称"), max_length=50)
    description = models.CharField(_("徽章描述"), max_length=200)
    icon = models.ImageField(_("徽章图标"), upload_to='badges/', blank=True, default='badges/default.png')
    required_days = models.IntegerField(_("所需连续打卡天数"), default=7)
    # 关联习惯
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name="badges", verbose_name=_("习惯"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("成就徽章")
        verbose_name_plural = _("成就徽章")


class BadgeRecords(models.Model):
    """用户获得的徽章记录模型"""
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="badge_records",
                             verbose_name=_("用户"))
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name="badge_records", verbose_name=_("徽章"))
    unlocked = models.BooleanField(_("是否解锁"), default=False)
    unlocked_at = models.DateTimeField(_("解锁时间"), auto_now_add=True)

    class Meta:
        verbose_name = _("徽章记录")
        verbose_name_plural = _("徽章记录")
        unique_together = ('user', 'badge')

    def __str__(self):
        return f"{self.user.username} 的 {self.badge.name} 徽章"
