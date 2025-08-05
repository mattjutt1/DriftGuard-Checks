#!/usr/bin/env python3
"""
Enhanced Test Runner with Convex Logging Integration
Runs existing tests and submits results to Convex backend
"""

import subprocess
import json
import time
import sys
import os
from test_logger import TestLogger


def run_pytest_with_logging():
    """Run pytest and capture results for logging"""
    
    # Initialize test logger
    logger = TestLogger("http://localhost:3000")  # Use local development URL
    
    print("🧪 Running pytest with Convex logging integration...")
    print(f"Execution ID: {logger.execution_id}")
    
    test_results = []
    api_calls = []
    errors = []
    
    try:
        # Run pytest with JSON output
        pytest_cmd = [
            'python', '-m', 'pytest', 
            'tests/', 
            '-v',
            '--tb=short',
            '--json-report',
            '--json-report-file=test_results.json'
        ]
        
        print(f"Running: {' '.join(pytest_cmd)}")
        start_time = time.time()
        
        result = subprocess.run(
            pytest_cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        duration = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        print(f"\n📊 Test execution completed in {duration/1000:.2f}s")
        print(f"Return code: {result.returncode}")
        
        # Parse pytest JSON output if available
        if os.path.exists('test_results.json'):
            try:
                with open('test_results.json', 'r') as f:
                    pytest_data = json.load(f)
                
                # Convert pytest results to our format
                for test in pytest_data.get('tests', []):
                    test_result = logger.create_test_result(
                        test_name=test.get('nodeid', 'unknown').split("::")[-1],
                        test_module=test.get('nodeid', 'unknown').split("::")[0],
                        status=test.get('outcome', 'unknown'),
                        duration=test.get('duration', 0) * 1000,  # Convert to ms
                        error_message=test.get('call', {}).get('longrepr') if test.get('outcome') == 'failed' else None,
                    )
                    test_results.append(test_result)
            except Exception as e:
                print(f"⚠️  Could not parse pytest JSON output: {e}")
        
        # If no JSON output, parse text output
        if not test_results:
            test_results = parse_pytest_text_output(result.stdout, logger)
        
        # Create summary API call log
        api_calls.append(logger.create_api_call_log(
            endpoint="/pytest-run",
            method="POST",
            status_code=200 if result.returncode == 0 else 500,
            response_time=duration,
            success=result.returncode == 0,
            error_message=result.stderr[:500] if result.stderr else None,
            metadata={
                "testCommand": " ".join(pytest_cmd),
                "totalTests": len(test_results),
            }
        ))
        
        # Log errors if any
        if result.returncode != 0:
            errors.append(logger.create_error_log(
                error_type="TestExecutionError",
                error_message=f"pytest failed with return code {result.returncode}",
                severity="high" if result.returncode != 0 else "low",
                error_trace=result.stderr[:1000] if result.stderr else None,
                context={
                    "function": "run_pytest_with_logging",
                    "file": "run_tests_with_logging.py",
                    "command": " ".join(pytest_cmd),
                }
            ))
        
        # Submit to Convex
        success = logger.submit_test_execution(
            test_type="integration",
            test_suite="prompt-wizard-pytest",
            environment="development",
            test_results=test_results,
            api_calls=api_calls,
            errors=errors,
        )
        
        if success:
            # Update final status
            passed_count = len([t for t in test_results if t["status"] == "passed"])
            failed_count = len([t for t in test_results if t["status"] == "failed"])
            skipped_count = len([t for t in test_results if t["status"] == "skipped"])
            
            final_results = {
                "totalTests": len(test_results),
                "passedTests": passed_count,
                "failedTests": failed_count,
                "skippedTests": skipped_count,
                "coverage": 0,  # Could integrate with coverage.py if needed
            }
            
            final_status = "passed" if result.returncode == 0 else "failed"
            logger.update_test_status(final_status, final_results)
            
            print(f"\n✅ Test results logged to Convex backend")
            print(f"   Status: {final_status}")
            print(f"   Tests: {passed_count} passed, {failed_count} failed, {skipped_count} skipped")
        else:
            print(f"\n⚠️  Failed to log test results to Convex backend")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        error = logger.create_error_log(
            error_type="TimeoutError",
            error_message="Test execution timed out after 5 minutes",
            severity="critical",
        )
        
        logger.submit_test_execution(
            test_type="integration",
            test_suite="prompt-wizard-pytest",
            environment="development",
            test_results=[],
            api_calls=[],
            errors=[error],
        )
        
        logger.update_test_status("timeout")
        print("❌ Test execution timed out")
        
        return False
        
    except Exception as e:
        error = logger.create_error_log(
            error_type="ExecutionError",
            error_message=str(e),
            severity="critical",
            context={"function": "run_pytest_with_logging"}
        )
        
        logger.submit_test_execution(
            test_type="integration", 
            test_suite="prompt-wizard-pytest",
            environment="development",
            test_results=[],
            api_calls=[],
            errors=[error],
        )
        
        logger.update_test_status("failed")
        print(f"❌ Test execution failed: {e}")
        
        return False


def parse_pytest_text_output(output: str, logger: TestLogger) -> list:
    """Parse pytest text output to extract test results"""
    test_results = []
    
    lines = output.split('\n')
    for line in lines:
        line = line.strip()
        
        # Look for test result lines like:
        # tests/test_client.py::test_config_loading PASSED
        # tests/test_client.py::test_invalid_config FAILED
        if '::' in line and any(status in line for status in ['PASSED', 'FAILED', 'SKIPPED']):
            parts = line.split()
            if len(parts) >= 2:
                test_path = parts[0]
                status = parts[1].lower()
                
                if '::' in test_path:
                    module, test_name = test_path.split('::', 1)
                    
                    test_result = logger.create_test_result(
                        test_name=test_name,
                        test_module=module,
                        status=status,
                        duration=0,  # Duration not available in text output
                    )
                    test_results.append(test_result)
    
    return test_results


def run_simple_cli_tests():
    """Run the simple CLI tests with logging"""
    
    logger = TestLogger("http://localhost:3000")
    
    print("🧪 Running simple CLI tests with logging...")
    
    # Import and run existing CLI tests
    try:
        from test_cli import test_installation, test_help, test_health_command
        
        test_results = []
        
        # Test installation
        start_time = time.time()
        success = test_installation()
        duration = (time.time() - start_time) * 1000
        
        test_results.append(logger.create_test_result(
            test_name="test_installation",
            test_module="test_cli",
            status="passed" if success else "failed",
            duration=duration,
        ))
        
        # Test help
        start_time = time.time()
        success = test_help()
        duration = (time.time() - start_time) * 1000
        
        test_results.append(logger.create_test_result(
            test_name="test_help",
            test_module="test_cli",
            status="passed" if success else "failed",
            duration=duration,
        ))
        
        # Test health command
        start_time = time.time()
        success = test_health_command()
        duration = (time.time() - start_time) * 1000
        
        test_results.append(logger.create_test_result(
            test_name="test_health_command",
            test_module="test_cli",
            status="passed" if success else "failed",
            duration=duration,
        ))
        
        # Submit results
        logger.submit_test_execution(
            test_type="cli",
            test_suite="prompt-wizard-cli-tests",
            environment="development",
            test_results=test_results,
        )
        
        passed_count = len([t for t in test_results if t["status"] == "passed"])
        failed_count = len([t for t in test_results if t["status"] == "failed"])
        
        final_status = "passed" if failed_count == 0 else "failed"
        
        logger.update_test_status(final_status, {
            "totalTests": len(test_results),
            "passedTests": passed_count,
            "failedTests": failed_count,
            "skippedTests": 0,
        })
        
        print(f"✅ CLI tests completed: {passed_count} passed, {failed_count} failed")
        return failed_count == 0
        
    except Exception as e:
        print(f"❌ Error running CLI tests: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        success = run_simple_cli_tests()
    else:
        success = run_pytest_with_logging()
    
    sys.exit(0 if success else 1)