# Finance Manager - Django

A powerful personal finance management web application built using Django with AI/ML capabilities. This comprehensive application helps users track their income, expenses, and budgets efficiently with intelligent insights and predictions.

## 🚀 Features

### Core Features
- **User Authentication & Registration** - Secure user management system
- **Expense Tracking** - Add, edit, delete, and categorize expenses
- **Income Management** - Track various income sources
- **Financial Reports** - Interactive charts and monthly summaries
- **Account Management** - Multiple account support with balance tracking
- **Long-term Financial Planning** - Support for loans, investments with interest calculations

### AI/ML Features
- **Expense Prediction** - ML-powered expense forecasting
- **Anomaly Detection** - Identify unusual spending patterns
- **Financial Insights** - AI-generated recommendations
- **Trend Analysis** - Historical data analysis and trends

### API Features
- **RESTful API** - Complete API for mobile/web integration
- **Swagger Documentation** - Interactive API documentation
- **CORS Support** - Cross-origin resource sharing enabled

## 🛠️ Technology Stack

- **Backend**: Django 5.2.1
- **Database**: PostgreSQL (with SQLite for development)
- **Frontend**: HTML, CSS, JavaScript
- **Charts**: Plotly.js
- **AI/ML**: Scikit-learn, Pandas, NumPy
- **API**: Django REST Framework
- **Documentation**: Swagger/OpenAPI
- **Deployment**: Gunicorn, WhiteNoise

## 📋 Prerequisites

Before running this application, make sure you have the following installed:

- Python 3.8 or higher
- PostgreSQL (for production) or SQLite (for development)
- pip (Python package installer)

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/widushan/FinanceManager---Django.git
cd FinanceManager---Django
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup

#### Option A: SQLite (Development - Default)
The application is configured to use SQLite by default for development. No additional setup required.

#### Option B: PostgreSQL (Production)
1. Install PostgreSQL
2. Create a database named `finance`
3. Update database settings in `ExpenseTracker/ExpenseTracker/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'finance',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432'
    }
}
```

### 5. Run Migrations

```bash
cd ExpenseTracker
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 7. Run the Development Server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## 📱 Usage

### Web Interface
1. **Home Page**: `http://127.0.0.1:8000/`
2. **Register**: `http://127.0.0.1:8000/accounts/register/`
3. **Login**: `http://127.0.0.1:8000/accounts/login/`
4. **Expenses**: `http://127.0.0.1:8000/expenses`
5. **Incomes**: `http://127.0.0.1:8000/incomes`
6. **Reports**: `http://127.0.0.1:8000/report/`
7. **AI Insights**: `http://127.0.0.1:8000/ai-insights/`

### API Endpoints
- **API Root**: `http://127.0.0.1:8000/api/v1/`
- **Swagger Documentation**: `http://127.0.0.1:8000/swagger/`
- **ReDoc Documentation**: `http://127.0.0.1:8000/redoc/`

### Admin Interface
- **Django Admin**: `http://127.0.0.1:8000/admin/`

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root for sensitive configuration:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgresql://user:password@localhost:5432/finance
```

### Static Files
For production, collect static files:

```bash
python manage.py collectstatic
```

## 🧪 Testing

Run the test suite:

```bash
python manage.py test
```



## 📊 Project Structure

```
FinanceManager---Django/
├── ExpenseTracker/
│   ├── exp_tracker/           # Main Django app
│   │   ├── models.py         # Database models
│   │   ├── views.py          # View logic
│   │   ├── urls.py           # URL routing
│   │   ├── api_views.py      # API views
│   │   ├── serializers.py    # API serializers
│   │   ├── ml_models.py      # AI/ML functionality
│   │   ├── templates/        # HTML templates
│   │   └── static/          # CSS, JS, images
│   ├── ExpenseTracker/       # Django project settings
│   │   ├── settings.py      # Project configuration
│   │   └── urls.py          # Main URL configuration
│   └── manage.py            # Django management script
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── Procfile               # Heroku deployment
```

## 🤖 AI/ML Features

### Expense Prediction
The application uses machine learning to predict future expenses based on historical data:

```python
# Train the model
POST /api/train-model/

# Get predictions
GET /api/predict-expenses/
```

### Anomaly Detection
Identifies unusual spending patterns:

```python
GET /api/anomalies/
```

### Financial Insights
AI-generated recommendations for better financial management.

## 🔌 API Documentation

### Authentication
The API supports token-based authentication and session authentication.

### Endpoints
- `GET /api/v1/accounts/` - List user accounts
- `POST /api/v1/accounts/` - Create new account
- `GET /api/v1/expenses/` - List expenses
- `POST /api/v1/expenses/` - Create new expense
- `GET /api/v1/incomes/` - List incomes
- `POST /api/v1/incomes/` - Create new income
- `GET /api/v1/reports/financial/` - Get financial reports
- `GET /api/v1/ai/insights/` - Get AI insights

For complete API documentation, visit: `http://127.0.0.1:8000/swagger/`

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure PostgreSQL is running
   - Check database credentials in settings.py
   - Verify database exists

2. **Static Files Not Loading**
   - Run `python manage.py collectstatic`
   - Check STATIC_URL and STATIC_ROOT settings

3. **ML Features Not Working**
   - Install required packages: `pip install scikit-learn pandas joblib`
   - Ensure you have sufficient data for training

4. **Migration Errors**
   - Delete migration files and recreate: `python manage.py makemigrations --empty app_name`
   - Reset database if needed

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Support

For support and questions:
- Create an issue in the repository
- Contact: pasindukavishka2001@gmail.com

## 🔄 Version History

- **v1.0.0** - Initial release with basic expense tracking
- **v1.1.0** - Added AI/ML features and API
- **v1.2.0** - Enhanced reporting and user interface

---

**Note**: This application is designed for personal use and educational purposes. For production deployment, ensure proper security measures and data protection compliance.
