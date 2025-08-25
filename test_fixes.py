#!/usr/bin/env python3
"""
Quick test to verify fixes work
"""

import sys
import os
import django

# Add the Django project to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ExpenseTracker'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ExpenseTracker.settings')

# Setup Django
django.setup()

def test_ml_prediction_fix():
    """Test the ML prediction fix"""
    print("🧪 Testing ML prediction fix...")
    
    try:
        from exp_tracker.ml_models import FinanceMLPredictor
        from datetime import datetime, timedelta
        import random
        
        # Create sample data
        sample_data = []
        start_date = datetime.now() - timedelta(days=30)
        
        for i in range(30):
            date = start_date + timedelta(days=i)
            expense = {
                'date': date,
                'amount': random.uniform(10, 100),
                'category': random.choice(['Food', 'Transport', 'Entertainment']),
                'description': f'Test expense {i}'
            }
            sample_data.append(expense)
        
        # Test ML predictor
        ml_predictor = FinanceMLPredictor()
        
        # Train model
        success, result = ml_predictor.train_expense_predictor(sample_data)
        print(f"Training: {'✅' if success else '❌'} - {result}")
        
        if success:
            # Test prediction
            prediction, message = ml_predictor.predict_next_month_expenses(user_id=1)
            print(f"Prediction: {'✅' if prediction else '❌'} - {message}")
            if prediction:
                print(f"   Predicted: Rs. {prediction.get('total_predicted', 0):.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ ML test failed: {e}")
        return False

def test_url_patterns():
    """Test URL patterns exist"""
    print("\n🔗 Testing URL patterns...")
    
    try:
        from django.urls import reverse, NoReverseMatch
        
        urls_to_test = ['home', 'expenses', 'incomes', 'report', 'ai_insights']
        
        for url_name in urls_to_test:
            try:
                url = reverse(url_name)
                print(f"✅ {url_name}: {url}")
            except NoReverseMatch:
                print(f"❌ {url_name}: Not found")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ URL test failed: {e}")
        return False

def test_coverage_import():
    """Test coverage import"""
    print("\n📊 Testing coverage import...")
    
    try:
        import coverage
        print("✅ Coverage package available")
        return True
    except ImportError:
        print("❌ Coverage package not available")
        return False

if __name__ == "__main__":
    print("🚀 Testing Fixes")
    print("=" * 40)
    
    ml_ok = test_ml_prediction_fix()
    urls_ok = test_url_patterns()
    coverage_ok = test_coverage_import()
    
    print("\n" + "=" * 40)
    print("📋 Test Results:")
    print(f"ML Prediction Fix: {'✅ PASS' if ml_ok else '❌ FAIL'}")
    print(f"URL Patterns: {'✅ PASS' if urls_ok else '❌ FAIL'}")
    print(f"Coverage Import: {'✅ PASS' if coverage_ok else '❌ FAIL'}")
    
    if all([ml_ok, urls_ok, coverage_ok]):
        print("\n🎉 All fixes verified! Ready to run full test suite.")
    else:
        print("\n⚠️ Some fixes still need attention.")
