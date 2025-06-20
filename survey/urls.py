# quiz/urls.py
from django.urls import path
from .views import quiz_view,report_view,camp_enrollment

urlpatterns = [
    path('quiz/', quiz_view, name='quiz'),
    path('report/', report_view, name='report'),
    path('enrollment/', camp_enrollment, name='enrollment'),
]