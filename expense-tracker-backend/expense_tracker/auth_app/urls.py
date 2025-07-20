from django.urls import path
from . import views
from .views import (
    login_view,
    signup_view,
    confirm_signup_view,
    forgot_password_view,
    confirm_forgot_password_view,
    verify_reset_code_view,
    profile_view,
    change_password_view,
)

urlpatterns = [
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('confirm-signup/', confirm_signup_view, name='confirm_signup'),
    path('forgot-password/', forgot_password_view, name='forgot_password'),
    path('confirm-forgot-password/', confirm_forgot_password_view,
         name='confirm_forgot_password'),
    path('verify-reset-code/', verify_reset_code_view, name='verify_reset_code'),
    path('profile/', profile_view, name='profile'),
    path('profile/change-password/', change_password_view, name='change_password'),
    path('expenses/', views.add_expense, name='add_expense'),
    path('expenses/list/', views.get_expenses, name='get_expenses'),
    path('receipts/upload/', views.upload_receipt, name='upload_receipt'),
    path('healthz/', views.healthz, name='healthz'),
]
