# family_quiz/urls.py

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('survey.urls')),  # 包含测试应用的URL
    path('', include('users.urls')),

]

# 仅在开发环境（DEBUG=True）提供媒体文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
