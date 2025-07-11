from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('confirm-signup/', views.confirm_signup_view, name='confirm_signup'),
    path('expenses/', views.add_expense, name='add_expense'),
    path('expenses/list/', views.get_expenses, name='get_expenses'),
    path('receipts/upload/', views.upload_receipt, name='upload_receipt'),
]
