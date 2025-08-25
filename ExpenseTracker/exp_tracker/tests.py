from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta
import json
from decimal import Decimal

from .models import Account, Expense, Income
from .forms import ExpenseForm, IncomeForm

class FinanceManagerTestCase(TestCase):
    """Base test case with common setup"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.account = Account.objects.create(
            name='Test Account',
            user=self.user,
            expense=0,
            income=0,
            balance=0
        )

class ModelTests(FinanceManagerTestCase):
    """Test cases for database models"""
    
    def test_account_creation(self):
        """Test account creation"""
        account = Account.objects.create(
            name='Savings Account',
            user=self.user,
            expense=1000.0,
            income=2000.0,
            balance=1000.0
        )
        self.assertEqual(account.name, 'Savings Account')
        self.assertEqual(account.balance, 1000.0)
        self.assertEqual(account.user, self.user)
    
    def test_expense_creation(self):
        """Test expense creation"""
        expense = Expense.objects.create(
            name='Groceries',
            amount=150.0,
            date=timezone.now().date(),
            user=self.user,
            long_term=False
        )
        self.assertEqual(expense.name, 'Groceries')
        self.assertEqual(expense.amount, 150.0)
        self.assertFalse(expense.long_term)
    
    def test_income_creation(self):
        """Test income creation"""
        income = Income.objects.create(
            name='Salary',
            amount=5000.0,
            date=timezone.now().date(),
            user=self.user,
            long_term=False
        )
        self.assertEqual(income.name, 'Salary')
        self.assertEqual(income.amount, 5000.0)
        self.assertFalse(income.long_term)
    
    def test_long_term_expense_calculation(self):
        """Test long-term expense monthly calculation"""
        end_date = timezone.now().date() + timedelta(days=365)
        expense = Expense.objects.create(
            name='Car Loan',
            amount=12000.0,
            date=timezone.now().date(),
            user=self.user,
            long_term=True,
            interest_rate=5.0,
            end_date=end_date
        )
        self.assertTrue(expense.long_term)
        self.assertIsNotNone(expense.monthly_expenses)
        self.assertGreater(expense.monthly_expenses, 0)

class ViewTests(FinanceManagerTestCase):
    """Test cases for views"""
    
    def test_home_page(self):
        """Test home page loads correctly"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/home.html')
    
    def test_expense_list_view(self):
        """Test expense list view"""
        # Create test expense
        Expense.objects.create(
            name='Test Expense',
            amount=100.0,
            date=timezone.now().date(),
            user=self.user
        )
        
        # Login and access expense list
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('expenses'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'exp_tracker/expenses_list.html')
    
    def test_income_list_view(self):
        """Test income list view"""
        # Create test income
        Income.objects.create(
            name='Test Income',
            amount=1000.0,
            date=timezone.now().date(),
            user=self.user
        )
        
        # Login and access income list
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('incomes'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'exp_tracker/incomes_list.html')
    
    def test_report_view(self):
        """Test report view"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('report'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'exp_tracker/report.html')
    
    def test_ai_insights_view(self):
        """Test AI insights view"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('ai_insights'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'exp_tracker/ai_insights.html')

class FormTests(FinanceManagerTestCase):
    """Test cases for forms"""
    
    def test_expense_form_valid(self):
        """Test valid expense form"""
        form_data = {
            'name': 'Test Expense',
            'amount': 100.0,
            'date': timezone.now().date(),
            'long_term': False
        }
        form = ExpenseForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_expense_form_invalid(self):
        """Test invalid expense form"""
        form_data = {
            'name': '',  # Empty name
            'amount': -100.0,  # Negative amount
            'date': timezone.now().date(),
            'long_term': False
        }
        form = ExpenseForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_income_form_valid(self):
        """Test valid income form"""
        form_data = {
            'name': 'Test Income',
            'amount': 1000.0,
            'date': timezone.now().date(),
            'long_term': False
        }
        form = IncomeForm(data=form_data)
        self.assertTrue(form.is_valid())

