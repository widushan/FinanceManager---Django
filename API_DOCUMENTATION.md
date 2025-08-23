# Finance Manager API Documentation

## Overview

The Finance Manager API provides a comprehensive RESTful interface for personal finance management, including expense tracking, income management, financial reporting, and AI-powered insights.

**Base URL**: `http://localhost:8000/api/v1/`

## Authentication

The API uses Django's session authentication. Users must be logged in to access protected endpoints.

### Authentication Methods:
- **Session Authentication**: Use Django's built-in session authentication
- **Basic Authentication**: For API clients, use HTTP Basic Auth

## API Endpoints

### 1. Accounts

#### Get User Account
```http
GET /api/v1/accounts/
```

**Response:**
```json
{
    "id": 1,
    "name": "My Account",
    "user": {
        "id": 1,
        "username": "user123",
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "date_joined": "2024-01-01T00:00:00Z"
    },
    "expense": 0.0,
    "income": 0.0,
    "balance": 0.0,
    "total_expenses": 1500.0,
    "total_incomes": 3000.0
}
```

#### Get Account Summary
```http
GET /api/v1/accounts/summary/
```

**Response:**
```json
{
    "total_expenses": 1500.0,
    "total_incomes": 3000.0,
    "balance": 1500.0,
    "expense_count": 15,
    "income_count": 5,
    "monthly_expenses": 500.0,
    "monthly_incomes": 1000.0,
    "profit_margin": 50.0,
    "top_expense_category": "Food",
    "top_income_source": "Salary"
}
```

### 2. Expenses

#### List All Expenses
```http
GET /api/v1/expenses/
```

**Query Parameters:**
- `page`: Page number for pagination
- `page_size`: Number of items per page (default: 20)

**Response:**
```json
{
    "count": 15,
    "next": "http://localhost:8000/api/v1/expenses/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Grocery Shopping",
            "amount": 150.0,
            "date": "2024-01-15",
            "long_term": false,
            "interest_rate": 0.0,
            "end_date": null,
            "monthly_expenses": null,
            "monthly_expenses_display": "N/A",
            "user": {
                "id": 1,
                "username": "user123",
                "email": "user@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "date_joined": "2024-01-01T00:00:00Z"
            },
            "category": "Food",
            "days_remaining": null
        }
    ]
}
```

#### Create New Expense
```http
POST /api/v1/expenses/
```

**Request Body:**
```json
{
    "name": "Grocery Shopping",
    "amount": 150.0,
    "date": "2024-01-15",
    "long_term": false,
    "interest_rate": 0.0,
    "end_date": null
}
```

#### Get Expense Summary
```http
GET /api/v1/expenses/summary/
```

**Response:**
```json
{
    "total_amount": 1500.0,
    "average_amount": 100.0,
    "count": 15,
    "categories": [
        {
            "category": "Food",
            "total_amount": 600.0,
            "percentage": 40.0,
            "count": 6
        },
        {
            "category": "Transport",
            "total_amount": 300.0,
            "percentage": 20.0,
            "count": 3
        }
    ],
    "monthly_trend": [
        {
            "month": "2024-01",
            "total": 500.0,
            "count": 5
        },
        {
            "month": "2023-12",
            "total": 400.0,
            "count": 4
        }
    ]
}
```

#### Get Expenses by Category
```http
GET /api/v1/expenses/by_category/?category=Food
```

#### Get Recent Expenses
```http
GET /api/v1/expenses/recent/
```

#### Update Expense
```http
PUT /api/v1/expenses/{id}/
```

#### Delete Expense
```http
DELETE /api/v1/expenses/{id}/
```

### 3. Incomes

#### List All Incomes
```http
GET /api/v1/incomes/
```

#### Create New Income
```http
POST /api/v1/incomes/
```

**Request Body:**
```json
{
    "name": "Salary",
    "amount": 3000.0,
    "date": "2024-01-01",
    "long_term": true,
    "interest_rate": 0.0,
    "end_date": "2024-12-31"
}
```

#### Get Income Summary
```http
GET /api/v1/incomes/summary/
```

#### Get Recent Incomes
```http
GET /api/v1/incomes/recent/
```

#### Update Income
```http
PUT /api/v1/incomes/{id}/
```

#### Delete Income
```http
DELETE /api/v1/incomes/{id}/
```

### 4. Financial Reports

#### Get Comprehensive Financial Report
```http
GET /api/v1/reports/financial/
```

**Response:**
```json
{
    "monthly_data": [
        {
            "month": "2024-01",
            "expenses": 500.0,
            "incomes": 1000.0,
            "profit_loss": 500.0,
            "profit_loss_percentage": 50.0,
            "status": "profit"
        },
        {
            "month": "2023-12",
            "expenses": 400.0,
            "incomes": 1000.0,
            "profit_loss": 600.0,
            "profit_loss_percentage": 60.0,
            "status": "profit"
        }
    ],
    "current_month": "2024-01",
    "total_months": 2
}
```

### 5. AI Insights

#### Get AI Insights and Predictions
```http
GET /api/v1/ai/insights/
```

