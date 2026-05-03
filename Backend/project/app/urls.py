from django.urls import path
from .views import RegisterView, LoginView, AddIncomeView, AddExpenseView, MonthlyReportView, SetBudgetView, ViewBalanceView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('add-income/', AddIncomeView.as_view()),
    path('add-expense/', AddExpenseView.as_view()),
    path('report/', MonthlyReportView.as_view()),
    path('set-budget/', SetBudgetView),
    path('view-balance/', ViewBalanceView),
]