# Test Logging System Usage Guide

## Overview

The test logging system captures test execution data, API performance metrics, and error logs in the Convex backend database. This helps bypass timeout issues by storing test results instead of relying on long-running pytest sessions.

## Components

### 1. Database Schema (Convex)
- **testExecutions** - Test run metadata and summaries
- **testResults** - Individual test results with detailed metrics
- **apiCalls** - API performance data with response times
- **errorLogs** - Detailed error information and context

### 2. HTTP Endpoints
- `POST /log-test` - Submit test execution data from CLI
- `GET /test-results` - Retrieve test execution history
- `GET /api-metrics` - Get API performance data
- `PUT /test-status` - Update test execution status

### 3. CLI Utilities
- **test_logger.py** - Core logging functionality and example usage
- **run_tests_with_logging.py** - Enhanced test runner with Convex integration

## Quick Start

### 1. Run Example Test Session
```bash
cd /home/matt/prompt-wizard/cli
python test_logger.py
```

This will submit sample test data to demonstrate the logging system.

### 2. Run Tests with Logging
```bash
# Run pytest with automatic logging
python run_tests_with_logging.py

# Run simple CLI tests with logging
python run_tests_with_logging.py cli
```

### 3. Install Dependencies
```bash
pip install requests
```

## API Usage Examples

### Submit Test Results via HTTP
```bash
curl -X POST http://localhost:3000/log-test \
  -H "Content-Type: application/json" \
  -d '{
    "executionId": "test_123456789",
    "testType": "api",
    "testSuite": "prompt-wizard-integration",
    "environment": "development",
    "testResults": [
      {
        "testId": "test_api::test_health",
        "testName": "test_health",
        "testModule": "test_api",
        "status": "passed",
        "duration": 150.5
      }
    ],
    "apiCalls": [],
    "errors": [],
    "metadata": {
      "pythonVersion": "3.9.0",
      "platform": "Linux"
    }
  }'
```

### Get Test Results
```bash
# Get recent test executions
curl "http://localhost:3000/test-results?limit=10"

# Get specific execution
curl "http://localhost:3000/test-results?executionId=test_123456789"

# Filter by test type
curl "http://localhost:3000/test-results?testType=api&limit=20"
```

### Get API Metrics
```bash
# Get last 24 hours of API metrics
curl "http://localhost:3000/api-metrics"

# Get metrics for specific endpoint
curl "http://localhost:3000/api-metrics?endpoint=/optimize&hours=12"
```

## Configuration

### Convex URL Configuration
The default configuration uses `http://localhost:3000` for local development. For deployed Convex, update the URL:

```python
logger = TestLogger("https://your-convex-deployment.convex.cloud")
```

### Environment Variables
Set these environment variables for enhanced metadata:
- `GIT_BRANCH` - Current git branch
- `GIT_COMMIT` - Current git commit hash

## Data Structure

### Test Result Object
```python
{
    "testId": "module::test_name",
    "testName": "test_name",
    "testModule": "module",
    "status": "passed|failed|skipped|timeout",
    "duration": 150.5,  # milliseconds
    "errorMessage": "Optional error message",
    "errorTrace": "Optional stack trace",
    "metadata": {
        "promptText": "Optional test prompt",
        "modelUsed": "Microsoft PromptWizard + Qwen3:4b"
    }
}
```

### API Call Log Object
```python
{
    "callId": "unique_call_id",
    "endpoint": "/optimize",
    "method": "POST",
    "statusCode": 200,
    "responseTime": 2450.5,  # milliseconds
    "success": True,
    "metadata": {
        "modelUsed": "Microsoft PromptWizard + Qwen3:4b",
        "promptTokens": 7,
        "completionTokens": 36,
        "totalTokens": 43
    }
}
```

### Error Log Object
```python
{
    "errorId": "unique_error_id",
    "errorType": "TimeoutError",
    "errorMessage": "Request timed out after 8 seconds",
    "severity": "high|medium|low|critical",
    "context": {
        "function": "test_function",
        "file": "test_file.py",
        "line": 45
    }
}
```

## Benefits

1. **Persistent Storage** - Test results stored in database, not lost on timeout
2. **Performance Metrics** - Track API response times and identify bottlenecks
3. **Error Analysis** - Detailed error logging with context and severity
4. **Historical Data** - Track performance trends over time
5. **Real-time Monitoring** - Query test results and metrics via HTTP API

## Integration with Existing Tests

The system integrates with:
- **pytest** - Automatic JSON output parsing
- **CLI tests** - Direct integration with existing test_cli.py
- **API tests** - Captures real API call performance
- **Custom tests** - Easy integration with TestLogger class

## Troubleshooting

1. **Connection Errors** - Ensure Convex backend is running on correct URL
2. **Timeout Issues** - Increase timeout values in requests
3. **JSON Parsing** - Check pytest-json-report plugin installation
4. **Permission Errors** - Ensure scripts are executable (`chmod +x`)

## Next Steps

1. Add automatic integration to CI/CD pipelines
2. Create dashboard for visualizing test metrics
3. Add email/Slack notifications for test failures
4. Implement test result comparison and regression detection
