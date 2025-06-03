from django.urls import path, include
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("home/", views.home, name="home"),
    path("report/", views.report, name="report"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/register/", views.register, name="register"),
    path("accounts/login/", views.register, name="login"),
    path("accounts/logout/", views.register, name="logout"),
    path("expenses", views.ExpenseListView.as_view(), name='expenses'),
    path("incomes", views.IncomeListView.as_view(), name='incomes'),
    path("expenses/edit/<int:expense_id>/", views.edit_expense, name='edit_expense'),
    path("incomes/edit/<int:income_id>/", views.edit_income, name='edit_income'),
    path("expenses/delete/<int:expense_id>/", views.delete_expense, name='delete_expense'),
    path("incomes/delete/<int:income_id>/", views.delete_income, name='delete_income'),
]
   