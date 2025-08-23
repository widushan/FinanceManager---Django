from django.shortcuts import render, redirect, get_object_or_404
#from django.http import HttpResponse
#from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
#from exp_tracker import models
from .models import Account, Expense, Income
from django.views.generic.edit import FormView
#from django.views.generic import ListView
from datetime import datetime
from .forms import ExpenseForm
from .forms import IncomeForm
from dateutil.relativedelta import relativedelta
from django.utils.safestring import mark_safe
#from django.db.models import Sum, Count, F
#import plotly.express as px
#from plotly.graph_objs import *
#from collections import defaultdict

# Import AI/ML functionality
try:
    from .ml_models import ml_predictor
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("Warning: ML packages not installed. AI features will be limited.")
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required




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
                            'total_amount': expense.amount
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

        # Process incomes for both dictionaries simultaneously to ensure consistency
        for account in accounts:
            incomes = account.income_list.all()
            for income in incomes:
                if income.long_term and income.monthly_incomes:
                    current_date = income.date
                    while current_date <= income.end_date:
                        year_month = current_date.strftime('%Y-%m')
                        
                        # For income_data (display)
                        if year_month not in income_data:
                            income_data[year_month] = []
                        income_data[year_month].append({
                            'id': income.id,
                            'name': income.name,
                            'amount': income.monthly_incomes,
                            'date': current_date,
                            'end_date': income.end_date,
                            'long_term': income.long_term,
                            'total_amount': income.amount
                        })
                        
                        # For income_data_graph (chart)
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




def report(request):
    user = request.user
    accounts = Account.objects.filter(user=user)
    
    # Initialize data structures
    monthly_data = {}
    current_month = datetime.now().strftime('%Y-%m')
    
    # Process expenses
    for account in accounts:
        expenses = account.expense_list.all()
        for expense in expenses:
            if expense.long_term and expense.monthly_expenses:
                current_date = expense.date
                while current_date <= expense.end_date:
                    year_month = current_date.strftime('%Y-%m')
                    if year_month not in monthly_data:
                        monthly_data[year_month] = {'expenses': 0, 'incomes': 0}
                    monthly_data[year_month]['expenses'] += float(expense.monthly_expenses)
                    current_date += relativedelta(months=1)
            else:
                year_month = expense.date.strftime('%Y-%m')
                if year_month not in monthly_data:
                    monthly_data[year_month] = {'expenses': 0, 'incomes': 0}
                monthly_data[year_month]['expenses'] += float(expense.amount)

    # Process incomes
    for account in accounts:
        incomes = account.income_list.all()
        for income in incomes:
            if income.long_term and income.monthly_incomes:
                current_date = income.date
                while current_date <= income.end_date:
                    year_month = current_date.strftime('%Y-%m')
                    if year_month not in monthly_data:
                        monthly_data[year_month] = {'expenses': 0, 'incomes': 0}
                    monthly_data[year_month]['incomes'] += float(income.monthly_incomes)
                    current_date += relativedelta(months=1)
            else:
                year_month = income.date.strftime('%Y-%m')
                if year_month not in monthly_data:
                    monthly_data[year_month] = {'expenses': 0, 'incomes': 0}
                monthly_data[year_month]['incomes'] += float(income.amount)

    # Calculate profit/loss for each month
    for month in monthly_data:
        incomes = monthly_data[month]['incomes']
        expenses = monthly_data[month]['expenses']
        profit_loss = incomes - expenses
        profit_loss_percentage = (profit_loss / incomes * 100) if incomes > 0 else 0
        
        monthly_data[month].update({
            'profit_loss': profit_loss,
            'profit_loss_percentage': profit_loss_percentage,
            'status': 'profit' if profit_loss >= 0 else 'loss'
        })

    # Sort months
    sorted_months = sorted(monthly_data.keys())
    
    # Prepare data for charts
    months = []
    incomes = []
    expenses = []
    profits = []
    
    for month in sorted_months:
        months.append(month)
        incomes.append(monthly_data[month]['incomes'])
        expenses.append(monthly_data[month]['expenses'])
        profits.append(monthly_data[month]['profit_loss'])

    # Create charts
    bar_chart = generate_monthly_comparison_chart(months, incomes, expenses, profits)
    
    # Current month pie chart
    if current_month in monthly_data:
        current_data = monthly_data[current_month]
        pie_chart = generate_profit_loss_chart({
            'values': [current_data['incomes'], current_data['expenses']],
            'labels': ['Income', 'Expenses'],
            'colors': ['#27ae60', '#e74c3c']
        })
    else:
        pie_chart = generate_profit_loss_chart({
            'values': [0, 0],
            'labels': ['Income', 'Expenses'],
            'colors': ['#27ae60', '#e74c3c']
        })

    context = {
        'monthly_data': monthly_data,
        'current_month': current_month,
        'sorted_months': sorted_months,
        'bar_chart': mark_safe(bar_chart),
        'pie_chart': mark_safe(pie_chart)
    }
    
    return render(request, 'exp_tracker/report.html', context)

