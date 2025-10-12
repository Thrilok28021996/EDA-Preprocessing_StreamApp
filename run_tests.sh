#!/bin/bash

# Script to run tests with coverage reporting for Django EDA Application

echo "======================================"
echo "Running Django EDA Application Tests"
echo "======================================"
echo ""

# Run tests with coverage
pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing --cov-report=xml

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "======================================"
    echo "✓ All tests passed!"
    echo "======================================"
    echo ""
    echo "Coverage report generated:"
    echo "  - HTML: htmlcov/index.html"
    echo "  - XML:  coverage.xml"
    echo ""
    echo "To view HTML coverage report:"
    echo "  open htmlcov/index.html"
else
    echo ""
    echo "======================================"
    echo "✗ Some tests failed"
    echo "======================================"
    exit 1
fi
