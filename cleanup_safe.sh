#!/bin/bash
# cleanup_safe.sh - Remove definitely unused files
# This script removes files that are safe to delete without breaking functionality

set -e  # Exit on error

echo "==========================================="
echo "Safe Cleanup Script for EDA Django App"
echo "==========================================="
echo ""

# Function to safely remove files
safe_remove() {
    local file=$1
    if [ -f "$file" ]; then
        echo "  Removing: $file"
        rm -f "$file"
    else
        echo "  Already removed: $file"
    fi
}

# Function to safely remove directories
safe_remove_dir() {
    local dir=$1
    if [ -d "$dir" ]; then
        echo "  Removing directory: $dir"
        rm -rf "$dir"
    else
        echo "  Directory not found: $dir"
    fi
}

echo "Step 1: Removing summary/report documentation files..."
echo "----------------------------------------"
safe_remove "CLEANUP_SUMMARY.md"
safe_remove "CHART_FIXES_SUMMARY.md"
safe_remove "DEPLOYMENT_CLEANUP_REPORT.md"
safe_remove "SECURITY_FIXES_SUMMARY.md"
safe_remove "IMPROVEMENTS_SUMMARY.md"
safe_remove "FILES_CHANGED.md"
safe_remove "AWS_DEPLOYMENT_SUMMARY.txt"
safe_remove "BUILD_SUCCESS.md"
echo ""

echo "Step 2: Removing duplicate root-level test files..."
echo "----------------------------------------"
safe_remove "test_utils.py"
safe_remove "test_chart_fixes.py"
safe_remove "test_security_fixes.py"
echo ""

echo "Step 3: Cleaning Python cache files..."
echo "----------------------------------------"
echo "  Removing __pycache__ directories..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
echo "  Removing .pyc files..."
find . -type f -name "*.pyc" -delete 2>/dev/null || true
echo "  Removing .pyo files..."
find . -type f -name "*.pyo" -delete 2>/dev/null || true
echo "  Removing .pyd files..."
find . -type f -name "*.pyd" -delete 2>/dev/null || true
echo ""

echo "Step 4: Cleaning log files..."
echo "----------------------------------------"
if [ -d "logs" ]; then
    echo "  Removing log files in logs/ directory..."
    rm -f logs/*.log 2>/dev/null || true
    echo "  Keeping logs/ directory structure"
else
    echo "  No logs directory found"
fi
echo ""

echo "Step 5: Removing collected static files (will be regenerated)..."
echo "----------------------------------------"
if [ -d "staticfiles" ]; then
    echo "  Removing staticfiles/ directory..."
    safe_remove_dir "staticfiles"
    echo "  Note: Run 'python manage.py collectstatic' to regenerate"
else
    echo "  No staticfiles directory found"
fi
echo ""

echo "==========================================="
echo "Safe cleanup completed successfully!"
echo "==========================================="
echo ""
echo "Summary of removed items:"
echo "  - Documentation summary files (8 files)"
echo "  - Duplicate test files (3 files)"
echo "  - Python cache files (__pycache__, *.pyc)"
echo "  - Log files (*.log)"
echo "  - Collected static files (staticfiles/)"
echo ""
echo "Files that need MANUAL REVIEW before removal:"
echo "  1. performance_settings.py - Verify not imported anywhere"
echo "  2. build_scripts/ - Remove if not building desktop app"
echo "  3. build_requirements.txt - Remove if not building desktop app"
echo "  4. Dockerfile* and docker-compose* - Remove if not using Docker"
echo "  5. Deployment docs - Consolidate into single guide"
echo "  6. db.sqlite3 - Add to .gitignore if not already"
echo ""
echo "Code changes recommended (see COMPREHENSIVE_CODE_CLEANUP_REPORT.md):"
echo "  1. Remove @csrf_exempt decorators in eda/views.py"
echo "  2. Remove unused imports in home/views.py"
echo "  3. Remove duplicate optimize_dataframe_dtypes() in home/views.py"
echo "  4. Replace print() statements with proper logging"
echo "  5. Update README.md to remove pickle references"
echo ""
echo "For detailed analysis, see:"
echo "  COMPREHENSIVE_CODE_CLEANUP_REPORT.md"
echo ""
