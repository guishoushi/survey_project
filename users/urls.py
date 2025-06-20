from django.urls import path
from .views import *

urlpatterns = [
    # path('register/', UserRegistrationView.as_view(), name='user_register'),
    path('login/', UserLoginView.as_view(), name='user_login'),
    path('logout/', UserLogoutView.as_view(), name='user_logout'),
    path('dashboard/', UserDashboardView.as_view(), name='user_dashboard'),
    # path('habits/', HabitListView.as_view(), name='habit_list'),
    # path('habits/add/', HabitCreateView.as_view(), name='habit_create'),
    # path('habits/<int:pk>/', HabitDetailView.as_view(), name='habit_detail'),
    path('habits/', CheckInCreateView.as_view(), name='checkin_create'),
    # path('profile/', UserProfileView.as_view(), name='user_profile'),
    # path('profile/edit/', UserUpdateView.as_view(), name='user_update'),
    # path('badges/', BadgeListView.as_view(), name='badge_list'),
]
