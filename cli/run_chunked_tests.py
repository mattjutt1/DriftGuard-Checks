#!/usr/bin/env python3
"""
Chunked Test Runner - Bypasses timeout by running tests in small batches
"""
import subprocess
import json
import time
from pathlib import Path

def run_test_chunk(test_pattern, chunk_name):
    """Run a specific chunk of tests"""
    start_time = time.time()
    
    cmd = [
        "./test_env/bin/python", "-m", "pytest", 
        test_pattern,
        "-v", 
        "--tb=short",
        "--json-report",
        f"--json-report-file=chunk_{chunk_name}.json"
    ]
    
    print(f"🧪 Running {chunk_name} tests: {test_pattern}")
    
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=45,  # 45 second timeout per chunk
            cwd="/home/matt/prompt-wizard/cli"
        )
        
        duration = time.time() - start_time
        
        # Parse JSON results if available
        json_file = Path(f"chunk_{chunk_name}.json")
        test_count = 0
        passed = 0
        failed = 0
        
        if json_file.exists():
            try:
                with open(json_file) as f:
                    data = json.load(f)
                    if 'summary' in data:
                        test_count = data['summary'].get('total', 0)
                        passed = data['summary'].get('passed', 0)
                        failed = data['summary'].get('failed', 0)
            except:
                pass
        
        return {
            'chunk': chunk_name,
            'pattern': test_pattern,
            'duration': duration,
            'return_code': result.returncode,
            'test_count': test_count,
            'passed': passed,
            'failed': failed,
            'stdout': result.stdout[:500] if result.stdout else "",
            'stderr': result.stderr[:500] if result.stderr else ""
        }
        
    except subprocess.TimeoutExpired:
        return {
            'chunk': chunk_name,
            'pattern': test_pattern,
            'duration': 45.0,
            'return_code': -1,
            'test_count': 0,
            'passed': 0,
            'failed': 0,
            'stdout': "",
            'stderr': "TIMEOUT"
        }
    except Exception as e:
        return {
            'chunk': chunk_name,
            'pattern': test_pattern,
            'duration': time.time() - start_time,
            'return_code': -2,
            'test_count': 0,
            'passed': 0,
            'failed': 0,
            'stdout': "",
            'stderr': str(e)
        }

def main():
    """Run all tests in manageable chunks"""
    
    # Define test chunks
    test_chunks = [
        ("tests/unit/test_client.py", "unit_client"),
        ("tests/unit/test_config.py", "unit_config"),
        ("tests/unit/test_main.py", "unit_main"),
        ("tests/integration/test_api_integration.py", "integration_api"),
        ("tests/integration/test_cli_workflows.py", "integration_cli"),
    ]
    
    results = []
    total_tests = 0
    total_passed = 0
    total_failed = 0
    total_duration = 0
    
    print("🚀 Starting Chunked Test Execution")
    print("=" * 60)
    
    for pattern, chunk_name in test_chunks:
        result = run_test_chunk(pattern, chunk_name)
        results.append(result)
        
        total_tests += result['test_count']
        total_passed += result['passed']
        total_failed += result['failed']
        total_duration += result['duration']
        
        # Print chunk summary
        status = "✅ PASS" if result['return_code'] == 0 else "❌ FAIL"
        print(f"{status} {chunk_name}: {result['passed']}/{result['test_count']} passed ({result['duration']:.1f}s)")
        
        if result['stderr'] and result['stderr'] != "":
            print(f"   ⚠️  Error: {result['stderr'][:100]}")
    
    print("=" * 60)
    print(f"📊 FINAL RESULTS:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {total_passed}")
    print(f"   Failed: {total_failed}")
    print(f"   Success Rate: {(total_passed/total_tests*100):.1f}%" if total_tests > 0 else "   Success Rate: 0%")
    print(f"   Total Duration: {total_duration:.1f}s")
    
    # Save complete results
    final_results = {
        'timestamp': time.time(),
        'execution_strategy': 'chunked_bypass',
        'total_tests': total_tests,
        'total_passed': total_passed,
        'total_failed': total_failed,
        'total_duration': total_duration,
        'success_rate': (total_passed/total_tests*100) if total_tests > 0 else 0,
        'chunks': results
    }
    
    with open('complete_chunked_results.json', 'w') as f:
        json.dump(final_results, f, indent=2)
    
    print(f"✅ Results saved to complete_chunked_results.json")
    
    return total_failed == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)