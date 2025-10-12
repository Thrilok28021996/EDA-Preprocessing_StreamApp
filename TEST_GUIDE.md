# EDA & Preprocessing Web Application - Test Guide

## 🧪 Testing Strategy

This application uses a comprehensive testing strategy covering unit tests, integration tests, and performance testing to ensure reliability and maintainability.

## 📋 Test Structure

```
tests/
├── __init__.py
├── test_home.py          # Home app tests (file upload, utilities)
├── test_eda.py           # EDA app tests (charts, analysis)
├── test_preprocessing.py # Preprocessing app tests (data operations)
└── test_feedback.py      # Feedback app tests (contact form)
```

## 🚀 Running Tests

### Quick Start

```bash
# Run all tests
python manage.py test

# Run specific test file
python manage.py test tests.test_home

# Run specific test class
python manage.py test tests.test_home.HomeViewsTestCase

# Run specific test method
python manage.py test tests.test_home.HomeViewsTestCase.test_valid_csv_upload
```

### With Coverage

```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run --source='.' manage.py test

# Generate coverage report
coverage report

# Generate HTML coverage report
coverage html
# View at: htmlcov/index.html
```

### Verbose Output

```bash
# Run tests with verbose output
python manage.py test --verbosity=2

# Keep test database for debugging
python manage.py test --keepdb

# Run tests in parallel (faster)
python manage.py test --parallel
```

## 📊 Test Categories

### 1. Unit Tests

#### Home App Tests (`test_home.py`)

**File Upload Tests:**
- ✅ Valid CSV file upload
- ✅ Invalid file extension handling
- ✅ File size limit enforcement
- ✅ Empty file handling
- ✅ Malformed CSV handling
- ✅ Large file processing

**DataFrame Optimization Tests:**
- ✅ Data type optimization
- ✅ Memory usage reduction
- ✅ Categorical conversion
- ✅ Numeric downcasting

**Session Management Tests:**
- ✅ DataFrame storage and retrieval
- ✅ Session data validation
- ✅ Corrupted session handling

#### EDA App Tests (`test_eda.py`)

**Chart Generation Tests:**
- ✅ Bar chart generation
- ✅ Line chart generation
- ✅ Histogram generation
- ✅ Pie chart generation
- ✅ Scatter plot generation
- ✅ Box plot generation
- ✅ Heatmap generation
- ✅ Area chart generation

**Data Analysis Tests:**
- ✅ Show data functionality
- ✅ Missing values analysis
- ✅ Duplicates detection
- ✅ Outliers analysis
- ✅ Data types analysis

**Error Handling Tests:**
- ✅ Invalid chart type handling
- ✅ Missing data scenarios
- ✅ Invalid analysis type handling

#### Preprocessing App Tests (`test_preprocessing.py`)

**Data Operations Tests:**
- ✅ Column selection
- ✅ Column dropping
- ✅ Value replacement
- ✅ Duplicate removal
- ✅ Missing value handling
- ✅ Data filtering
- ✅ Data reset functionality

**Export Tests:**
- ✅ CSV export
- ✅ JSON export
- ✅ Excel export (if configured)

**Complex Operations Tests:**
- ✅ Multi-condition filtering
- ✅ Statistical fill methods
- ✅ Column value retrieval

#### Feedback App Tests (`test_feedback.py`)

**Form Submission Tests:**
- ✅ Valid feedback submission (JSON)
- ✅ Valid feedback submission (form data)
- ✅ Missing required fields handling
- ✅ Invalid email format handling
- ✅ Long message handling
- ✅ Special characters support

**Session Storage Tests:**
- ✅ Feedback storage in session
- ✅ Multiple submissions handling
- ✅ Email failure handling

### 2. Integration Tests

Integration tests verify that different components work together correctly:

