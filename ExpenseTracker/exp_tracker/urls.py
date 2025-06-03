from django.urls import path, include
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("home/", views.home, name="home"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/register/", views.register, name="register"),
    path("accounts/login/", views.register, name="login"),
    path("accounts/logout/", views.register, name="logout"),
    path("expenses", views.ExpenseListView.as_view(), name='expenses'),
    path("expenses/edit/<int:expense_id>/", views.edit_expense, name='edit_expense'),
    path("expenses/delete/<int:expense_id>/", views.delete_expense, name='delete_expense'),
]
   