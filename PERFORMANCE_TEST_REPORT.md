# Performance Test Report

Generated: 2025-08-27 17:47:26

## Page Load Performance

- **home**: 2.01ms PASS
- **expenses**: 53.62ms PASS
- **incomes**: 17.87ms PASS
- **report**: 25.17ms PASS
- **ai_insights**: 11.30ms PASS

## API Response Performance

- **/api/v1/accounts/**: 1.87ms PASS (HTTP 200) (401 expected for unauthenticated requests)
- **/api/v1/expenses/**: 8.02ms PASS (HTTP 200) (401 expected for unauthenticated requests)
- **/api/v1/incomes/**: 5.60ms PASS (HTTP 200) (401 expected for unauthenticated requests)
- **/api/v1/reports/financial/**: 0.00ms PASS (HTTP 404) (401 expected for unauthenticated requests)
- **/api/v1/ai/insights/**: 8.14ms PASS (HTTP 404) (401 expected for unauthenticated requests)