def generate_monthly_comparison_chart(months, incomes, expenses, profits):
    import plotly.graph_objects as go
    
    fig = go.Figure()
    
    # Add traces for income, expenses, and profit/loss
    fig.add_trace(go.Bar(
        name='Income',
        x=months,
        y=incomes,
        marker_color='#27ae60'
    ))
    
    fig.add_trace(go.Bar(
        name='Expenses',
        x=months,
        y=expenses,
        marker_color='#e74c3c'
    ))
    
    fig.add_trace(go.Scatter(
        name='Profit/Loss',
        x=months,
        y=profits,
        line=dict(color='#3498db', width=2),
        mode='lines+markers'
    ))
    
    fig.update_layout(
        title='Monthly Financial Overview',
        barmode='group',
        xaxis=dict(
            title='Month',
            type='category'
        ),
        yaxis=dict(
            title='Amount (Rs.)',
            tickformat=',d'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='rgba(0,0,0,1)',
        height=400,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig.to_json()

def generate_profit_loss_chart(data):
    import plotly.graph_objects as go
    
    fig = go.Figure()
    
    fig.add_trace(go.Pie(
        labels=data['labels'],
        values=data['values'],
        marker_colors=data['colors'],
        hole=.3
    ))
    
    fig.update_layout(
        title='Income vs Expenses Distribution',
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='rgba(0,0,0,1)',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig.to_json()







        


                        
                            




# AI/ML Views
@login_required
def ai_insights(request):
    """
    Main AI insights page showing predictions and analysis
    """
    try:
        # Get user's expense data
        expenses = Expense.objects.filter(user=request.user).order_by('date')
        
        if not expenses.exists():
            return render(request, 'exp_tracker/ai_insights.html', {
                'error': 'No expense data available for AI analysis. Please add some expenses first.'
            })
        
        # Convert to format expected by ML models
        expenses_data = []
        for expense in expenses:
            # Create a simple category based on expense name or use a default
            category = "General"
            if expense.name.lower() in ['food', 'groceries', 'restaurant', 'dining']:
                category = "Food"
            elif expense.name.lower() in ['transport', 'gas', 'fuel', 'uber', 'taxi']:
                category = "Transport"
            elif expense.name.lower() in ['entertainment', 'movie', 'game', 'fun']:
                category = "Entertainment"
            elif expense.name.lower() in ['shopping', 'clothes', 'electronics']:
                category = "Shopping"
            elif expense.name.lower() in ['bills', 'electricity', 'water', 'internet']:
                category = "Bills"
            elif expense.name.lower() in ['health', 'medical', 'doctor', 'medicine']:
                category = "Healthcare"
            
            expenses_data.append({
                'date': expense.date,
                'amount': float(expense.amount),
                'category': category,
                'description': expense.name or ''
            })
        
        # Get AI insights
        context = {
            'total_expenses': len(expenses_data),
            'date_range': {
                'start': expenses.first().date.strftime('%Y-%m-%d'),
                'end': expenses.last().date.strftime('%Y-%m-%d')
            }
        }
        
        # Spending pattern analysis
        if ML_AVAILABLE:
            pattern_analysis, pattern_message = ml_predictor.analyze_spending_patterns(expenses_data)
            context['pattern_analysis'] = pattern_analysis
            context['pattern_message'] = pattern_message
        else:
            # Simple analysis without ML
            total_amount = sum(expense.amount for expense in expenses)
            avg_amount = total_amount / len(expenses) if expenses else 0
            
            # Simple category analysis
            categories = {}
            for expense in expenses:
                category = "General"
                if expense.name.lower() in ['food', 'groceries', 'restaurant', 'dining']:
                    category = "Food"
                elif expense.name.lower() in ['transport', 'gas', 'fuel', 'uber', 'taxi']:
                    category = "Transport"
                elif expense.name.lower() in ['entertainment', 'movie', 'game', 'fun']:
                    category = "Entertainment"
                elif expense.name.lower() in ['shopping', 'clothes', 'electronics']:
                    category = "Shopping"
                elif expense.name.lower() in ['bills', 'electricity', 'water', 'internet']:
                    category = "Bills"
                elif expense.name.lower() in ['health', 'medical', 'doctor', 'medicine']:
                    category = "Healthcare"
                
                categories[category] = categories.get(category, 0) + expense.amount
            
            top_category = max(categories.items(), key=lambda x: x[1]) if categories else ("None", 0)
            
            context['pattern_analysis'] = {
                'total_spent': round(total_amount, 2),
                'avg_daily_spending': round(avg_amount, 2),
                'avg_transaction': round(avg_amount, 2),
                'top_category': top_category[0],
                'top_category_percentage': round((top_category[1] / total_amount * 100), 1) if total_amount > 0 else 0,
                'spending_trend': "Stable",
                'total_transactions': len(expenses),
                'date_range': {
                    'start': expenses.first().date.strftime('%Y-%m-%d'),
                    'end': expenses.last().date.strftime('%Y-%m-%d')
                },
                'recommendations': ["Add more expense data for better AI insights"]
            }
            context['pattern_message'] = "Basic analysis completed (ML not available)"
        
        # Anomaly detection
        if ML_AVAILABLE:
            anomalies, anomaly_message = ml_predictor.detect_anomalies(expenses_data)
            context['anomalies'] = anomalies
            context['anomaly_message'] = anomaly_message
        else:
            # Simple anomaly detection without ML
            amounts = [expense.amount for expense in expenses]
            if amounts:
                mean_amount = sum(amounts) / len(amounts)
                std_amount = (sum((x - mean_amount) ** 2 for x in amounts) / len(amounts)) ** 0.5
                
                anomalies = []
                for expense in expenses:
                    if abs(expense.amount - mean_amount) > 2 * std_amount:  # 2 standard deviations
                        category = "General"
                        if expense.name.lower() in ['food', 'groceries', 'restaurant', 'dining']:
                            category = "Food"
                        elif expense.name.lower() in ['transport', 'gas', 'fuel', 'uber', 'taxi']:
                            category = "Transport"
                        elif expense.name.lower() in ['entertainment', 'movie', 'game', 'fun']:
                            category = "Entertainment"
                        elif expense.name.lower() in ['shopping', 'clothes', 'electronics']:
                            category = "Shopping"
                        elif expense.name.lower() in ['bills', 'electricity', 'water', 'internet']:
                            category = "Bills"
                        elif expense.name.lower() in ['health', 'medical', 'doctor', 'medicine']:
                            category = "Healthcare"
                        
                        anomalies.append({
                            'date': expense.date.strftime('%Y-%m-%d'),
                            'amount': expense.amount,
                            'category': category,
                            'description': expense.name,
                            'anomaly_score': -1.0
                        })
                
                context['anomalies'] = anomalies
                context['anomaly_message'] = f"Detected {len(anomalies)} potential anomalies using basic statistics"
            else:
                context['anomalies'] = []
                context['anomaly_message'] = "No anomalies detected"
        
        # Expense prediction
        if ML_AVAILABLE:
            prediction, prediction_message = ml_predictor.predict_next_month_expenses(request.user.id)
            context['prediction'] = prediction
            context['prediction_message'] = prediction_message
        else:
            # Simple prediction without ML
            if len(expenses) >= 3:
                recent_expenses = expenses.order_by('-date')[:30]  # Last 30 expenses
                avg_monthly = sum(expense.amount for expense in recent_expenses) / 3  # Assume 3 months
                
                context['prediction'] = {
                    'total_predicted': round(avg_monthly, 2),
                    'daily_average': round(avg_monthly / 30, 2),
                    'month': 'Next Month',
                    'confidence': 'Low'
                }
                context['prediction_message'] = "Basic prediction based on recent expenses"
            else:
                context['prediction'] = None
                context['prediction_message'] = "Need more data for prediction"
        
        # Model training status
        if len(expenses_data) >= 10:
            if ML_AVAILABLE:
                training_success, training_result = ml_predictor.train_expense_predictor(expenses_data)
                context['model_trained'] = training_success
                context['training_result'] = training_result
            else:
                context['model_trained'] = False
                context['training_result'] = "ML models not available. Cannot train."
        else:
            context['model_trained'] = False
            context['training_result'] = f"Need at least 10 expense records for training. Currently have {len(expenses_data)}."
        
        return render(request, 'exp_tracker/ai_insights.html', context)
        
    except Exception as e:
        return render(request, 'exp_tracker/ai_insights.html', {
            'error': f'Error generating AI insights: {str(e)}'
        })

@login_required
def train_ml_model(request):
    """
    API endpoint to train the ML model
    """
    try:
        expenses = Expense.objects.filter(user=request.user).order_by('date')
        
        if not expenses.exists():
            return JsonResponse({
                'success': False,
                'message': 'No expense data available for training'
            })
        
        expenses_data = []
        for expense in expenses:
            # Create a simple category based on expense name
            category = "General"
            if expense.name.lower() in ['food', 'groceries', 'restaurant', 'dining']:
                category = "Food"
            elif expense.name.lower() in ['transport', 'gas', 'fuel', 'uber', 'taxi']:
                category = "Transport"
            elif expense.name.lower() in ['entertainment', 'movie', 'game', 'fun']:
                category = "Entertainment"
            elif expense.name.lower() in ['shopping', 'clothes', 'electronics']:
                category = "Shopping"
            elif expense.name.lower() in ['bills', 'electricity', 'water', 'internet']:
                category = "Bills"
            elif expense.name.lower() in ['health', 'medical', 'doctor', 'medicine']:
                category = "Healthcare"
            
            expenses_data.append({
                'date': expense.date,
                'amount': float(expense.amount),
                'category': category,
                'description': expense.name or ''
            })
        
        if ML_AVAILABLE:
            success, result = ml_predictor.train_expense_predictor(expenses_data)
        else:
            success = False
            result = "ML models not available. Cannot train."
        
        return JsonResponse({
            'success': success,
            'result': result
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Training failed: {str(e)}'
        })

@login_required
def get_expense_prediction(request):
    """
    API endpoint to get expense predictions
    """
    try:
        if ML_AVAILABLE:
            prediction, message = ml_predictor.predict_next_month_expenses(request.user.id)
        else:
            prediction = None
            message = "ML models not available. Please install ML packages for predictions."
        
        return JsonResponse({
            'success': prediction is not None,
            'prediction': prediction,
            'message': message
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Prediction failed: {str(e)}'
        })

@login_required
def get_anomalies(request):
    """
    API endpoint to get spending anomalies
    """
    try:
        expenses = Expense.objects.filter(user=request.user).order_by('date')
        
        if not expenses.exists():
            return JsonResponse({
                'success': False,
                'message': 'No expense data available'
            })
        
        expenses_data = []
        for expense in expenses:
            # Create a simple category based on expense name
            category = "General"
            if expense.name.lower() in ['food', 'groceries', 'restaurant', 'dining']:
                category = "Food"
            elif expense.name.lower() in ['transport', 'gas', 'fuel', 'uber', 'taxi']:
                category = "Transport"
            elif expense.name.lower() in ['entertainment', 'movie', 'game', 'fun']:
                category = "Entertainment"
            elif expense.name.lower() in ['shopping', 'clothes', 'electronics']:
                category = "Shopping"
            elif expense.name.lower() in ['bills', 'electricity', 'water', 'internet']:
                category = "Bills"
            elif expense.name.lower() in ['health', 'medical', 'doctor', 'medicine']:
                category = "Healthcare"
            
            expenses_data.append({
                'date': expense.date,
                'amount': float(expense.amount),
                'category': category,
                'description': expense.name or ''
            })
        
        if ML_AVAILABLE:
            anomalies, message = ml_predictor.detect_anomalies(expenses_data)
        else:
            # Simple anomaly detection without ML
            amounts = [expense.amount for expense in expenses]
            if amounts:
                mean_amount = sum(amounts) / len(amounts)
                std_amount = (sum((x - mean_amount) ** 2 for x in amounts) / len(amounts)) ** 0.5
                
                anomalies = []
                for expense in expenses:
                    if abs(expense.amount - mean_amount) > 2 * std_amount:  # 2 standard deviations
                        category = "General"
                        if expense.name.lower() in ['food', 'groceries', 'restaurant', 'dining']:
                            category = "Food"
                        elif expense.name.lower() in ['transport', 'gas', 'fuel', 'uber', 'taxi']:
                            category = "Transport"
                        elif expense.name.lower() in ['entertainment', 'movie', 'game', 'fun']:
                            category = "Entertainment"
                        elif expense.name.lower() in ['shopping', 'clothes', 'electronics']:
                            category = "Shopping"
                        elif expense.name.lower() in ['bills', 'electricity', 'water', 'internet']:
                            category = "Bills"
                        elif expense.name.lower() in ['health', 'medical', 'doctor', 'medicine']:
                            category = "Healthcare"
                        
                        anomalies.append({
                            'date': expense.date.strftime('%Y-%m-%d'),
                            'amount': expense.amount,
                            'category': category,
                            'description': expense.name,
                            'anomaly_score': -1.0
                        })
                
                message = f"Detected {len(anomalies)} potential anomalies using basic statistics"
            else:
                anomalies = []
                message = "No anomalies detected"
        
        return JsonResponse({
            'success': True,
            'anomalies': anomalies,
            'message': message
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Anomaly detection failed: {str(e)}'
        })







        


                        
                            



