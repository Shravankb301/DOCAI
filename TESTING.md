# Testing Guide

This document provides instructions for running tests in the DocAI project.

## Backend Tests

The backend tests are written using pytest and are organized into unit and integration tests.

### Running Backend Tests

To run all backend tests:

```bash
cd backend
pytest
```

To run only unit tests:

```bash
cd backend
pytest tests/unit
```

To run only integration tests:

```bash
cd backend
pytest tests/integration
```

To run tests with coverage:

```bash
cd backend
pytest --cov=app
```

## Frontend Tests

The frontend tests are written using Jest for unit/component tests and Playwright for E2E tests.

### Running Frontend Unit Tests

To run all frontend unit tests:

```bash
cd frontend
npm test
```

To run tests in watch mode:

```bash
cd frontend
npm run test:watch
```

### Running Frontend E2E Tests

To run E2E tests:

```bash
cd frontend
npm run test:e2e
```

To run E2E tests in a specific browser:

```bash
cd frontend
npx playwright test --project=chromium
```

## Continuous Integration

This project uses GitHub Actions for continuous integration. The workflow is defined in `.github/workflows/continuous-testing.yml`.

The CI pipeline runs:
1. Backend unit and integration tests
2. Frontend unit tests
3. End-to-end tests

## Using the Test Script

For convenience, a test script is provided to run all tests in one command:

```bash
./run_tests.sh
```

By default, this will run backend and frontend tests, but skip E2E tests.

### Options

- `-b, --backend`: Run only backend tests
- `-f, --frontend`: Run only frontend tests
- `-e, --e2e`: Run only end-to-end tests
- `-a, --all`: Run all tests (including E2E)
- `-c, --coverage`: Generate coverage reports

Example:
```bash
./run_tests.sh --backend --coverage
```

## Known Issues and Workarounds

### Backend Tests

- The backend tests require Python 3.x. If you have multiple Python versions installed, make sure to use Python 3.
- For integration tests, the TestClient requires httpx version 0.24.0 to work correctly with the current FastAPI version.

### Frontend Tests

- The frontend tests use Jest for unit tests and Playwright for E2E tests.
- E2E tests require a running backend and frontend server.
- If you encounter ESLint errors during the build, you can use the `.eslintrc.json` file to disable specific rules.

### E2E Tests

- E2E tests are currently skipped by default due to environment setup complexity.
- To run E2E tests, use the `--e2e` flag with the run_tests.sh script.
- Make sure Playwright is installed: `npx playwright install`

## Adding New Tests

### Backend

1. Unit tests should be added to `backend/tests/unit/`
2. Integration tests should be added to `backend/tests/integration/`
3. Test data should be added to `backend/tests/data/`

### Frontend

1. Component tests should be added alongside the component with a `.test.tsx` extension
2. E2E tests should be added to `frontend/e2e/` with a `.spec.ts` extension

## Best Practices

1. Write tests before implementing features (TDD)
2. Ensure tests are isolated and don't depend on each other
3. Mock external dependencies
4. Keep tests fast and focused
5. Aim for high test coverage, especially for critical paths 