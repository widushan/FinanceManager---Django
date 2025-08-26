# Performance Test Report

Generated: 2025-08-26 17:00:29

## Page Load Performance

- **home**: 5.00ms PASS
- **expenses**: 28.25ms PASS
- **incomes**: 30.98ms PASS
- **report**: 58.64ms PASS
- **ai_insights**: 14.61ms PASS

## API Response Performance

- **/api/v1/accounts/**: 7.69ms PASS (HTTP 200) (401 expected for unauthenticated requests)
- **/api/v1/expenses/**: 7.10ms PASS (HTTP 200) (401 expected for unauthenticated requests)
- **/api/v1/incomes/**: 13.60ms PASS (HTTP 200) (401 expected for unauthenticated requests)
- **/api/v1/reports/financial/**: 7.65ms PASS (HTTP 404) (401 expected for unauthenticated requests)
- **/api/v1/ai/insights/**: 7.52ms PASS (HTTP 404) (401 expected for unauthenticated requests)
