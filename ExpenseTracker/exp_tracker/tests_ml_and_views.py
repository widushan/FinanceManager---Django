from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from exp_tracker.ml_models import FinanceMLPredictor
from exp_tracker.models import Expense


class MLAnomalyDetectionTests(TestCase):
    def test_detect_anomalies_insufficient_data(self):
        ml = FinanceMLPredictor()
        small = [
            {'date': '2024-01-01', 'amount': 10, 'category': 'General'},
            {'date': '2024-01-02', 'amount': 12, 'category': 'General'},
            {'date': '2024-01-03', 'amount': 11, 'category': 'General'},
            {'date': '2024-01-04', 'amount': 9, 'category': 'General'},
        ]
        anomalies, msg = ml.detect_anomalies(small)
        self.assertEqual(anomalies, [])
        self.assertIn('Insufficient data', msg)

    def test_detect_anomalies_contamination_effect(self):
        data = []
        for i in range(1, 31):
            amt = 100
            if i == 15:
                amt = 600  # clear outlier
            data.append({'date': f'2024-01-{i:02d}', 'amount': amt, 'category': 'General'})

        ml = FinanceMLPredictor()
        anomalies_low, _ = ml.detect_anomalies(data, contamination=0.02)
        anomalies_high, _ = ml.detect_anomalies(data, contamination=0.2)
        self.assertGreaterEqual(len(anomalies_high), len(anomalies_low))


class MLTrainingPredictionTests(TestCase):
    def test_train_insufficient_data(self):
        ml = FinanceMLPredictor()
        tiny = [
            {'date': '2024-01-01', 'amount': 10, 'category': 'General'}
            for _ in range(8)
        ]
        ok, msg = ml.train_expense_predictor(tiny)
        self.assertFalse(ok)
        self.assertIn('Insufficient data', msg)

    def test_predict_without_training(self):
        ml = FinanceMLPredictor()
        result = ml.predict_next_month_expenses(user_id=1)
        # Function may return a tuple (None, msg) if no model is trained,
        # or a dict if a previously trained model exists on disk.
        if isinstance(result, tuple):
            res, msg = result
            self.assertIsNone(res)
            self.assertIn('Model not trained yet', msg)
        else:
            self.assertIsInstance(result, dict)
            self.assertIn('total_predicted', result)


class APIAnomaliesTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('u', 'u@example.com', 'p')
        self.client.login(username='u', password='p')

    def test_get_anomalies_no_expenses(self):
        resp = self.client.get(reverse('get_anomalies'))
        # When no expenses exist, view returns a success False JSON
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertIn('success', body)
        self.assertFalse(body['success'])

    def test_get_anomalies_with_data(self):
        # Seed some expenses so endpoint exercises ML path or fallback
        for i in range(1, 8):
            Expense.objects.create(
                name='Groceries' if i != 6 else 'Electronics',
                amount=100 if i != 6 else 600,
                date=timezone.now().date(),
                user=self.user
            )
        resp = self.client.get(reverse('get_anomalies'))
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        # In ML mode response has anomalies list; in fallback we still expect a list
        self.assertIn('anomalies', body)
        self.assertIsInstance(body['anomalies'], list)


