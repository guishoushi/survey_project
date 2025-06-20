from django import forms
from .models import Question

from django import forms
from .models import CampEnrollment
import datetime


class SurveyForm(forms.Form):
    name = forms.CharField(label='您的姓名', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        questions = kwargs.pop('questions', [])
        super(SurveyForm, self).__init__(*args, **kwargs)

        for question in questions:
            field_name = f'q_{question.id}'
            if question.type == Question.TEXT:
                self.fields[field_name] = forms.CharField(
                    label=question.text,
                    widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
                    required=True
                )
            elif question.type == Question.CHOICE:
                self.fields[field_name] = forms.ChoiceField(
                    label=question.text,
                    choices=[(c, c) for c in question.get_choices()],
                    widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
                    required=True
                )
            elif question.type == Question.MULTIPLE:
                self.fields[field_name] = forms.MultipleChoiceField(
                    label=question.text,
                    choices=[(c, c) for c in question.get_choices()],
                    widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
                    required=False
                )


class CampEnrollmentForm(forms.ModelForm):
    camp_date_15 = forms.DateField(required=False, widget=forms.DateInput(
        attrs={'type': 'date', 'placeholder': '入营日期'}))
    camp_date_15_commander = forms.DateField(required=False, widget=forms.DateInput(
        attrs={'type': 'date', 'placeholder': '入营日期'}))
    camp_date_30 = forms.DateField(required=False, widget=forms.DateInput(
        attrs={'type': 'date', 'placeholder': '入营日期'}))
    camp_date_30_commander = forms.DateField(required=False, widget=forms.DateInput(
        attrs={'type': 'date', 'placeholder': '入营日期'}))
    camp_date_45 = forms.DateField(required=False, widget=forms.DateInput(
        attrs={'type': 'date', 'placeholder': '入营日期'}))
    camp_date_45_commander = forms.DateField(required=False, widget=forms.DateInput(
        attrs={'type': 'date', 'placeholder': '入营日期'}))

    class Meta:
        model = CampEnrollment
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': '请输入营员姓名'}),
            'gender': forms.Select(attrs={'placeholder': '请选择性别'}),
            'pickup_location': forms.TextInput(attrs={'placeholder': '请输入接送地点'}),
            'birthdate': forms.DateInput(attrs={'type': 'date'}),
            'hometown': forms.TextInput(attrs={'placeholder': '请输入籍贯'}),
            'blood_type': forms.Select(attrs={'placeholder': '请选择血型'}),
            'id_card': forms.TextInput(attrs={'placeholder': '请输入身份证号码'}),
            'height': forms.NumberInput(attrs={'placeholder': '请输入身高'}),
            'weight': forms.NumberInput(attrs={'placeholder': '请输入体重'}),
            'email': forms.EmailInput(attrs={'placeholder': '请输入电子邮箱'}),
            'hobbies': forms.TextInput(attrs={'placeholder': '请输入兴趣爱好'}),
            'specialty': forms.TextInput(attrs={'placeholder': '请输入个人专长'}),
            'school_class': forms.TextInput(attrs={'placeholder': '例如：上海市第一中学 高一(3)班'}),

            # 监护人信息
            'guardian_name': forms.TextInput(attrs={'placeholder': '请输入监护人姓名'}),
            'guardian_workplace': forms.TextInput(attrs={'placeholder': '请输入工作单位'}),
            'guardian_id_card': forms.TextInput(attrs={'placeholder': '请输入监护人身份证号码'}),
            'guardian_phone': forms.TextInput(attrs={'placeholder': '请输入联系电话'}),
            'relationship': forms.Select(attrs={'placeholder': '请选择关系'}),
            'emergency_phone': forms.TextInput(attrs={'placeholder': '请输入紧急联系电话'}),
            'address': forms.TextInput(attrs={'placeholder': '请输入详细家庭住址'}),
            'postal_code': forms.TextInput(attrs={'placeholder': '请输入邮政编码'}),
            'region': forms.TextInput(attrs={'placeholder': '例如：上海市徐汇区'}),
            'signature': forms.TextInput(attrs={'placeholder': '请在此签名'}),
            'sign_date': forms.DateInput(attrs={'type': 'date'}),

            'special_notes': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': '请详细描述您希望孩子在夏令营中得到改善的问题或习惯'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.initial['sign_date'] = datetime.date.today()

        # 设置选择字段的占位符为空标签
        self.fields['gender'].empty_label = "请选择性别"
        self.fields['blood_type'].empty_label = "请选择血型"
        self.fields['relationship'].empty_label = "请选择关系"

    def clean(self):
        cleaned_data = super().clean()

        # 仅保存用户选择的日期字段值
        camp_type = cleaned_data.get('camp_type')
        camp_date = None

        # 验证训练营类型和日期
        if camp_type:
            # 根据训练营类型确定对应的日期字段
            if camp_type == '15天训练营':
                camp_date = cleaned_data.get('camp_date_15')
            elif camp_type == '15天将帅营':
                camp_date = cleaned_data.get('camp_date_15_commander')
            elif camp_type == '30天训练营':
                camp_date = cleaned_data.get('camp_date_30')
            elif camp_type == '30天将帅营':
                camp_date = cleaned_data.get('camp_date_30_commander')
            elif camp_type == '45天训练营':
                camp_date = cleaned_data.get('camp_date_45')
            elif camp_type == '45天将帅营':
                camp_date = cleaned_data.get('camp_date_45_commander')

            # 仅设置值，不进行验证
            cleaned_data['camp_date'] = camp_date

        # 验证出生日期（保留此验证）
        birthdate = cleaned_data.get('birthdate')
        camp_date = cleaned_data.get('camp_date')

        if birthdate and camp_date:
            # 计算参加夏令营时的年龄
            age_at_camp = camp_date.year - birthdate.year - (
                    (camp_date.month, camp_date.day) < (birthdate.month, birthdate.day))

            # 检查年龄是否在6-18岁之间
            if age_at_camp < 6 or age_at_camp > 18:
                self.add_error('birthdate', "营员年龄需在6-18岁之间")

        return cleaned_data
