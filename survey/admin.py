# quiz/admin.py
from django.contrib import admin
from .models import Question, Option, CampEnrollment
from import_export.admin import ImportExportModelAdmin
from import_export.formats.base_formats import XLSX, JSON, HTML  # 导入所需格式


class OptionInline(admin.TabularInline):
    model = Option
    extra = 4


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'category', 'explanation']
    list_filter = ['category']
    inlines = [OptionInline]
    search_fields = ['question_text']


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ['option_text', 'question', 'is_correct']
    list_filter = ['question__category', 'is_correct']
    search_fields = ['option_text']


@admin.register(CampEnrollment)
class CampEnrollmentAdmin(ImportExportModelAdmin):
    formats = [XLSX, JSON, HTML]  # 包含所有需要的格式

    def get_export_formats(self):
        """强制启用所有声明的格式"""
        return [f for f in self.formats if f().can_export()]

    # 列表页配置
    list_display = (
        'name',
        'gender',
        'camp_type',
        'camp_date',
        'birthdate',
        'school_class',
        'guardian_name',
        'relationship',
        'guardian_phone',
        'created_at'
    )
    list_filter = (
        'created_at',
        'camp_type',
        'gender',
        'relationship'
    )
    search_fields = (
        'name',
        'guardian_name',
        'guardian_phone',
        'emergency_phone',
        'id_card',
        'guardian_id_card',
        'email',
        'school_class'
    )
    list_per_page = 50
    date_hierarchy = 'created_at'

    # 详情页配置
    fieldsets = (
        ('营员信息', {
            'fields': (
                'name', 'gender', 'birthdate', 'height', 'weight',
                'id_card', 'blood_type', 'hobbies', 'specialty',
                'school_class', 'hometown', 'email'
            )
        }),
        ('训练营信息', {
            'fields': (
                'camp_type', 'camp_date', 'special_notes', 'pickup_location'
            )
        }),
        ('监护人信息', {
            'fields': (
                'guardian_name', 'guardian_workplace', 'relationship',
                'guardian_id_card', 'guardian_phone', 'emergency_phone',
                'address', 'postal_code', 'region'
            )
        }),
        ('签名与日期', {
            'fields': (
                'signature', 'sign_date'
            )
        }),
        ('系统信息', {
            'fields': (
                'created_at',
            )
        })
    )

    # 只读字段
    readonly_fields = ('created_at',)

    # 导出功能
    actions = ['export_as_csv']

    def export_as_csv(self, request, queryset):
        """
        导出选中项为 CSV 文件
        """
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = 'attachment; filename="camp_enrollments.csv"'

        writer = csv.writer(response)

        # 写入表头
        writer.writerow([
            '姓名', '性别', '出生日期', '身高(cm)', '体重(kg)',
            '身份证号', '血型', '兴趣爱好', '个人专长', '学校及班级',
            '籍贯', '电子邮箱', '训练营类型', '入营日期', '特殊说明',
            '接送地点', '监护人姓名', '工作单位', '关系', '监护人身份证',
            '监护人电话', '紧急电话', '家庭住址', '邮政编码', '所属区域',
            '签名', '签名日期', '报名时间'
        ])

        # 写入数据
        for obj in queryset:
            writer.writerow([
                obj.name, obj.gender, obj.birthdate, obj.height, obj.weight,
                obj.id_card, obj.blood_type, obj.hobbies, obj.specialty,
                obj.school_class, obj.hometown, obj.email, obj.camp_type,
                obj.camp_date, obj.special_notes, obj.pickup_location,
                obj.guardian_name, obj.guardian_workplace, obj.relationship,
                obj.guardian_id_card, obj.guardian_phone, obj.emergency_phone,
                obj.address, obj.postal_code, obj.region, obj.signature,
                obj.sign_date, obj.created_at.strftime("%Y-%m-%d %H:%M:%S")
            ])

        return response

    export_as_csv.short_description = "导出选中项为 CSV"


admin.site.site_header = '西点好习惯夏令营管理后台'
admin.site.site_title = '夏令营报名系统'
admin.site.index_title = '系统管理'
