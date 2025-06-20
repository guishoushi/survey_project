from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from .models import UserProfile, Habit, CheckIn


class UserRegistrationForm(UserCreationForm):
    """用户注册表单"""
    phone = forms.CharField(
        label="手机号",
        max_length=11,
        widget=forms.TextInput(attrs={'placeholder': '请输入手机号', 'class': 'form-control'}),
        help_text="请输入有效的11位手机号码"
    )
    password1 = forms.CharField(
        label="密码",
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': '请输入密码', 'class': 'form-control'}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label="确认密码",
        widget=forms.PasswordInput(attrs={'placeholder': '请再次输入密码', 'class': 'form-control'}),
        strip=False,
        help_text="请再次输入相同的密码",
    )

    class Meta:
        model = UserProfile
        fields = ('phone', 'username')
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': '请输入用户名', 'class': 'form-control'}),
        }

    def clean_phone(self):
        phone = self.cleaned_data["phone"]
        if UserProfile.objects.filter(phone=phone).exists():
            raise ValidationError("该手机号已被注册")
        return phone


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
