"""
Pytest configuration and fixtures for Django EDA Application tests

This module provides common fixtures and test configuration
for all test modules in the test suite.
"""

import pytest
import pandas as pd
import numpy as np
from django.test import Client
from django.contrib.auth.models import User


@pytest.fixture
def api_client():
    """Fixture providing a Django test client"""
    return Client()


@pytest.fixture
def sample_dataframe():
    """Fixture providing a sample pandas DataFrame for testing"""
    return pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
        'age': [25, 30, 35, 40, 45],
        'salary': [50000, 60000, 70000, 80000, 90000],
        'department': ['HR', 'IT', 'IT', 'Sales', 'HR']
    })


@pytest.fixture
def sample_dataframe_with_missing():
    """Fixture providing a DataFrame with missing values"""
    return pd.DataFrame({
        'col1': [1, 2, np.nan, 4, 5],
        'col2': ['a', 'b', 'c', np.nan, 'e'],
        'col3': [1.1, 2.2, 3.3, 4.4, np.nan]
    })


@pytest.fixture
def sample_dataframe_with_duplicates():
    """Fixture providing a DataFrame with duplicate rows"""
    return pd.DataFrame({
        'id': [1, 2, 3, 2, 5],
        'value': ['a', 'b', 'c', 'b', 'e']
    })


@pytest.fixture
def sample_dataframe_with_outliers():
    """Fixture providing a DataFrame with outliers"""
    data = pd.DataFrame({
        'normal': np.random.normal(100, 10, 100),
        'with_outliers': list(np.random.normal(100, 10, 95)) + [200, 250, 300, 350, 400]
    })
    return data


@pytest.fixture
def test_user(db):
    """Fixture providing a test user"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def authenticated_client(api_client, test_user):
    """Fixture providing an authenticated test client"""
    api_client.force_login(test_user)
    return api_client


@pytest.fixture
def sample_csv_content():
    """Fixture providing sample CSV content as bytes"""
    csv_data = """id,name,age,salary
1,Alice,25,50000
2,Bob,30,60000
3,Charlie,35,70000"""
    return csv_data.encode('utf-8')
