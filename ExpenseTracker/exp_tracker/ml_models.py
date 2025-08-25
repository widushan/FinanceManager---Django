import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os
from datetime import datetime, timedelta
from django.conf import settings


class FinanceMLPredictor:
    """
    AI/ML class for financial predictions and analysis
    """
    
    def __init__(self):
        self.expense_model = None
        self.anomaly_detector = None
        self.scaler = StandardScaler()
        self.model_path = os.path.join(settings.BASE_DIR, 'exp_tracker', 'ml_models')
        os.makedirs(self.model_path, exist_ok=True)
        
    def prepare_expense_data(self, expenses_data):
        """
        Prepare expense data for ML training
        """
        df = pd.DataFrame(expenses_data)
        
        # Convert date to features
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.month
        df['day_of_week'] = df['date'].dt.dayofweek
        df['day_of_month'] = df['date'].dt.day
        df['quarter'] = df['date'].dt.quarter
        
        # Create category features (one-hot encoding)
        category_dummies = pd.get_dummies(df['category'], prefix='category')
        df = pd.concat([df, category_dummies], axis=1)
        
        # Select features for training
        feature_columns = ['month', 'day_of_week', 'day_of_month', 'quarter'] + \
                         [col for col in df.columns if col.startswith('category_')]
        
        X = df[feature_columns]
        y = df['amount']
        
        return X, y, feature_columns
    
    def train_expense_predictor(self, expenses_data):
        """
        Train a model to predict future expenses
        """
        try:
            X, y, feature_columns = self.prepare_expense_data(expenses_data)
            
            if len(X) < 10:  # Need minimum data points
                return False, "Insufficient data for training (need at least 10 records)"
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.expense_model = LinearRegression()
            self.expense_model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = self.expense_model.predict(X_test_scaled)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # Save model and scaler
            joblib.dump(self.expense_model, os.path.join(self.model_path, 'expense_predictor.pkl'))
            joblib.dump(self.scaler, os.path.join(self.model_path, 'expense_scaler.pkl'))
            joblib.dump(feature_columns, os.path.join(self.model_path, 'feature_columns.pkl'))
            
            return True, {
                'mae': round(mae, 2),
                'r2': round(r2, 3),
                'training_samples': len(X_train),
                'test_samples': len(X_test)
            }
            
        except Exception as e:
            return False, f"Training failed: {str(e)}"
    
    def predict_next_month_expenses(self, user_id, current_month_data=None):
        """
        Predict expenses for the next month
        """
        try:
            # Load model if not loaded
            feature_columns = None
            if self.expense_model is None:
                model_file = os.path.join(self.model_path, 'expense_predictor.pkl')
                if os.path.exists(model_file):
                    self.expense_model = joblib.load(model_file)
                    self.scaler = joblib.load(os.path.join(self.model_path, 'expense_scaler.pkl'))
                    feature_columns = joblib.load(os.path.join(self.model_path, 'feature_columns.pkl'))
                else:
                    return None, "Model not trained yet"
            else:
                # Load feature columns if model is already loaded
                feature_columns_file = os.path.join(self.model_path, 'feature_columns.pkl')
                if os.path.exists(feature_columns_file):
                    feature_columns = joblib.load(feature_columns_file)
                else:
                    return None, "Feature columns not found"
            
            # Create prediction data for next month
            next_month = datetime.now().replace(day=1) + timedelta(days=32)
            next_month = next_month.replace(day=1)
            
            # Get the actual number of days in the next month
            import calendar
            _, days_in_month = calendar.monthrange(next_month.year, next_month.month)
            
            # Generate features for next month
            prediction_data = []
            for day in range(1, days_in_month + 1):  # Use actual days in month
                try:
                    date = next_month.replace(day=day)
                    row = {
                        'month': date.month,
                        'day_of_week': date.weekday(),
                        'day_of_month': date.day,
                        # Python datetime has no quarter attribute; compute manually
                        'quarter': ((date.month - 1) // 3) + 1
                    }
                    # Add category features (assuming most common categories)
                    for col in feature_columns:
                        if col.startswith('category_'):
                            row[col] = 0  # Default to 0, can be enhanced with user preferences
                    prediction_data.append(row)
                except ValueError:
                    # Skip invalid dates (shouldn't happen with proper day calculation)
                    continue
            
            X_pred = pd.DataFrame(prediction_data)
            X_pred_scaled = self.scaler.transform(X_pred[feature_columns])
            
            # Make predictions
            predictions = self.expense_model.predict(X_pred_scaled)
            
            # Aggregate predictions
            total_predicted = np.sum(predictions)
            daily_average = np.mean(predictions)
            
            return {
                'total_predicted': round(total_predicted, 2),
                'daily_average': round(daily_average, 2),
                'month': next_month.strftime('%B %Y'),
                'confidence': 'Medium'  # Can be enhanced with prediction intervals
            }
            
        except Exception as e:
            return None, f"Prediction failed: {str(e)}"
    
    def detect_anomalies(self, expenses_data, contamination=0.1):
        """
        Detect unusual spending patterns
        """
        try:
            df = pd.DataFrame(expenses_data)
            
            if len(df) < 5:
                return [], "Insufficient data for anomaly detection"
            
            # Prepare features for anomaly detection
            features = df[['amount']].copy()
            
            # Add time-based features
            df['date'] = pd.to_datetime(df['date'])
            features['days_since_start'] = (df['date'] - df['date'].min()).dt.days
            features['day_of_week'] = df['date'].dt.dayofweek
            
            # Scale features
            features_scaled = self.scaler.fit_transform(features)
            
            # Train anomaly detector
            self.anomaly_detector = IsolationForest(
                contamination=contamination,
                random_state=42
            )
            self.anomaly_detector.fit(features_scaled)
            
            # Detect anomalies
            anomaly_scores = self.anomaly_detector.predict(features_scaled)
            anomaly_indices = np.where(anomaly_scores == -1)[0]
            
            anomalies = []
            for idx in anomaly_indices:
                anomaly = {
                    'date': df.iloc[idx]['date'].strftime('%Y-%m-%d'),
                    'amount': df.iloc[idx]['amount'],
                    'category': df.iloc[idx]['category'],
                    'description': df.iloc[idx].get('description', ''),
                    'anomaly_score': float(anomaly_scores[idx])
                }
                anomalies.append(anomaly)
            
            return anomalies, f"Detected {len(anomalies)} anomalies"
            
        except Exception as e:
            return [], f"Anomaly detection failed: {str(e)}"
    
    def analyze_spending_patterns(self, expenses_data):
        """
        Analyze spending patterns and provide insights
        """
        try:
            df = pd.DataFrame(expenses_data)
            
            if len(df) == 0:
                return {}, "No data available for analysis"
            
            df['date'] = pd.to_datetime(df['date'])
            
            # Basic statistics
            total_spent = df['amount'].sum()
            avg_daily = df.groupby(df['date'].dt.date)['amount'].sum().mean()
            avg_transaction = df['amount'].mean()
            
            # Category analysis
            category_totals = df.groupby('category')['amount'].sum().sort_values(ascending=False)
            top_category = category_totals.index[0] if len(category_totals) > 0 else "None"
            
            # Time-based patterns
            monthly_totals = df.groupby(df['date'].dt.to_period('M'))['amount'].sum()
            #day_of_week_totals = df.groupby(df['date'].dt.dayofweek)['amount'].sum()
            
            # Spending trends
            if len(monthly_totals) > 1:
                trend = "Increasing" if monthly_totals.iloc[-1] > monthly_totals.iloc[-2] else "Decreasing"
            else:
                trend = "Stable"
            
            # Recommendations
            recommendations = []
            if avg_daily > total_spent * 0.1:  # If daily average is more than 10% of total
                recommendations.append("Consider spreading expenses more evenly throughout the month")
            
            if category_totals.iloc[0] > total_spent * 0.5:  # If top category is more than 50%
                recommendations.append(f"Your spending is heavily concentrated in {top_category}. Consider diversifying expenses.")
            
            analysis = {
                'total_spent': round(total_spent, 2),
                'avg_daily_spending': round(avg_daily, 2),
                'avg_transaction': round(avg_transaction, 2),
                'top_category': top_category,
                'top_category_percentage': round((category_totals.iloc[0] / total_spent * 100), 1) if len(category_totals) > 0 else 0,
                'spending_trend': trend,
                'total_transactions': len(df),
                'date_range': {
                    'start': df['date'].min().strftime('%Y-%m-%d'),
                    'end': df['date'].max().strftime('%Y-%m-%d')
                },
                'recommendations': recommendations
            }
            
            return analysis, "Analysis completed successfully"
            
        except Exception as e:
            return {}, f"Pattern analysis failed: {str(e)}"

# Global instance
ml_predictor = FinanceMLPredictor()
