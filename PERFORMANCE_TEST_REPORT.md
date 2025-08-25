# Performance Test Report

Generated: 2025-08-26 00:27:05

## Page Load Performance

- **home**: 4.53ms PASS
- **expenses**: 38.56ms PASS
- **incomes**: 42.77ms PASS
- **report**: 31.58ms PASS
- **ai_insights**: 6.89ms PASS

## API Response Performance

- **/api/v1/accounts/**: 8.52ms PASS (HTTP 200) (401 expected for unauthenticated requests)
- **/api/v1/expenses/**: 6.01ms PASS (HTTP 200) (401 expected for unauthenticated requests)
- **/api/v1/incomes/**: 7.51ms PASS (HTTP 200) (401 expected for unauthenticated requests)
- **/api/v1/reports/financial/**: 7.53ms PASS (HTTP 404) (401 expected for unauthenticated requests)
- **/api/v1/ai/insights/**: 4.01ms PASS (HTTP 404) (401 expected for unauthenticated requests)
