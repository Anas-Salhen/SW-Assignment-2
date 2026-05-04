from django.urls import path
from . import views 
from .views import RegisterView, LoginView, AddIncomeView, AddExpenseView, MonthlyReportView, SetBudgetView, ViewBalanceView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('add-income/', AddIncomeView.as_view()),
    path('add-expense/', AddExpenseView.as_view()),
    path('report/', MonthlyReportView.as_view()),
    path('set-budget/', SetBudgetView.as_view(), name='set_budget'),
    path('view-balance/', ViewBalanceView.as_view(), name='view_balance'),
    
    path('home/', views.index_view, name='home'),
    path('add/', views.add_transaction_view, name='add_transaction'),
]