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
from dateutil.relativedelta import relativedelta
from django.utils.safestring import mark_safe
from django.db.models import Sum, Count, F
import plotly.express as px
from plotly.graph_objs import *



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


def generate_graph(data):
    fig = px.bar(data, x='months', y='expenses', title='Monthly Expenses')
    fig.update_layout(
        xaxis = dict(rangeslider=dict(visible=True)),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='rgba(0,0,0,1)',
        
    )
    fig.update_traces(marker_color='#008c41')

    graph_json = fig.to_json()
    return graph_json




class ExpenseListView(FormView):
    template_name = 'exp_tracker/expenses_list.html'
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
        
        expense_data_graph = {}
        expense_data = {}

        for account in accounts:
            expenses = account.expense_list.all()
            for expense in expenses:
                if expense.long_term and expense.monthly_expenses:
                    current_date = expense.date
                    while current_date <= expense.end_date:
                        year_month = current_date.strftime('%Y-%m')
                        if year_month not in expense_data_graph:
                            expense_data_graph[year_month] = []

                        expense_data_graph[year_month].append({
                            'name': expense.name,
                            'amount': expense.monthly_expenses,
                            'date': expense.date,
                            'end_date': expense.end_date,
                        })
                        current_date += relativedelta(months=1)
                else:
                    year_month = expense.date.strftime('%Y-%m')
                    if year_month not in expense_data_graph:
                        expense_data_graph[year_month] = []
                    
                    expense_data_graph[year_month].append({
                        'name': expense.name,
                        'amount': expense.amount,
                        'date': expense.date,
                        
                    })
  
        for account in accounts:
            expenses = account.expense_list.all()
            for expense in expenses:
                if expense.long_term and expense.monthly_expenses:
                    current_date = expense.date
                    year_month = current_date.strftime('%Y-%m')
                    if year_month not in expense_data_graph:
                        expense_data[year_month] = []

                        expense_data[year_month].append({
                            'name': expense.name,
                            'amount': expense.monthly_expenses,
                            'date': expense.date,
                            'end_date': expense.end_date,
                            'long_term': expense.long_term,
                        })
                        current_date += relativedelta(months=1)
                else:
                    year_month = expense.date.strftime('%Y-%m')
                    if year_month not in expense_data:
                        expense_data[year_month] = []
                    
                    expense_data[year_month].append({
                        'name': expense.name,
                        'amount': expense.amount,
                        'date': expense.date,
                    })


        aggregated_data = [{'year_month': key, 'expenses': sum(item['amount'] for item in value)} for key, value in expense_data_graph.items()]

        context['expense_data'] = expense_data
        context['aggregated_data'] = aggregated_data

        graph_data = {
        'months': [item['year_month'] for item in aggregated_data],
        'expenses': [item['expenses'] for item in aggregated_data],
        }

        graph_data['chart'] = generate_graph(graph_data)
        context['graph_data'] = mark_safe(graph_data['chart'])

        return context
    




    


        


                        
                            



