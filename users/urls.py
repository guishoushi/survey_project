from django.urls import path
from .views import *

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user_register'),
    path('login/', UserLoginView.as_view(), name='user_login'),
    path('logout/', UserLogoutView.as_view(), name='user_logout'),
    path('dashboard/', UserDashboardView.as_view(), name='user_dashboard'),
    path('', UserDashboardView.as_view(), name='user_dashboard'),
    path('habits/', CheckInCreateView.as_view(), name='checkin_create'),
    path('rankings/', RankingListView.as_view(), name='ranking_list'),
    path('badges/', BadgeListView.as_view(), name='badge_list'),
    path('profile/', UserProfileUpdateView.as_view(), name='user_profile'),
    # path('profile/edit/', UserUpdateView.as_view(), name='user_update'),
    # path('badges/', BadgeListView.as_view(), name='badge_list'),
]
