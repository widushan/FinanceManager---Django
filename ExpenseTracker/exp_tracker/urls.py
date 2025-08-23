from django.urls import path, include
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("home/", views.home, name="home"),
    path("report/", views.report, name="report"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/register/", views.register, name="register"),
    # Login handled by django.contrib.auth.urls
    
    path("expenses", views.ExpenseListView.as_view(), name='expenses'),
    path("incomes", views.IncomeListView.as_view(), name='incomes'),
    path("expenses/edit/<int:expense_id>/", views.edit_expense, name='edit_expense'),
    path("incomes/edit/<int:income_id>/", views.edit_income, name='edit_income'),
    path("expenses/delete/<int:expense_id>/", views.delete_expense, name='delete_expense'),
    path("incomes/delete/<int:income_id>/", views.delete_income, name='delete_income'),
    
    # AI/ML Features
    path("ai-insights/", views.ai_insights, name='ai_insights'),
    path("api/train-model/", views.train_ml_model, name='train_ml_model'),
    path("api/predict-expenses/", views.get_expense_prediction, name='get_expense_prediction'),
    path("api/anomalies/", views.get_anomalies, name='get_anomalies'),
]
   