```python
# Example integration test
def test_full_workflow(self):
    """Test complete workflow from upload to analysis"""
    # 1. Upload CSV file
    response = self.client.post('/home/upload/', {'csv_file': self.csv_file})
    
    # 2. Generate chart
    response = self.client.post('/eda/generate-chart/', chart_data)
    
    # 3. Apply preprocessing
    response = self.client.post('/preprocessing/apply/', operation_data)
    
    # 4. Export data
    response = self.client.get('/preprocessing/export/csv/')
    
    # Verify entire workflow works
    self.assertEqual(response.status_code, 200)
```

### 3. Performance Tests

Performance tests ensure the application handles load and large datasets efficiently:

```python
# Example performance test
def test_large_dataset_processing(self):
    """Test processing of large datasets"""
    # Create large dataset (100k rows)
    large_data = self.create_large_dataset(100000)
    
    start_time = time.time()
    # Process dataset
    response = self.process_dataset(large_data)
    processing_time = time.time() - start_time
    
    # Verify performance requirements
    self.assertLess(processing_time, 30)  # Should complete in < 30 seconds
    self.assertEqual(response.status_code, 200)
```

## 🎯 Test Data Management

### Sample Data Generation

The test suite includes utilities for generating test data:

```python
# Create sample CSV data
sample_csv = """name,age,salary,department
John Doe,25,50000,Engineering
Jane Smith,30,60000,Marketing
Bob Johnson,35,55000,Sales"""

# Create large datasets
large_dataset = generate_large_dataset(rows=10000, columns=20)

# Create datasets with specific characteristics
dataset_with_nulls = create_dataset_with_missing_values(null_percentage=0.2)
dataset_with_duplicates = create_dataset_with_duplicates(duplicate_percentage=0.1)
```

### Test Fixtures

```python
# fixtures.py
class TestDataMixin:
    def setUp(self):
        self.sample_data = {
            'numeric_col': [1, 2, 3, 4, 5],
            'categorical_col': ['A', 'B', 'C', 'A', 'B'],
            'string_col': ['apple', 'banana', 'cherry', 'apple', 'banana']
        }
        self.df = pd.DataFrame(self.sample_data)
        
    def create_session_with_data(self):
        """Helper to create session with test data"""
        session = self.client.session
        session['df_data'] = pickle.dumps(self.df)
        session['df_uploaded'] = True
        session.save()
```

## 🔍 Testing Best Practices

### 1. Test Isolation

Each test is completely isolated and doesn't depend on other tests:

```python
def setUp(self):
    """Set up clean state for each test"""
    self.client = Client()
    # Clear any existing session data
    self.client.session.flush()
    
def tearDown(self):
    """Clean up after each test"""
    # Clean up any test files
    self.cleanup_test_files()
```

### 2. Mock External Dependencies

External services are mocked to ensure tests are reliable:

```python
@patch('django.core.mail.send_mail')
def test_email_sending(self, mock_send_mail):
    """Test email functionality with mocked email backend"""
    mock_send_mail.return_value = True
    
    response = self.submit_feedback()
    
    self.assertTrue(mock_send_mail.called)
    self.assertEqual(response.status_code, 200)
```

### 3. Test Error Conditions

Tests cover both success and failure scenarios:

```python
def test_csv_upload_success(self):
    """Test successful CSV upload"""
    # Test happy path
    
def test_csv_upload_invalid_format(self):
    """Test CSV upload with invalid format"""
    # Test error handling
    
def test_csv_upload_file_too_large(self):
    """Test CSV upload with oversized file"""
    # Test validation
```

## 📈 Performance Testing

### Load Testing with Locust

```python
# locustfile.py
from locust import HttpUser, task, between

class EDAUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Upload CSV file at start"""
        self.upload_csv()
    
    @task(3)
    def generate_chart(self):
        """Generate charts"""
        self.client.post("/eda/generate-chart/", json={
            "chart_type": "bar",
            "options": {"column": "category"}
        })
    
    @task(2)
    def apply_preprocessing(self):
        """Apply preprocessing operations"""
        self.client.post("/preprocessing/apply/", json={
            "operation": "drop_duplicates",
            "params": {}
        })
    
    @task(1)
    def export_data(self):
        """Export processed data"""
        self.client.get("/preprocessing/export/csv/")

# Run load test
# locust -f locustfile.py --host=http://localhost:8000
```

