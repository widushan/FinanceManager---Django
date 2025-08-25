# Performance Test Report

Generated: 2025-08-25 18:37:11

## Page Load Performance

- **home**: 3.47ms PASS
- **expenses**: 14.95ms PASS
- **incomes**: 23.17ms PASS
- **report**: 40.68ms PASS
- **ai_insights**: 6.79ms PASS

## API Response Performance

- **/api/v1/accounts/**: 5.16ms PASS (HTTP 200) (401 expected for unauthenticated requests)
- **/api/v1/expenses/**: 3.53ms PASS (HTTP 200) (401 expected for unauthenticated requests)
- **/api/v1/incomes/**: 6.05ms PASS (HTTP 200) (401 expected for unauthenticated requests)
- **/api/v1/reports/financial/**: 6.53ms PASS (HTTP 404) (401 expected for unauthenticated requests)
- **/api/v1/ai/insights/**: 12.27ms PASS (HTTP 404) (401 expected for unauthenticated requests)
