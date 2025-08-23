from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'accounts', api_views.AccountViewSet, basename='account')
router.register(r'expenses', api_views.ExpenseViewSet, basename='expense')
router.register(r'incomes', api_views.IncomeViewSet, basename='income')

# API URL patterns
urlpatterns = [
    # Router URLs for ViewSets
    path('', include(router.urls)),
    
    # Additional API endpoints
    path('reports/financial/', api_views.FinancialReportAPIView.as_view(), name='api_financial_report'),
    path('ai/insights/', api_views.AIInsightsAPIView.as_view(), name='api_ai_insights'),
    
    # API root
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
