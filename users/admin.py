from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile, Badge, Habit, CheckIn, BadgeRecords
from django.contrib.admin.decorators import register


class CustomUserAdmin(UserAdmin):
    """自定义用户管理界面"""
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('个人信息', {'fields': ('username', 'first_name', 'last_name', 'email', 'avatar', 'bio')}),
        ('权限', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('重要日期', {'fields': ('last_login', 'date_joined')}),
        ('成就徽章', {'fields': ('badges',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'username', 'password1', 'password2'),
        }),
    )
    list_display = ('phone', 'username', 'is_staff')
    search_fields = ('phone', 'username', 'email')
    ordering = ('-date_joined',)


@register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    list_display = ('user', 'habit', 'date', 'streak', 'total_checkins', 'note', 'created_at')
    list_filter = ('user', 'habit', 'date')
    search_fields = ('user__username', 'habit__name')
    ordering = ('-date',)


@register(BadgeRecords)
class BadgeRecordsAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge', 'unlocked', 'unlocked_at')
    list_filter = ('user', 'badge', 'unlocked_at')
    list_editable = ('unlocked',)
    search_fields = ('user__username', 'badge__name')


@register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon','habit', 'description')
    list_editable = ('habit',)
    search_fields = ('name', 'description')


@register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name',)


admin.site.register(UserProfile, CustomUserAdmin)
