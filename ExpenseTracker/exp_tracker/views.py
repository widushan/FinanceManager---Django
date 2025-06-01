from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from exp_tracker import models
from .models import Account, Expense, Income
from django.views.generic.edit import FormView
from django.views.generic import ListView
from datetime import datetime
from .forms import ExpenseForm

import plotly.express as px
from plotly.graph_objects import *



# Create your views here.
def home(request):
    return render(request, 'home/home.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})




class ExpenseListView(FormView):
    template_name = 'home/expenses.html'
    form_class = ExpenseForm
    success_url = '/'

    def form_valid(self, form):
        account, _ = Account.objects.get_or_create(user=self.request.user)

        expense = Expense(
            name = form.cleaned_data['name'],
            amount = form.cleaned_data['amount'],
            interest_rate = form.cleaned_data['interest_rate'],
            date = form.cleaned_data['date'],
            end_date = form.cleaned_data['end_date'],
            long_term = form.cleaned_data['long_term'],
            user = self.request.user
        )
        expense.save()
        account.expense_list.add(expense)
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        accounts = Account.objects.filter(user=user)
        



