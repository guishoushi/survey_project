# quiz/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Question(models.Model):
    CATEGORY_CHOICES = [
        ('communication', '沟通技巧'),
        ('discipline', '纪律与规则'),
        ('emotion', '情绪管理'),
        ('education', '学习教育'),
        ('values', '价值观培养'),
    ]

    question_text = models.TextField(verbose_name="问题内容")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="问题类别")
    explanation = models.TextField(blank=True, null=True, verbose_name="答案解析")

    def __str__(self):
        return f"{self.category} - {self.question_text[:30]}..."

    class Meta:
        verbose_name = "问卷题目"
        verbose_name_plural = "问卷题目"


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    option_text = models.CharField(max_length=200, verbose_name="选项内容")
    is_correct = models.BooleanField(default=False, verbose_name="是否正确")

    def __str__(self):
        return f"{self.option_text} - {self.question.question_text[:10]}"

    class Meta:
        verbose_name = "题目选项"
        verbose_name_plural = "题目选项"


class CampEnrollment(models.Model):
    # 营员信息
    name = models.CharField("姓名", max_length=100)
    gender = models.CharField("性别", max_length=10, choices=[('男', '男'), ('女', '女')])
    pickup_location = models.CharField("接送地点", max_length=200)
    birthdate = models.DateField("出生日期")
    hometown = models.CharField("籍贯", max_length=100)
    blood_type = models.CharField("血型", max_length=10, blank=True, choices=[
        ('A', 'A型'), ('B', 'B型'), ('AB', 'AB型'), ('O', 'O型'), ('other', '其他/未知')
    ])
    id_card = models.CharField("身份证号", max_length=20)
    height = models.FloatField("身高(cm)", validators=[MinValueValidator(50), MaxValueValidator(250)])
    weight = models.FloatField("体重(kg)", validators=[MinValueValidator(20), MaxValueValidator(200)])
    email = models.EmailField("电子邮箱", blank=True)
    hobbies = models.CharField("兴趣爱好", max_length=200, blank=True)
    specialty = models.CharField("个人专长", max_length=200, blank=True)
    school_class = models.CharField("学校及班级", max_length=200)

    # 训练营信息
    camp_type = models.CharField("训练营类型", max_length=50, choices=[
        ('15天训练营', '15天训练营'),
        ('15天将帅营', '15天将帅营'),
        ('30天训练营', '30天训练营'),
        ('30天将帅营', '30天将帅营'),

        ('45天训练营', '45天训练营'),
        ('45天将帅营', '45天将帅营'),
    ])
    camp_date = models.DateField("入营日期", blank=True, null=True)
    special_notes = models.TextField("特殊说明", blank=True)

    # 监护人信息
    guardian_name = models.CharField("监护人姓名", max_length=100)
    guardian_workplace = models.CharField("工作单位", max_length=200, blank=True)
    guardian_id_card = models.CharField("监护人身份证号", max_length=20)
    guardian_phone = models.CharField("监护人电话", max_length=20)
    relationship = models.CharField("与营员关系", max_length=20, choices=[
        ('父亲', '父亲'), ('母亲', '母亲'), ('祖父', '祖父'), ('祖母', '祖母'),
        ('外祖父', '外祖父'), ('外祖母', '外祖母'), ('其他亲属', '其他亲属'), ('其他', '其他')
    ])
    emergency_phone = models.CharField("紧急联系电话", max_length=20)
    address = models.CharField("家庭住址", max_length=300)
    postal_code = models.CharField("邮政编码", max_length=10)
    region = models.CharField("所属区域", max_length=100)

    # 签名
    signature = models.CharField("监护人签名", max_length=100)
    sign_date = models.DateField("签名日期")

    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "夏令营报名信息"
        verbose_name_plural = "夏令营报名信息"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.camp_type} ({self.camp_date})"