class APITests(FinanceManagerTestCase):
    """Test cases for API endpoints"""
    
    def setUp(self):
        super().setUp()
        self.client.login(username='testuser', password='testpass123')
    
    def test_api_accounts_list(self):
        """Test API accounts list endpoint"""
        response = self.client.get('/api/v1/accounts/')
        self.assertEqual(response.status_code, 200)
    
    def test_api_expenses_list(self):
        """Test API expenses list endpoint"""
        response = self.client.get('/api/v1/expenses/')
        self.assertEqual(response.status_code, 200)
    
    def test_api_incomes_list(self):
        """Test API incomes list endpoint"""
        response = self.client.get('/api/v1/incomes/')
        self.assertEqual(response.status_code, 200)
    
    def test_api_create_expense(self):
        """Test API create expense endpoint"""
        expense_data = {
            'name': 'API Test Expense',
            'amount': 200.0,
            'date': timezone.now().date().isoformat(),
            'long_term': False
        }
        response = self.client.post(
            '/api/v1/expenses/',
            data=json.dumps(expense_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
    
    def test_api_financial_report(self):
        """Test API financial report endpoint"""
        response = self.client.get('/api/v1/reports/financial/')
        self.assertEqual(response.status_code, 200)
    
    def test_api_ai_insights(self):
        """Test API AI insights endpoint"""
        # Ensure there is at least one expense so insights endpoint returns data
        Expense.objects.create(
            name='Seed Expense', amount=10.0, date=timezone.now().date(), user=self.user
        )
        response = self.client.get('/api/v1/ai/insights/')
        self.assertEqual(response.status_code, 200)

class AuthenticationTests(FinanceManagerTestCase):
    """Test cases for authentication"""
    
    def test_register_view(self):
        """Test user registration"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')
    
    def test_login_view(self):
        """Test user login"""
        response = self.client.get('/accounts/login/')
        self.assertEqual(response.status_code, 200)
    
    def test_protected_view_access(self):
        """Test protected views require authentication"""
        # Try to access expense list without login
        response = self.client.get(reverse('expenses'), follow=False)
        self.assertIn(response.status_code, [302, 301])  # Redirect to login
        
        # Login and try again
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('expenses'))
        self.assertEqual(response.status_code, 200)

class SecurityTests(FinanceManagerTestCase):
    """Test cases for security features"""
    
    def test_csrf_protection(self):
        """Test CSRF protection"""
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass123'
        )
        other_account = Account.objects.create(
            name='Other Account',
            user=other_user
        )
        
        # Login as testuser
        self.client.login(username='testuser', password='testpass123')
        
        # Try to access other user's data
        response = self.client.get(f'/api/v1/accounts/{other_account.id}/')
        self.assertEqual(response.status_code, 404)  # Should not be accessible
    
    def test_sql_injection_protection(self):
        """Test SQL injection protection"""
        malicious_input = "'; DROP TABLE exp_tracker_expense; --"
        
        # Try to create expense with malicious input
        expense_data = {
            'name': malicious_input,
            'amount': 100.0,
            'date': timezone.now().date().isoformat(),
            'long_term': False
        }
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            '/api/v1/expenses/',
            data=json.dumps(expense_data),
            content_type='application/json'
        )
        
        # Should handle malicious input safely
        self.assertNotEqual(response.status_code, 500)

class PerformanceTests(FinanceManagerTestCase):
    """Test cases for performance"""
    
    def test_large_dataset_handling(self):
        """Test handling of large datasets"""
        # Create many expenses
        for i in range(100):
            Expense.objects.create(
                name=f'Expense {i}',
                amount=100.0 + i,
                date=timezone.now().date(),
                user=self.user
            )
        
        # Test expense list view performance
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('expenses'))
        self.assertEqual(response.status_code, 200)
        
        # Test API performance
        response = self.client.get('/api/v1/expenses/')
        self.assertEqual(response.status_code, 200)
    
    def test_database_query_optimization(self):
        """Test database query optimization"""
        # Create expenses with different dates
        for i in range(30):
            date = timezone.now().date() - timedelta(days=i)
            Expense.objects.create(
                name=f'Expense {i}',
                amount=100.0,
                date=date,
                user=self.user
            )
        
        # Test report generation performance
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('report'))
        self.assertEqual(response.status_code, 200)
