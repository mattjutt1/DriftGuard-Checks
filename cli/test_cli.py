#!/usr/bin/env python3
"""
Simple test script to verify CLI installation and basic functionality
"""

import subprocess
import sys


def test_installation():
    """Test if the CLI is properly installed"""
    try:
        result = subprocess.run(["promptevolver", "--version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ CLI installation successful")
            print(f"   Version: {result.stdout.strip()}")
            return True
        else:
            print("❌ CLI installation failed")
            print(f"   Error: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ CLI not found - installation may have failed")
        return False
    except subprocess.TimeoutExpired:
        print("❌ CLI command timed out")
        return False


def test_help():
    """Test if help commands work"""
    try:
        result = subprocess.run(["promptevolver", "--help"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and "PromptEvolver CLI" in result.stdout:
            print("✅ Help command works")
            return True
        else:
            print("❌ Help command failed")
            return False
    except Exception as e:
        print(f"❌ Help command error: {e}")
        return False


def test_health_command():
    """Test the health command (without actually calling the API)"""
    try:
        # Test that the command exists and shows help
        result = subprocess.run(["promptevolver", "health", "--help"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and "Check Ollama health" in result.stdout:
            print("✅ Health command available")
            return True
        else:
            print("❌ Health command not available")
            return False
    except Exception as e:
        print(f"❌ Health command error: {e}")
        return False


def main():
    print("🔍 Testing PromptEvolver CLI Installation...")
    print()

    tests = [
        ("Installation", test_installation),
        ("Help Command", test_help),
        ("Health Command", test_health_command),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"Testing {test_name}...")
        if test_func():
            passed += 1
        print()

    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! CLI is ready to use.")
        print()
        print("Try these commands:")
        print("  promptevolver --help")
        print("  promptevolver health")
        print("  promptevolver optimize 'test prompt'")
    else:
        print("⚠️  Some tests failed. Check the installation.")
        sys.exit(1)


if __name__ == "__main__":
    main()
