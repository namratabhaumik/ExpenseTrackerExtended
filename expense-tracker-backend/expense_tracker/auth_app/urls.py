from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('expenses/', views.add_expense, name='add_expense'),
    path('expenses/list/', views.get_expenses, name='get_expenses'),
    path('receipts/upload/', views.upload_receipt, name='upload_receipt'),
]
