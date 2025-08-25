# Performance Test Report

Generated: 2025-08-25 13:09:51

## Page Load Performance

- **home**: 2.20ms PASS
- **expenses**: 15.06ms PASS
- **incomes**: 20.50ms PASS
- **report**: 31.74ms PASS
- **ai_insights**: 5.89ms PASS

## API Response Performance

- **/api/v1/accounts/**: 10.61ms PASS (HTTP 200) (401 expected for unauthenticated requests)
- **/api/v1/expenses/**: 8.40ms PASS (HTTP 200) (401 expected for unauthenticated requests)
- **/api/v1/incomes/**: 6.78ms PASS (HTTP 200) (401 expected for unauthenticated requests)
- **/api/v1/reports/financial/**: 4.02ms PASS (HTTP 404) (401 expected for unauthenticated requests)
- **/api/v1/ai/insights/**: 3.80ms PASS (HTTP 404) (401 expected for unauthenticated requests)
