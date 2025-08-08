#!/usr/bin/env python3
"""
Simple CLI Test Result Submission Utility for PromptEvolver
Submits test execution data to Convex backend via HTTP API
"""

import os
import platform
import subprocess
import sys
import time
import uuid
from typing import Any, Dict, List, Optional

import requests


class TestLogger:
    """Simple test result logger for Convex backend"""

    def __init__(self, convex_url: str = "https://your-convex-deployment.convex.cloud"):
        self.convex_url = convex_url.rstrip("/")
        self.execution_id = f"test_{int(time.time())}_{str(uuid.uuid4())[:8]}"
        self.start_time = time.time() * 1000  # milliseconds

    def get_system_metadata(self) -> Dict[str, str]:
        """Collect system metadata for test execution"""
        try:
            python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

            # Try to get pytest version
            pytest_version = "unknown"
            try:
                result = subprocess.run(["pytest", "--version"], capture_output=True, text=True)
                if result.returncode == 0:
                    pytest_version = result.stdout.strip().split("\n")[0].split()[-1]
            except (subprocess.SubprocessError, IndexError):
                pass

            return {
                "pythonVersion": python_version,
                "pytestVersion": pytest_version,
                "platform": platform.platform(),
                "branch": os.environ.get("GIT_BRANCH", "unknown"),
                "commit": os.environ.get("GIT_COMMIT", "unknown"),
            }
        except Exception as e:
            print(f"Warning: Could not collect system metadata: {e}")
            return {}

    def create_test_result(
        self,
        test_name: str,
        test_module: str,
        status: str,
        duration: float,
        error_message: Optional[str] = None,
        error_trace: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Create a test result object"""
        return {
            "testId": f"{test_module}::{test_name}",
            "testName": test_name,
            "testModule": test_module,
            "status": status,  # passed, failed, skipped, timeout
            "duration": duration,
            "errorMessage": error_message,
            "errorTrace": error_trace,
            "metadata": metadata or {},
        }

    def create_api_call_log(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        response_time: float,
        success: bool,
        error_message: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Create an API call log object"""
        return {
            "callId": f"api_{int(time.time() * 1000)}_{str(uuid.uuid4())[:8]}",
            "endpoint": endpoint,
            "method": method,
            "statusCode": status_code,
            "responseTime": response_time,
            "success": success,
            "errorMessage": error_message,
            "metadata": metadata or {},
        }

    def create_error_log(
        self,
        error_type: str,
        error_message: str,
        severity: str = "medium",
        error_trace: Optional[str] = None,
        context: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Create an error log object"""
        return {
            "errorId": f"error_{int(time.time() * 1000)}_{str(uuid.uuid4())[:8]}",
            "errorType": error_type,
            "errorMessage": error_message,
            "errorTrace": error_trace,
            "severity": severity,  # low, medium, high, critical
            "context": context or {},
        }

    def submit_test_execution(
        self,
        test_type: str = "cli",
        test_suite: str = "prompt-wizard-cli",
        environment: str = "development",
        test_results: List[Dict] = None,
        api_calls: List[Dict] = None,
        errors: List[Dict] = None,
    ) -> bool:
        """Submit test execution data to Convex backend"""

        payload = {
            "executionId": self.execution_id,
            "testType": test_type,
            "testSuite": test_suite,
            "environment": environment,
            "testResults": test_results or [],
            "apiCalls": api_calls or [],
            "errors": errors or [],
            "metadata": self.get_system_metadata(),
        }

        print(f"📊 Submitting test execution {self.execution_id} to {self.convex_url}/log-test")
        print(f"   Test Results: {len(payload['testResults'])}")
        print(f"   API Calls: {len(payload['apiCalls'])}")
        print(f"   Errors: {len(payload['errors'])}")

        try:
            response = requests.post(
                f"{self.convex_url}/log-test",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30,
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    print(f"✅ Successfully logged test execution")
                    print(f"   Execution ID: {result['data']['testExecutionId']}")
                    return True
                else:
                    print(f"❌ Failed to log test execution: {result.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"❌ HTTP {response.status_code}: {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ Network error submitting test results: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error submitting test results: {e}")
            return False

    def update_test_status(self, status: str, results: Optional[Dict] = None) -> bool:
        """Update test execution status"""

        payload = {
            "executionId": self.execution_id,
            "status": status,
            "endTime": int(time.time() * 1000),
            "duration": int(time.time() * 1000) - int(self.start_time),
            "results": results,
        }

        try:
            response = requests.put(
                f"{self.convex_url}/test-status",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    print(f"✅ Updated test status to: {status}")
                    return True

            print(f"⚠️  Failed to update test status: {response.text}")
            return False

        except Exception as e:
            print(f"⚠️  Error updating test status: {e}")
            return False


def run_example_test_session():
    """Example usage of TestLogger with sample test data"""

    # Use local Convex development URL
    logger = TestLogger("http://localhost:3000")

    print("🧪 Running Example Test Session")
    print(f"Execution ID: {logger.execution_id}")

    # Sample test results
    test_results = [
        logger.create_test_result(
            test_name="test_prompt_optimization",
            test_module="test_api_integration",
            status="passed",
            duration=2450.5,
            metadata={
                "promptText": "Test prompt for optimization",
                "promptLength": 28,
                "responseLength": 145,
                "modelUsed": "Microsoft PromptWizard + Qwen3:4b",
            },
        ),
        logger.create_test_result(
            test_name="test_health_check",
            test_module="test_api_integration",
            status="passed",
            duration=156.2,
        ),
        logger.create_test_result(
            test_name="test_invalid_prompt",
            test_module="test_api_integration",
            status="failed",
            duration=89.3,
            error_message="Timeout waiting for API response",
            error_trace="requests.exceptions.Timeout: HTTPSConnectionPool timeout",
        ),
    ]

    # Sample API calls
    api_calls = [
        logger.create_api_call_log(
            endpoint="/health",
            method="GET",
            status_code=200,
            response_time=156.2,
            success=True,
            metadata={"modelUsed": "Microsoft PromptWizard + Qwen3:4b"},
        ),
        logger.create_api_call_log(
            endpoint="/optimize",
            method="POST",
            status_code=200,
            response_time=2450.5,
            success=True,
            metadata={
                "modelUsed": "Microsoft PromptWizard + Qwen3:4b",
                "promptTokens": 7,
                "completionTokens": 36,
                "totalTokens": 43,
            },
        ),
        logger.create_api_call_log(
            endpoint="/optimize",
            method="POST",
            status_code=500,
            response_time=8000.0,
            success=False,
            error_message="Timeout waiting for API response",
        ),
    ]

    # Sample errors
    errors = [
        logger.create_error_log(
            error_type="TimeoutError",
            error_message="API request timed out after 8 seconds",
            severity="high",
            context={
                "function": "test_invalid_prompt",
                "file": "test_api_integration.py",
                "line": 45,
            },
        ),
    ]

    # Submit test execution
    success = logger.submit_test_execution(
        test_type="api",
        test_suite="prompt-wizard-integration-tests",
        environment="development",
        test_results=test_results,
        api_calls=api_calls,
        errors=errors,
    )

    if success:
        # Update final status
        final_results = {
            "totalTests": len(test_results),
            "passedTests": len([t for t in test_results if t["status"] == "passed"]),
            "failedTests": len([t for t in test_results if t["status"] == "failed"]),
            "skippedTests": len([t for t in test_results if t["status"] == "skipped"]),
            "coverage": 85.5,
        }

        logger.update_test_status("failed", final_results)  # Failed due to timeout

        print("\n📈 Test Execution Summary:")
        print(f"   Total Tests: {final_results['totalTests']}")
        print(f"   Passed: {final_results['passedTests']}")
        print(f"   Failed: {final_results['failedTests']}")
        print(f"   API Calls: {len(api_calls)}")
        print(f"   Errors: {len(errors)}")

        return True
    else:
        return False


if __name__ == "__main__":
    # Run example test session
    success = run_example_test_session()
    sys.exit(0 if success else 1)
