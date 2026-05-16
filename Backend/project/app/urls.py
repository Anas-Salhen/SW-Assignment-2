from django.urls import path
from . import views
from .views import RegisterView, LoginView, AddIncomeView, AddExpenseView, MonthlyReportView, SetBudgetView, ViewBalanceView

urlpatterns = [
    # HTML views
    path('', views.register_view, name='register'),
    path('login-view/', views.login_view, name='login'),
    path('register-view/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.index_view, name='home'),
    path('add/', views.add_transaction_view, name='add_transaction'),
    path('set-budget-view/', views.set_budget_view, name='set_budget_view'),
    path('view-balance-view/', views.view_balance_view, name='view_balance_view'),
    path('report-view/', views.report_view, name='report_view'),
    path('goals-view/', views.goals_view, name='goals_view'),
    # API endpoints
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('add-income/', AddIncomeView.as_view()),
    path('add-expense/', AddExpenseView.as_view()),
    path('report/', MonthlyReportView.as_view()),
    path('set-budget/', SetBudgetView.as_view(), name='set_budget'),
    path('view-balance/', ViewBalanceView.as_view(), name='view_balance'),
]