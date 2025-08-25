from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum,Avg
from django.utils import timezone

from dateutil.relativedelta import relativedelta
from collections import defaultdict


from .models import Account, Expense, Income
from .serializers import (
    AccountSerializer, ExpenseSerializer, IncomeSerializer,
    ExpenseCreateSerializer, IncomeCreateSerializer,
    FinancialStatsSerializer, AIInsightSerializer,
    ExpenseSummarySerializer, IncomeSummarySerializer
)

# Import AI/ML functionality
try:
    from .ml_models import ml_predictor
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False


class AccountViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing user accounts
    """
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return accounts for the current user"""
        return Account.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get account summary with financial overview"""
        account = self.get_queryset().first()
        if not account:
            return Response({'error': 'No account found'}, status=status.HTTP_404_NOT_FOUND)

        # Calculate financial statistics
        total_expenses = sum(expense.amount for expense in account.expense_list.all())
        total_incomes = sum(income.amount for income in account.income_list.all())
        balance = total_incomes - total_expenses

        # Monthly calculations
        current_month = timezone.now().strftime('%Y-%m')
        monthly_expenses = sum(
            expense.amount for expense in account.expense_list.all()
            if expense.date.strftime('%Y-%m') == current_month
        )
        monthly_incomes = sum(
            income.amount for income in account.income_list.all()
            if income.date.strftime('%Y-%m') == current_month
        )

        # Top categories
        expense_categories = defaultdict(float)
        for expense in account.expense_list.all():
            category = self._get_expense_category(expense.name)
            expense_categories[category] += expense.amount

        top_expense_category = max(expense_categories.items(), key=lambda x: x[1])[0] if expense_categories else "None"

        data = {
            'total_expenses': total_expenses,
            'total_incomes': total_incomes,
            'balance': balance,
            'expense_count': account.expense_list.count(),
            'income_count': account.income_list.count(),
            'monthly_expenses': monthly_expenses,
            'monthly_incomes': monthly_incomes,
            'profit_margin': (balance / total_incomes * 100) if total_incomes > 0 else 0,
            'top_expense_category': top_expense_category,
            'top_income_source': "Salary"  # Default, can be enhanced
        }

        serializer = FinancialStatsSerializer(data)
        return Response(serializer.data)

    def _get_expense_category(self, name):
        """Helper method to categorize expenses"""
        name_lower = name.lower()
        if any(word in name_lower for word in ['food', 'groceries', 'restaurant', 'dining']):
            return "Food"
        elif any(word in name_lower for word in ['transport', 'gas', 'fuel', 'uber', 'taxi']):
            return "Transport"
        elif any(word in name_lower for word in ['entertainment', 'movie', 'game', 'fun']):
            return "Entertainment"
        elif any(word in name_lower for word in ['shopping', 'clothes', 'electronics']):
            return "Shopping"
        elif any(word in name_lower for word in ['bills', 'electricity', 'water', 'internet']):
            return "Bills"
        elif any(word in name_lower for word in ['health', 'medical', 'doctor', 'medicine']):
            return "Healthcare"
        return "General"


class ExpenseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing expenses
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return expenses for the current user"""
        return Expense.objects.filter(user=self.request.user).order_by('-date')

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return ExpenseCreateSerializer
        return ExpenseSerializer

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get expense summary with statistics"""
        expenses = self.get_queryset()
        
        if not expenses.exists():
            return Response({'error': 'No expenses found'}, status=status.HTTP_404_NOT_FOUND)

        # Basic statistics
        total_amount = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
        average_amount = expenses.aggregate(Avg('amount'))['amount__avg'] or 0
        count = expenses.count()

        # Category breakdown
        categories = defaultdict(lambda: {'total': 0, 'count': 0})
        for expense in expenses:
            category = self._get_expense_category(expense.name)
            categories[category]['total'] += expense.amount
            categories[category]['count'] += 1

        category_breakdown = []
        for category, data in categories.items():
            percentage = (data['total'] / total_amount * 100) if total_amount > 0 else 0
            category_breakdown.append({
                'category': category,
                'total_amount': data['total'],
                'percentage': round(percentage, 2),
                'count': data['count']
            })

        # Monthly trend (last 6 months)
        monthly_trend = []
        for i in range(6):
            month_date = timezone.now() - relativedelta(months=i)
            month_str = month_date.strftime('%Y-%m')
            month_expenses = expenses.filter(date__year=month_date.year, date__month=month_date.month)
            month_total = month_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
            monthly_trend.append({
                'month': month_str,
                'total': month_total,
                'count': month_expenses.count()
            })

        data = {
            'total_amount': total_amount,
            'average_amount': average_amount,
            'count': count,
            'categories': category_breakdown,
            'monthly_trend': monthly_trend
        }

        serializer = ExpenseSummarySerializer(data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get expenses grouped by category"""
        category = request.query_params.get('category', '').title()
        expenses = self.get_queryset()
        
        if category:
            # Filter by category (using name matching)
            if category == "Food":
                expenses = expenses.filter(name__icontains='food') | expenses.filter(name__icontains='groceries')
            elif category == "Transport":
                expenses = expenses.filter(name__icontains='transport') | expenses.filter(name__icontains='gas')
            elif category == "Entertainment":
                expenses = expenses.filter(name__icontains='entertainment') | expenses.filter(name__icontains='movie')
            elif category == "Shopping":
                expenses = expenses.filter(name__icontains='shopping') | expenses.filter(name__icontains='clothes')
            elif category == "Bills":
                expenses = expenses.filter(name__icontains='bills') | expenses.filter(name__icontains='electricity')
            elif category == "Healthcare":
                expenses = expenses.filter(name__icontains='health') | expenses.filter(name__icontains='medical')

        serializer = self.get_serializer(expenses, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent expenses (last 10)"""
        recent_expenses = self.get_queryset()[:10]
        serializer = self.get_serializer(recent_expenses, many=True)
        return Response(serializer.data)

    def _get_expense_category(self, name):
        """Helper method to categorize expenses"""
        name_lower = name.lower()
        if any(word in name_lower for word in ['food', 'groceries', 'restaurant', 'dining']):
            return "Food"
        elif any(word in name_lower for word in ['transport', 'gas', 'fuel', 'uber', 'taxi']):
            return "Transport"
        elif any(word in name_lower for word in ['entertainment', 'movie', 'game', 'fun']):
            return "Entertainment"
        elif any(word in name_lower for word in ['shopping', 'clothes', 'electronics']):
            return "Shopping"
        elif any(word in name_lower for word in ['bills', 'electricity', 'water', 'internet']):
            return "Bills"
        elif any(word in name_lower for word in ['health', 'medical', 'doctor', 'medicine']):
            return "Healthcare"
        return "General"


class IncomeViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing incomes
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return incomes for the current user"""
        return Income.objects.filter(user=self.request.user).order_by('-date')

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return IncomeCreateSerializer
        return IncomeSerializer

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get income summary with statistics"""
        incomes = self.get_queryset()
        
        if not incomes.exists():
            return Response({'error': 'No incomes found'}, status=status.HTTP_404_NOT_FOUND)

        # Basic statistics
        total_amount = incomes.aggregate(Sum('amount'))['amount__sum'] or 0
        average_amount = incomes.aggregate(Avg('amount'))['amount__avg'] or 0
        count = incomes.count()

        # Monthly trend (last 6 months)
        monthly_trend = []
        for i in range(6):
            month_date = timezone.now() - relativedelta(months=i)
            month_str = month_date.strftime('%Y-%m')
            month_incomes = incomes.filter(date__year=month_date.year, date__month=month_date.month)
            month_total = month_incomes.aggregate(Sum('amount'))['amount__sum'] or 0
            monthly_trend.append({
                'month': month_str,
                'total': month_total,
                'count': month_incomes.count()
            })

        data = {
            'total_amount': total_amount,
            'average_amount': average_amount,
            'count': count,
            'monthly_trend': monthly_trend
        }

        serializer = IncomeSummarySerializer(data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent incomes (last 10)"""
        recent_incomes = self.get_queryset()[:10]
        serializer = self.get_serializer(recent_incomes, many=True)
        return Response(serializer.data)


class FinancialReportAPIView(APIView):
    """
    API endpoint for comprehensive financial reports
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get comprehensive financial report"""
        user = request.user
        accounts = Account.objects.filter(user=user)
        
        if not accounts.exists():
            return Response({'error': 'No account found'}, status=status.HTTP_404_NOT_FOUND)

        # Initialize data structures
        monthly_data = {}
        current_month = timezone.now().strftime('%Y-%m')
        
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
        
        # Prepare response data
        report_data = []
        for month in sorted_months:
            data = monthly_data[month]
            data['month'] = month
            report_data.append(data)

        return Response({
            'monthly_data': report_data,
            'current_month': current_month,
            'total_months': len(report_data)
        })


class AIInsightsAPIView(APIView):
    """
    API endpoint for AI insights and predictions
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get AI insights for the user"""
        expenses = Expense.objects.filter(user=request.user).order_by('date')
        
        if not expenses.exists():
            return Response({'error': 'No expense data available for AI analysis'}, 
                          status=status.HTTP_404_NOT_FOUND)

        # Convert to format expected by ML models
        expenses_data = []
        for expense in expenses:
            category = self._get_expense_category(expense.name)
            expenses_data.append({
                'date': expense.date,
                'amount': float(expense.amount),
                'category': category,
                'description': expense.name or ''
            })

        # Get AI insights
        context = {
            'total_expenses_analyzed': len(expenses_data),
            'date_range': {
                'start': expenses.first().date.strftime('%Y-%m-%d'),
                'end': expenses.last().date.strftime('%Y-%m-%d')
            }
        }

        # Spending pattern analysis
        if ML_AVAILABLE:
            pattern_analysis, pattern_message = ml_predictor.analyze_spending_patterns(expenses_data)
            context['pattern_analysis'] = pattern_analysis
        else:
            # Simple analysis without ML
            total_amount = sum(expense.amount for expense in expenses)
            avg_amount = total_amount / len(expenses) if expenses else 0
            
            categories = defaultdict(float)
            for expense in expenses:
                category = self._get_expense_category(expense.name)
                categories[category] += expense.amount
            
            top_category = max(categories.items(), key=lambda x: x[1]) if categories else ("None", 0)
            
            context['pattern_analysis'] = {
                'total_spent': round(total_amount, 2),
                'avg_daily_spending': round(avg_amount, 2),
                'avg_transaction': round(avg_amount, 2),
                'top_category': top_category[0],
                'top_category_percentage': round((top_category[1] / total_amount * 100), 1) if total_amount > 0 else 0,
                'spending_trend': "Stable",
                'total_transactions': len(expenses),
                'recommendations': ["Add more expense data for better AI insights"]
            }

        # Anomaly detection
        if ML_AVAILABLE:
            anomalies, anomaly_message = ml_predictor.detect_anomalies(expenses_data)
            context['anomalies'] = anomalies
        else:
            # Simple anomaly detection without ML
            amounts = [expense.amount for expense in expenses]
            if amounts:
                mean_amount = sum(amounts) / len(amounts)
                std_amount = (sum((x - mean_amount) ** 2 for x in amounts) / len(amounts)) ** 0.5
                
                anomalies = []
                for expense in expenses:
                    if abs(expense.amount - mean_amount) > 2 * std_amount:  # 2 standard deviations
                        category = self._get_expense_category(expense.name)
                        anomalies.append({
                            'date': expense.date.strftime('%Y-%m-%d'),
                            'amount': expense.amount,
                            'category': category,
                            'description': expense.name,
                            'anomaly_score': -1.0
                        })
                
                context['anomalies'] = anomalies
            else:
                context['anomalies'] = []

        # Expense prediction
        if ML_AVAILABLE:
            prediction_result = ml_predictor.predict_next_month_expenses(request.user.id)
            if isinstance(prediction_result, tuple):
                prediction, _ = prediction_result
            else:
                prediction = prediction_result
            context['prediction'] = prediction
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
            else:
                context['prediction'] = None

        # Model training status
        if len(expenses_data) >= 10:
            if ML_AVAILABLE:
                training_success, training_result = ml_predictor.train_expense_predictor(expenses_data)
                context['model_status'] = 'Trained' if training_success else 'Training Failed'
            else:
                context['model_status'] = 'ML not available'
        else:
            context['model_status'] = f'Need {10 - len(expenses_data)} more records'

        serializer = AIInsightSerializer(context)
        return Response(serializer.data)

    def _get_expense_category(self, name):
        """Helper method to categorize expenses"""
        name_lower = name.lower()
        if any(word in name_lower for word in ['food', 'groceries', 'restaurant', 'dining']):
            return "Food"
        elif any(word in name_lower for word in ['transport', 'gas', 'fuel', 'uber', 'taxi']):
            return "Transport"
        elif any(word in name_lower for word in ['entertainment', 'movie', 'game', 'fun']):
            return "Entertainment"
        elif any(word in name_lower for word in ['shopping', 'clothes', 'electronics']):
            return "Shopping"
        elif any(word in name_lower for word in ['bills', 'electricity', 'water', 'internet']):
            return "Bills"
        elif any(word in name_lower for word in ['health', 'medical', 'doctor', 'medicine']):
            return "Healthcare"
        return "General"