### Memory Usage Testing

```python
import psutil
import os

def test_memory_usage_large_dataset(self):
    """Test memory usage with large datasets"""
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    # Process large dataset
    large_csv = self.create_large_csv(100000)  # 100k rows
    self.client.post('/home/upload/', {'csv_file': large_csv})
    
    final_memory = process.memory_info().rss
    memory_increase = (final_memory - initial_memory) / (1024**2)  # MB
    
    # Memory increase should be reasonable
    self.assertLess(memory_increase, 500)  # Less than 500MB increase
```

## 🐛 Debugging Tests

### Running Tests in Debug Mode

```python
# Add to test method for debugging
import pdb; pdb.set_trace()

# Or use Django's debugging
from django.test.utils import override_settings

@override_settings(DEBUG=True)
def test_with_debug(self):
    """Test with debug information"""
    response = self.client.get('/eda/')
    print(f"Response content: {response.content}")
    print(f"Context: {response.context}")
```

### Test Database Inspection

```bash
# Keep test database after tests
python manage.py test --keepdb

# Inspect test database
python manage.py dbshell
```

## 📊 Test Coverage Goals

### Current Coverage Targets

- **Overall Coverage:** >90%
- **Views Coverage:** >95%
- **Utility Functions:** >90%
- **Error Handling:** >85%
- **Critical Paths:** 100%

### Coverage Report Example

```
Name                           Stmts   Miss  Cover   Missing
------------------------------------------------------------
home/views.py                    89      5    94%   45-47, 78
eda/views.py                    156     12    92%   89-92, 145-148
preprocessing/views.py          134      8    94%   67-69, 123-125
feedback/views.py                67      3    96%   45-47
eda_project/middleware.py       89      7    92%   78-82, 156-158
------------------------------------------------------------
TOTAL                          535     35    93%
```

## 🚨 Continuous Integration

### GitHub Actions Example

```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install coverage
    
    - name: Run tests with coverage
      run: |
        coverage run --source='.' manage.py test
        coverage report --fail-under=90
        coverage xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
```

## 📝 Test Documentation

### Writing New Tests

1. **Follow naming convention:** `test_feature_description`
2. **Use descriptive docstrings:** Explain what the test verifies
3. **Test both success and failure cases**
4. **Keep tests focused and atomic**
5. **Use appropriate assertions**

### Test Review Checklist

- [ ] Test covers the intended functionality
- [ ] Test includes error cases
- [ ] Test is properly isolated
- [ ] Test has descriptive name and docstring
- [ ] Test follows project testing conventions
- [ ] Test passes consistently
- [ ] Test contributes to coverage goals

---

## 🎯 Running Specific Test Scenarios

### Test File Upload Scenarios

```bash
# Test various file upload scenarios
python manage.py test tests.test_home.HomeViewsTestCase.test_valid_csv_upload
python manage.py test tests.test_home.HomeViewsTestCase.test_invalid_file_extension
python manage.py test tests.test_home.HomeViewsTestCase.test_file_size_limit
python manage.py test tests.test_home.HomeViewsTestCase.test_large_csv_processing
```

### Test Chart Generation

```bash
# Test all chart types
python manage.py test tests.test_eda.EDAViewsTestCase -k "chart"
```

### Test Data Processing

```bash
# Test preprocessing operations
python manage.py test tests.test_preprocessing.PreprocessingViewsTestCase
```

### Test Error Handling

```bash
# Test error handling across all apps
python manage.py test -k "error"
python manage.py test -k "invalid"
python manage.py test -k "failure"
```

This comprehensive test guide ensures the EDA & Preprocessing Web Application maintains high quality, reliability, and performance standards.