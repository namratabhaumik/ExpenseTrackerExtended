#!/usr/bin/env python
"""
Verification script to test that the SystemExit errors are resolved.
"""

import os
import sys
import subprocess


def run_test_command():
    """Run a simple test command to verify the fix."""
    try:
        # Change to the correct directory
        os.chdir('expense-tracker-backend/expense_tracker')

        # Run a simple test to check if SystemExit errors are resolved
        result = subprocess.run([
            sys.executable, '-m', 'pytest',
            'auth_app/tests.py::LoginViewTest::test_login_success',
            '-v', '--tb=short'
        ], capture_output=True, text=True, timeout=30)

        print("Test Output:")
        print(result.stdout)

        if result.stderr:
            print("Error Output:")
            print(result.stderr)

        if result.returncode == 0:
            print("✓ Test passed! SystemExit errors are resolved.")
            return True
        else:
            print(f"✗ Test failed with return code: {result.returncode}")
            return False

    except subprocess.TimeoutExpired:
        print("✗ Test timed out")
        return False
    except Exception as e:
        print(f"✗ Error running test: {e}")
        return False


if __name__ == '__main__':
    success = run_test_command()
    sys.exit(0 if success else 1)
