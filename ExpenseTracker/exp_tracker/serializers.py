from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Account, Expense, Income
from datetime import datetime


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class AccountSerializer(serializers.ModelSerializer):
    """Serializer for Account model"""
    user = UserSerializer(read_only=True)
    total_expenses = serializers.SerializerMethodField()
    total_incomes = serializers.SerializerMethodField()
    balance = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = ['id', 'name', 'user', 'expense', 'income', 'balance', 
                 'total_expenses', 'total_incomes']
        read_only_fields = ['id', 'expense', 'income', 'balance']

    def get_total_expenses(self, obj):
        """Calculate total expenses from expense_list"""
        return sum(expense.amount for expense in obj.expense_list.all())

    def get_total_incomes(self, obj):
        """Calculate total incomes from income_list"""
        return sum(income.amount for income in obj.income_list.all())

    def get_balance(self, obj):
        """Calculate current balance"""
        return self.get_total_incomes(obj) - self.get_total_expenses(obj)


class ExpenseSerializer(serializers.ModelSerializer):
    """Serializer for Expense model"""
    user = UserSerializer(read_only=True)
    category = serializers.SerializerMethodField()
    monthly_expenses_display = serializers.SerializerMethodField()
    days_remaining = serializers.SerializerMethodField()

    class Meta:
        model = Expense
        fields = ['id', 'name', 'amount', 'date', 'long_term', 'interest_rate', 
                 'end_date', 'monthly_expenses', 'monthly_expenses_display', 
                 'user', 'category', 'days_remaining']
        read_only_fields = ['id', 'monthly_expenses']

    def get_category(self, obj):
        """Infer category from expense name"""
        name_lower = obj.name.lower()
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

    def get_monthly_expenses_display(self, obj):
        """Get formatted monthly expenses"""
        if obj.monthly_expenses:
            return f"Rs. {obj.monthly_expenses:.2f}"
        return "N/A"

    def get_days_remaining(self, obj):
        """Calculate days remaining for long-term expenses"""
        if obj.long_term and obj.end_date:
            remaining = obj.end_date - datetime.now().date()
            return max(0, remaining.days)
        return None


class IncomeSerializer(serializers.ModelSerializer):
    """Serializer for Income model"""
    user = UserSerializer(read_only=True)
    monthly_incomes_display = serializers.SerializerMethodField()
    days_remaining = serializers.SerializerMethodField()

    class Meta:
        model = Income
        fields = ['id', 'name', 'amount', 'date', 'long_term', 'interest_rate', 
                 'end_date', 'monthly_incomes', 'monthly_incomes_display', 
                 'user', 'days_remaining']
        read_only_fields = ['id', 'monthly_incomes']

    def get_monthly_incomes_display(self, obj):
        """Get formatted monthly incomes"""
        if obj.monthly_incomes:
            return f"Rs. {obj.monthly_incomes:.2f}"
        return "N/A"

    def get_days_remaining(self, obj):
        """Calculate days remaining for long-term incomes"""
        if obj.long_term and obj.end_date:
            remaining = obj.end_date - datetime.now().date()
            return max(0, remaining.days)
        return None


class ExpenseCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating expenses"""
    class Meta:
        model = Expense
        fields = ['name', 'amount', 'date', 'long_term', 'interest_rate', 'end_date']

    def create(self, validated_data):
        """Create expense and associate with user"""
        user = self.context['request'].user
        expense = Expense.objects.create(user=user, **validated_data)
        
        # Associate with user's account
        account, _ = Account.objects.get_or_create(user=user)
        account.expense_list.add(expense)
        
        return expense


class IncomeCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating incomes"""
    class Meta:
        model = Income
        fields = ['name', 'amount', 'date', 'long_term', 'interest_rate', 'end_date']

    def create(self, validated_data):
        """Create income and associate with user"""
        user = self.context['request'].user
        income = Income.objects.create(user=user, **validated_data)
        
        # Associate with user's account
        account, _ = Account.objects.get_or_create(user=user)
        account.income_list.add(income)
        
        return income


class FinancialStatsSerializer(serializers.Serializer):
    """Serializer for financial statistics"""
    total_expenses = serializers.FloatField()
    total_incomes = serializers.FloatField()
    balance = serializers.FloatField()
    expense_count = serializers.IntegerField()
    income_count = serializers.IntegerField()
    monthly_expenses = serializers.FloatField()
    monthly_incomes = serializers.FloatField()
    profit_margin = serializers.FloatField()
    top_expense_category = serializers.CharField()
    top_income_source = serializers.CharField()


class MonthlyDataSerializer(serializers.Serializer):
    """Serializer for monthly financial data"""
    month = serializers.CharField()
    expenses = serializers.FloatField()
    incomes = serializers.FloatField()
    profit_loss = serializers.FloatField()
    profit_loss_percentage = serializers.FloatField()
    status = serializers.CharField()


class AIInsightSerializer(serializers.Serializer):
    """Serializer for AI insights"""
    total_expenses_analyzed = serializers.IntegerField()
    date_range = serializers.DictField()
    pattern_analysis = serializers.DictField()
    anomalies = serializers.ListField()
    prediction = serializers.DictField(allow_null=True)
    model_status = serializers.CharField()


class CategoryBreakdownSerializer(serializers.Serializer):
    """Serializer for category breakdown"""
    category = serializers.CharField()
    total_amount = serializers.FloatField()
    percentage = serializers.FloatField()
    count = serializers.IntegerField()


class ExpenseSummarySerializer(serializers.Serializer):
    """Serializer for expense summary"""
    total_amount = serializers.FloatField()
    average_amount = serializers.FloatField()
    count = serializers.IntegerField()
    categories = CategoryBreakdownSerializer(many=True)
    monthly_trend = serializers.ListField()


class IncomeSummarySerializer(serializers.Serializer):
    """Serializer for income summary"""
    total_amount = serializers.FloatField()
    average_amount = serializers.FloatField()
    count = serializers.IntegerField()
    monthly_trend = serializers.ListField()
