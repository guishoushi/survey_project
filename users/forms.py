from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from .models import UserProfile, Habit, CheckIn


class UserRegistrationForm(UserCreationForm):
    """用户注册表单"""
    phone = forms.CharField(
        label="手机号",
        max_length=11,
        widget=forms.TextInput(attrs={
            'class': 'w-full pl-12 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all placeholder-gray-400',
            'placeholder': '请输入手机号'
        }),
        help_text="请输入有效的11位手机号码"
    )
    password1 = forms.CharField(
        label="密码",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full pl-12 pr-12 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all placeholder-gray-400',
            'placeholder': '设置6-16位密码'
        }),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label="确认密码",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full pl-12 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all placeholder-gray-400',
            'placeholder': '请再次输入密码'
        }),
        strip=False,
        help_text="请再次输入相同的密码",
    )

    class Meta:
        model = UserProfile
        fields = ('phone', 'username')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full pl-12 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all placeholder-gray-400',
                'placeholder': '给自己起个特别的昵称'
            }),
        }


class UserLoginForm(AuthenticationForm):
    """用户登录表单"""
    username = forms.CharField(
        label="手机号",
        widget=forms.TextInput(attrs={'placeholder': '请输入手机号', 'class': 'form-control'})
    )
    password = forms.CharField(
        label="密码",
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': '请输入密码', 'class': 'form-control'}),
    )


class HabitForm(forms.ModelForm):
    """习惯创建/编辑表单"""
    name = forms.CharField(
        label="习惯名称",
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': '例如：每天阅读30分钟', 'class': 'form-control'})
    )
    category = forms.CharField(
        label="习惯类别",
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '例如：学习、健康', 'class': 'form-control'})
    )
    target_days = forms.IntegerField(
        label="目标坚持天数",
        min_value=1,
        max_value=365,
        initial=21,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Habit
        fields = ('name', 'category', 'target_days')


class CheckInForm(forms.ModelForm):
    """打卡表单"""
    note = forms.CharField(
        label="打卡备注",
        required=False,
        max_length=200,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': '记录今天的完成情况...',
            'class': 'form-control'
        })
    )

    class Meta:
        model = CheckIn
        fields = ('note',)


User = get_user_model()


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'bio', 'avatar']
        labels = {
            'username': _('用户名'),
            'bio': _('个人简介'),
            'avatar': _('头像'),
        }
        help_texts = {
            'username': _('2-16个字符，支持中文、字母和数字'),
            'bio': _('分享您的成长历程（不超过500字）'),
            'avatar': _('支持JPG、PNG、WebP格式，大小不超过5MB'),
        }
        error_messages = {
            'username': {
                'min_length': _('用户名长度需在2-16个字符之间'),
                'max_length': _('用户名长度需在2-16个字符之间'),
                'unique': _('该用户名已被使用'),
            }
        }
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 为头像字段添加特定属性
        self.fields['avatar'].widget.attrs = {
            'class': 'file-input',
            'accept': 'image/*'
        }

        # 为字段添加额外的类
        self.fields['username'].widget.attrs.update({'class': 'input-field'})
        self.fields['bio'].widget.attrs.update({'class': 'bio-field'})

        # 移除头像字段的必填属性
        self.fields['avatar'].required = False

    def clean_username(self):
        username = self.cleaned_data['username'].strip()

        # 检查用户名是否唯一（排除当前用户）
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise ValidationError(_('该用户名已被使用'))

        return username

    def clean_bio(self):
        bio = self.cleaned_data.get('bio', '')
        if len(bio) > 500:
            raise ValidationError(_('个人简介不能超过500个字符'))
        return bio

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')

        # 只有当是新的上传文件时才进行验证
        if avatar and hasattr(avatar, 'content_type'):
            # 验证文件格式
            file_type = avatar.content_type
            valid_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']

            # 获取文件扩展名
            ext = avatar.name.split('.')[-1].lower() if '.' in avatar.name else '未知格式'

            if file_type not in valid_types:
                raise ValidationError(_(f'不支持的文件格式: .{ext}。仅支持JPEG、PNG、GIF或WebP格式的图片'))

            # 验证文件大小 (最大5MB)
            max_size = 5 * 1024 * 1024  # 5MB
            if avatar.size > max_size:
                size_mb = avatar.size / (1024 * 1024)
                raise ValidationError(_(f'头像大小({size_mb:.1f}MB)不能超过5MB'))

        # 返回验证后的头像
        return avatar
