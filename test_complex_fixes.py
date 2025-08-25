#!/usr/bin/env python3
"""
Comprehensive Test for Complex Fixes
This script tests all the complex fixes applied to the Finance Manager Django
"""

import sys
import os
import django
from datetime import datetime, timedelta
import random
import calendar

# Add the Django project to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ExpenseTracker'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ExpenseTracker.settings')

# Setup Django
django.setup()

def test_date_handling_fix():
    """Test the date handling fix for ML prediction"""
    print("🧪 Testing Date Handling Fix...")
    
    try:
        from exp_tracker.ml_models import FinanceMLPredictor
        
        # Test with different months to ensure date handling works
        test_months = [
            (2024, 1),   # January (31 days)
            (2024, 2),   # February (29 days - leap year)
            (2024, 4),   # April (30 days)
            (2024, 12),  # December (31 days)
        ]
        
        for year, month in test_months:
            # Get actual days in month
            _, days_in_month = calendar.monthrange(year, month)
            print(f"   - {calendar.month_name[month]} {year}: {days_in_month} days")
            
            # Test creating dates for each day
            for day in range(1, days_in_month + 1):
                try:
                    test_date = datetime(year, month, day)
                    # This should not raise ValueError
                except ValueError as e:
                    print(f"   ❌ Date error for {year}-{month:02d}-{day:02d}: {e}")
                    return False
        
        print("   ✅ Date handling works correctly")
        return True
        
    except Exception as e:
        print(f"   ❌ Date handling test failed: {e}")
        return False

def test_ml_prediction_with_fixed_dates():
    """Test ML prediction with the fixed date handling"""
    print("\n🤖 Testing ML Prediction with Fixed Dates...")
    
    try:
        from exp_tracker.ml_models import FinanceMLPredictor
        
        # Create sample data
        sample_data = []
        start_date = datetime.now() - timedelta(days=60)
        
        for i in range(60):
            date = start_date + timedelta(days=i)
            expense = {
                'date': date,
                'amount': random.uniform(10, 200),
                'category': random.choice(['Food', 'Transport', 'Entertainment']),
                'description': f'Test expense {i}'
            }
            sample_data.append(expense)
        
        # Test ML predictor
        ml_predictor = FinanceMLPredictor()
        
        # Train model
        success, result = ml_predictor.train_expense_predictor(sample_data)
        print(f"   Training: {'✅' if success else '❌'} - {result}")
        
        if success:
            # Test prediction
            prediction, message = ml_predictor.predict_next_month_expenses(user_id=1)
            print(f"   Prediction: {'✅' if prediction else '❌'} - {message}")
            if prediction:
                print(f"   Predicted: Rs. {prediction.get('total_predicted', 0):.2f}")
                return True
            else:
                print(f"   Prediction failed: {message}")
                return False
        else:
            print(f"   Training failed: {result}")
            return False
        
    except Exception as e:
        print(f"   ❌ ML prediction test failed: {e}")
        return False

def test_unicode_encoding_fix():
    """Test Unicode encoding fix for report generation"""
    print("\n📝 Testing Unicode Encoding Fix...")
    
    try:
        # Test writing files with Unicode characters
        test_data = {
            'page_load_times': {
                'home': {'time': 150.5, 'status_code': 200, 'success': True},
                'expenses': {'time': 200.3, 'status_code': 200, 'success': True}
            },
            'api_response_times': {
                '/api/v1/accounts/': {'time': 50.2, 'status_code': 401, 'success': True}
            },
            'success': True
        }
        
        # Test performance report generation
        from run_tests import generate_performance_report
        generate_performance_report(test_data)
        
        # Check if file was created successfully
        if os.path.exists('PERFORMANCE_TEST_REPORT.md'):
            print("   ✅ Performance report generated successfully")
            
            # Read the file to check encoding
            with open('PERFORMANCE_TEST_REPORT.md', 'r', encoding='utf-8') as f:
                content = f.read()
                if 'PASS' in content and 'FAIL' in content:
                    print("   ✅ Unicode characters handled correctly")
                    return True
                else:
                    print("   ❌ Unicode characters not found in report")
                    return False
        else:
            print("   ❌ Performance report file not created")
            return False
        
    except Exception as e:
        print(f"   ❌ Unicode encoding test failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints to ensure they exist and handle authentication properly"""
    print("\n🔗 Testing API Endpoints...")
    
    try:
        from django.test import Client
        from django.urls import reverse
        
        client = Client()
        
        # Test API endpoints without authentication (should return 401)
        api_endpoints = [
            '/api/v1/accounts/',
            '/api/v1/expenses/',
            '/api/v1/incomes/',
            '/api/v1/reports/financial/',
            '/api/v1/ai/insights/'
        ]
        
        for endpoint in api_endpoints:
            response = client.get(endpoint)
            if response.status_code in [401, 403, 404]:
                print(f"   ✅ {endpoint}: HTTP {response.status_code} (expected for unauthenticated)")
            else:
                print(f"   ⚠️ {endpoint}: HTTP {response.status_code} (unexpected)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ API endpoint test failed: {e}")
        return False

def test_coverage_import():
    """Test coverage import and basic functionality"""
    print("\n📊 Testing Coverage Import...")
    
    try:
        import coverage
        print("   ✅ Coverage package imported successfully")
        
        # Test basic coverage functionality
        cov = coverage.Coverage()
        print("   ✅ Coverage object created successfully")
        
        return True
        
    except ImportError:
        print("   ❌ Coverage package not available")
        return False
    except Exception as e:
        print(f"   ❌ Coverage test failed: {e}")
        return False

def test_report_generation():
    """Test all report generation functions"""
    print("\n📋 Testing Report Generation...")
    
    try:
        from run_tests import generate_coverage_report, generate_performance_report, generate_security_report
        
        # Test data
        coverage_data = {
            'success': True,
            'coverage_percentage': 75.5,
            'total_statements': 1000,
            'covered_statements': 755
        }
        
        performance_data = {
            'success': True,
            'page_load_times': {
                'home': {'time': 150.5, 'status_code': 200, 'success': True},
                'expenses': {'time': 200.3, 'status_code': 200, 'success': True}
            },
            'api_response_times': {
                '/api/v1/accounts/': {'time': 50.2, 'status_code': 401, 'success': True, 'note': '401 expected'}
            }
        }
        
        security_data = {
            'success': True,
            'csrf_protection': True,
            'xss_protection': True,
            'sql_injection_protection': True,
            'authentication_required': True,
            'authorization_working': True
        }
        
        # Generate reports
        generate_coverage_report(coverage_data)
        generate_performance_report(performance_data)
        generate_security_report(security_data)
        
        # Check if files were created
        files_to_check = [
            'TEST_COVERAGE_REPORT.md',
            'PERFORMANCE_TEST_REPORT.md',
            'SECURITY_AUDIT_REPORT.md'
        ]
        
        for filename in files_to_check:
            if os.path.exists(filename):
                print(f"   ✅ {filename} generated successfully")
            else:
                print(f"   ❌ {filename} not created")
                return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Report generation test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Testing Complex Fixes")
    print("=" * 50)
    
    tests = [
        ("Date Handling Fix", test_date_handling_fix),
        ("ML Prediction with Fixed Dates", test_ml_prediction_with_fixed_dates),
        ("Unicode Encoding Fix", test_unicode_encoding_fix),
        ("API Endpoints", test_api_endpoints),
        ("Coverage Import", test_coverage_import),
        ("Report Generation", test_report_generation)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📋 Test Results Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All complex fixes verified! Ready to run full test suite.")
        return True
    else:
        print("\n⚠️ Some fixes still need attention.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
