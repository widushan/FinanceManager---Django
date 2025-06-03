from django.shortcuts import render, redirect, get_object_or_404
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
from .forms import IncomeForm
from dateutil.relativedelta import relativedelta
from django.utils.safestring import mark_safe
from django.db.models import Sum, Count, F
import plotly.express as px
from plotly.graph_objs import *
from collections import defaultdict




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
    # Import plotly.graph_objects for more control
    import plotly.graph_objects as go
    
    fig = go.Figure()
    
    # Add the bar trace
    fig.add_trace(go.Bar(
        x=data['months'],
        y=data['expenses'],
        marker_color='#008c41'
    ))
    
    # Update layout with better formatting
    fig.update_layout(
        title='Monthly Expenses',
        xaxis=dict(
            title='Month',
            type='category'  # Treat months as categories to preserve order
        ),
        yaxis=dict(
            title='Amount (Rs.)',
            tickformat=',d'  # Format with commas for thousands
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='rgba(0,0,0,1)',
        height=400
    )
    
    # Debug: Print out the raw data
    print("Months:", data['months'])
    print("Expenses:", data['expenses'])
    
    graph_json = fig.to_json()
    return graph_json





def income_generate_graph(data):
    # Import plotly.graph_objects for more control
    import plotly.graph_objects as go
    
    fig = go.Figure()
    
    # Add the bar trace
    fig.add_trace(go.Bar(
        x=data['months'],
        y=data['incomes'],
        marker_color='#008c41'
    ))
    
    # Update layout with better formatting
    fig.update_layout(
        title='Monthly Incomes',
        xaxis=dict(
            title='Month',
            type='category'  # Treat months as categories to preserve order
        ),
        yaxis=dict(
            title='Amount (Rs.)',
            tickformat=',d'  # Format with commas for thousands
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='rgba(0,0,0,1)',
        height=400
    )
    
    # Debug: Print out the raw data
    print("Months:", data['months'])
    print("Incomes:", data['incomes'])
    
    graph_json = fig.to_json()
    return graph_json







class ExpenseListView(FormView):
    template_name = 'exp_tracker/expenses_list.html'
    form_class = ExpenseForm
    success_url = '/expenses'


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

        # Process expenses for both dictionaries simultaneously to ensure consistency
        for account in accounts:
            expenses = account.expense_list.all()
            for expense in expenses:
                if expense.long_term and expense.monthly_expenses:
                    current_date = expense.date
                    while current_date <= expense.end_date:
                        year_month = current_date.strftime('%Y-%m')
                        
                        # For expense_data (display)
                        if year_month not in expense_data:
                            expense_data[year_month] = []
                        expense_data[year_month].append({
                            'id': expense.id,
                            'name': expense.name,
                            'amount': expense.monthly_expenses,
                            'date': current_date,
                            'end_date': expense.end_date,
                            'long_term': expense.long_term,
                        })
                        
                        # For expense_data_graph (chart)
                        if year_month not in expense_data_graph:
                            expense_data_graph[year_month] = 0
                        expense_data_graph[year_month] += float(expense.monthly_expenses)
                        
                        current_date += relativedelta(months=1)
                else:
                    year_month = expense.date.strftime('%Y-%m')
                    
                    # For expense_data (display)
                    if year_month not in expense_data:
                        expense_data[year_month] = []
                    expense_data[year_month].append({
                        'id': expense.id,
                        'name': expense.name,
                        'amount': expense.amount,
                        'date': expense.date,
                        'long_term': expense.long_term,
                    })
                    
                    # For expense_data_graph (chart)
                    if year_month not in expense_data_graph:
                        expense_data_graph[year_month] = 0
                    expense_data_graph[year_month] += float(expense.amount)

        # Prepare data for the graph
        months = []
        expenses = []
        
        for month in sorted(expense_data_graph.keys()):
            months.append(month)
            expenses.append(expense_data_graph[month])
        
        # Debug output
        print("Month-wise expense totals:")
        for month, amount in zip(months, expenses):
            print(f"{month}: Rs. {amount:,.2f}")
            
        # Convert to dicts for template
        aggregated_data = [{'year_month': month, 'expenses': expense_data_graph[month]} 
                           for month in sorted(expense_data_graph.keys())]

        context['expense_data'] = expense_data
        context['aggregated_data'] = aggregated_data

        graph_data = {
            'months': months,
            'expenses': expenses,
        }

        graph_data['chart'] = generate_graph(graph_data)
        context['graph_data'] = mark_safe(graph_data['chart'])

        return context
    




class IncomeListView(FormView):
    template_name = 'exp_tracker/incomes_list.html'
    form_class = IncomeForm
    success_url = '/incomes'


    def form_valid(self, form):
        account, _ = Account.objects.get_or_create(user=self.request.user)

        income = Income(
            name = form.cleaned_data['name'],
            amount = form.cleaned_data['amount'],
            interest_rate = form.cleaned_data['interest_rate'],
            date = form.cleaned_data['date'],
            end_date = form.cleaned_data['end_date'],
            long_term = form.cleaned_data['long_term'],
            user = self.request.user
        )
        income.save()
        account.income_list.add(income)
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        accounts = Account.objects.filter(user=user)
        
        income_data_graph = {}
        income_data = {}

        # Process expenses for both dictionaries simultaneously to ensure consistency
        for account in accounts:
            incomes = account.income_list.all()
            for income in incomes:
                if income.long_term and income.monthly_incomes:
                    current_date = income.date
                    while current_date <= income.end_date:
                        year_month = current_date.strftime('%Y-%m')
                        
                        # For expense_data (display)
                        if year_month not in income_data:
                            income_data[year_month] = []
                            income_data[year_month].append({
                                'id': income.id,
                                'name': income.name,
                                'amount': income.monthly_incomes,
                                'date': current_date,
                                'end_date': income.end_date,
                                'long_term': income.long_term,
                            })
                        
                        # For expense_data_graph (chart)
                        if year_month not in income_data_graph:
                            income_data_graph[year_month] = 0
                        income_data_graph[year_month] += float(income.monthly_incomes)
                        
                        current_date += relativedelta(months=1)
                else:
                    year_month = income.date.strftime('%Y-%m')
                    
                    # For expense_data (display)
                    if year_month not in income_data:
                        income_data[year_month] = []
                    income_data[year_month].append({
                        'id': income.id,
                        'name': income.name,
                        'amount': income.amount,
                        'date': income.date,
                        'long_term': income.long_term,
                    })
                    
                    # For expense_data_graph (chart)
                    if year_month not in income_data_graph:
                        income_data_graph[year_month] = 0
                    income_data_graph[year_month] += float(income.amount)

        # Prepare data for the graph
        months = []
        incomes = []
        
        for month in sorted(income_data_graph.keys()):
            months.append(month)
            incomes.append(income_data_graph[month])
        
        # Debug output
        print("Month-wise income totals:")
        for month, amount in zip(months, incomes):
            print(f"{month}: Rs. {amount:,.2f}")
            
        # Convert to dicts for template
        aggregated_data = [{'year_month': month, 'incomes': income_data_graph[month]} 
                           for month in sorted(income_data_graph.keys())]

        context['income_data'] = income_data
        context['aggregated_data'] = aggregated_data

        graph_data = {
            'months': months,
            'incomes': incomes,
        }

        graph_data['chart'] = income_generate_graph(graph_data)
        context['graph_data'] = mark_safe(graph_data['chart'])

        return context
    
    

def edit_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('expenses')
    else:
        form = ExpenseForm(instance=expense)
        
    return render(request, 'exp_tracker/edit_expense.html', {
        'form': form,
        'expense': expense
    })


def edit_income(request, income_id):
    income = get_object_or_404(Income, id=income_id, user=request.user)
    
    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=income)
        if form.is_valid():
            form.save()
            return redirect('incomes')
    else:
        form = IncomeForm(instance=income)
        
    return render(request, 'exp_tracker/edit_income.html', {
        'form': form,
        'income': income
    })

def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    
    # Find and update the associated account
    accounts = Account.objects.filter(user=request.user, expense_list=expense)
    for account in accounts:
        account.expense_list.remove(expense)
    
    # Delete the expense
    expense.delete()
    
    return redirect('expenses')



def delete_income(request, income_id):
    income = get_object_or_404(Income, id=income_id, user=request.user)
    
    # Find and update the associated account
    accounts = Account.objects.filter(user=request.user, income_list=income)
    for account in accounts:
        account.income_list.remove(income)
    
    # Delete the expense
    income.delete()
    
    return redirect('incomes')
    




    


        


                        
                            



