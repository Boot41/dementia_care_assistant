from django.urls import path
from .auth_register import register
from .auth_login import login_view
from .get_user import get_user
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .memory_assistant import process_user_input

from .activitysuggestion import activity_suggestion
from .riddlesgame import riddle_game
from .music_suggestion import music_recommendation
from .reminder_assistant import save_reminder, get_reminders









urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('memory_assistant/', process_user_input, name='process_user_input'),
    path('activitysuggestion/', activity_suggestion, name='activity_suggestion'),
    path('riddlesgame/', riddle_game, name='riddle_game'),
    path('music_suggestion/', music_recommendation, name='music_recommendation'),
    path('save_reminder/', save_reminder, name='save_reminder'),
    path('get_reminders/', get_reminders, name='get_reminders'),


    



]
