#!/usr/bin/env python
"""
Comprehensive test runner for the EDA & Preprocessing Django Application
Runs all tests and generates a detailed test report
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner
from django.core.management import execute_from_command_line


def setup_django():
    """Setup Django environment for testing"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eda_project.settings')
    django.setup()


def run_all_tests():
    """Run all tests and display results"""
    print("=" * 80)
    print("EDA & PREPROCESSING DJANGO APPLICATION - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print()
    
    # Test modules to run
    test_modules = [
        'home.tests',           # Home app tests
        'eda.tests',            # EDA app tests
        'preprocessing.tests',  # Preprocessing app tests
        'feedback.tests'        # Feedback app tests
    ]
    
    print("Running tests for the following modules:")
    for module in test_modules:
        print(f"  ✓ {module}")
    print()
    
    # Run tests with verbose output
    test_command = [
        'manage.py',
        'test',
        '--verbosity=2',
        '--keepdb',  # Keep test database for faster subsequent runs
        '--parallel', 'auto'  # Run tests in parallel
    ] + test_modules
    
    try:
        execute_from_command_line(test_command)
        print()
        print("=" * 80)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 80)
        
    except SystemExit as e:
        if e.code == 0:
            print()
            print("=" * 80)
            print("✅ ALL TESTS PASSED SUCCESSFULLY!")
            print("=" * 80)
        else:
            print()
            print("=" * 80) 
            print("❌ SOME TESTS FAILED")
            print("=" * 80)
            sys.exit(e.code)


def run_specific_tests():
    """Run tests for specific modules based on command line arguments"""
    if len(sys.argv) < 2:
        print("Usage: python run_tests.py [all|home|eda|preprocessing|feedback]")
        return
    
    target = sys.argv[1].lower()
    
    test_map = {
        'all': ['home.tests', 'eda.tests', 'preprocessing.tests', 'feedback.tests'],
        'home': ['home.tests'],
        'eda': ['eda.tests'],
        'preprocessing': ['preprocessing.tests'],
        'feedback': ['feedback.tests']
    }
    
    if target not in test_map:
        print(f"Invalid target: {target}")
        print("Valid targets: all, home, eda, preprocessing, feedback")
        return
    
    modules = test_map[target]
    
    print(f"Running tests for: {target.upper()}")
    print("Modules:", ', '.join(modules))
    print()
    
    test_command = [
        'manage.py',
        'test',
        '--verbosity=2',
        '--keepdb'
    ] + modules
    
    execute_from_command_line(test_command)


def main():
    """Main function"""
    setup_django()
    
    if len(sys.argv) > 1:
        run_specific_tests()
    else:
        run_all_tests()


if __name__ == '__main__':
    main()