**Response:**
```json
{
    "total_expenses_analyzed": 15,
    "date_range": {
        "start": "2023-12-01",
        "end": "2024-01-15"
    },
    "pattern_analysis": {
        "total_spent": 1500.0,
        "avg_daily_spending": 50.0,
        "avg_transaction": 100.0,
        "top_category": "Food",
        "top_category_percentage": 40.0,
        "spending_trend": "Stable",
        "total_transactions": 15,
        "recommendations": [
            "Consider spreading expenses more evenly throughout the month"
        ]
    },
    "anomalies": [
        {
            "date": "2024-01-10",
            "amount": 500.0,
            "category": "Shopping",
            "description": "Electronics Purchase",
            "anomaly_score": -1.0
        }
    ],
    "prediction": {
        "total_predicted": 1200.0,
        "daily_average": 40.0,
        "month": "Next Month",
        "confidence": "Medium"
    },
    "model_status": "Trained"
}
```

## Error Handling

The API returns standard HTTP status codes:

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

### Error Response Format
```json
{
    "error": "Error message description",
    "detail": "Additional error details"
}
```

## Pagination

List endpoints support pagination with the following parameters:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

### Pagination Response Format
```json
{
    "count": 100,
    "next": "http://localhost:8000/api/v1/expenses/?page=2",
    "previous": null,
    "results": [...]
}
```

## Rate Limiting

API requests are limited to:
- 1000 requests per hour per user
- 100 requests per minute per user

## CORS Support

The API supports Cross-Origin Resource Sharing (CORS) for the following origins:
- `http://localhost:3000`
- `http://127.0.0.1:3000`
- `http://localhost:8000`
- `http://127.0.0.1:8000`

## Swagger Documentation

Interactive API documentation is available at:
- **Swagger UI**: `http://localhost:8000/swagger/`
- **ReDoc**: `http://localhost:8000/redoc/`
- **OpenAPI JSON**: `http://localhost:8000/swagger.json`
- **OpenAPI YAML**: `http://localhost:8000/swagger.yaml`

## Usage Examples

### Using cURL

#### Get all expenses
```bash
curl -X GET "http://localhost:8000/api/v1/expenses/" \
  -H "Authorization: Basic dXNlcjEyMzpwYXNzd29yZA=="
```

#### Create a new expense
```bash
curl -X POST "http://localhost:8000/api/v1/expenses/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic dXNlcjEyMzpwYXNzd29yZA==" \
  -d '{
    "name": "Grocery Shopping",
    "amount": 150.0,
    "date": "2024-01-15",
    "long_term": false
  }'
```

### Using Python requests

```python
import requests

# Base URL
base_url = "http://localhost:8000/api/v1"

# Authentication
auth = ('user123', 'password')

# Get all expenses
response = requests.get(f"{base_url}/expenses/", auth=auth)
expenses = response.json()

# Create new expense
new_expense = {
    "name": "Grocery Shopping",
    "amount": 150.0,
    "date": "2024-01-15",
    "long_term": False
}
response = requests.post(f"{base_url}/expenses/", json=new_expense, auth=auth)
created_expense = response.json()

# Get AI insights
response = requests.get(f"{base_url}/ai/insights/", auth=auth)
insights = response.json()
```

### Using JavaScript/Fetch

```javascript
// Base URL
const baseUrl = 'http://localhost:8000/api/v1';

// Get all expenses
async function getExpenses() {
    const response = await fetch(`${baseUrl}/expenses/`, {
        credentials: 'include' // For session authentication
    });
    const expenses = await response.json();
    return expenses;
}

// Create new expense
async function createExpense(expenseData) {
    const response = await fetch(`${baseUrl}/expenses/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(expenseData)
    });
    const newExpense = await response.json();
    return newExpense;
}

// Get AI insights
async function getAIInsights() {
    const response = await fetch(`${baseUrl}/ai/insights/`, {
        credentials: 'include'
    });
    const insights = await response.json();
    return insights;
}
```

## Data Models

### Expense Model
```json
{
    "id": "integer (read-only)",
    "name": "string (required)",
    "amount": "float (required)",
    "date": "date (required)",
    "long_term": "boolean (default: false)",
    "interest_rate": "float (optional)",
    "end_date": "date (optional)",
    "monthly_expenses": "float (read-only)",
    "user": "User object (read-only)",
    "category": "string (auto-generated)",
    "days_remaining": "integer (auto-calculated)"
}
```

### Income Model
```json
{
    "id": "integer (read-only)",
    "name": "string (required)",
    "amount": "float (required)",
    "date": "date (required)",
    "long_term": "boolean (default: false)",
    "interest_rate": "float (optional)",
    "end_date": "date (optional)",
    "monthly_incomes": "float (read-only)",
    "user": "User object (read-only)",
    "days_remaining": "integer (auto-calculated)"
}
```

## Versioning

The API uses URL versioning:
- Current version: `v1`
- Base URL: `/api/v1/`

Future versions will be available at `/api/v2/`, `/api/v3/`, etc.

## Support

For API support and questions:
- Email: contact@financemanager.local
- Documentation: Available at `/swagger/` and `/redoc/`
- GitHub Issues: For bug reports and feature requests
