"""
Unit tests for utils.py module

Tests cover DataFrame operations, session management, preprocessing,
and data analysis functionality.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
import io

import sys
sys.path.insert(0, '/Volumes/personal/programmingFolders/saas/EDA-Preprocessing_StreamApp_main/django_eda_app')

from utils import (
    get_memory_usage_info,
    optimize_dataframe_memory,
    check_missing_values,
    find_duplicates,
    detect_outliers,
    check_data_types,
    get_basic_info,
    get_column_statistics,
    export_dataframe,
)


@pytest.mark.unit
class TestMemoryManagement:
    """Tests for memory management functions"""

    def test_get_memory_usage_info(self, sample_dataframe):
        """Test memory usage information retrieval"""
        memory_info = get_memory_usage_info(sample_dataframe)

        assert 'total_memory_mb' in memory_info
        assert 'shape' in memory_info
        assert 'column_memory' in memory_info
        assert 'dtype_distribution' in memory_info

        assert memory_info['shape'] == (5, 5)
        assert isinstance(memory_info['total_memory_mb'], float)
        assert len(memory_info['column_memory']) == 5

    def test_optimize_dataframe_memory(self, sample_dataframe):
        """Test DataFrame memory optimization"""
        original_memory = sample_dataframe.memory_usage(deep=True).sum()
        optimized_df = optimize_dataframe_memory(sample_dataframe)

        # Check that optimization doesn't change data
        pd.testing.assert_frame_equal(
            sample_dataframe.astype(str),
            optimized_df.astype(str)
        )

        # Memory should be same or reduced
        optimized_memory = optimized_df.memory_usage(deep=True).sum()
        assert optimized_memory <= original_memory


@pytest.mark.unit
class TestMissingValues:
    """Tests for missing value detection"""

    def test_check_missing_values_no_missing(self, sample_dataframe):
        """Test missing value check with no missing values"""
        result = check_missing_values(sample_dataframe)

        assert result['total_missing'] == 0
        assert len(result['columns_with_missing']) == 0
        assert result['missing_counts'] is not None

    def test_check_missing_values_with_missing(self, sample_dataframe_with_missing):
        """Test missing value check with missing values"""
        result = check_missing_values(sample_dataframe_with_missing)

        assert result['total_missing'] == 3
        assert len(result['columns_with_missing']) == 3

        # Check that percentages are calculated correctly
        for col_info in result['columns_with_missing']:
            assert 'column' in col_info
            assert 'count' in col_info
            assert 'percentage' in col_info
            assert col_info['percentage'] == 20.0  # 1 out of 5 is 20%


@pytest.mark.unit
class TestDuplicates:
    """Tests for duplicate detection"""

    def test_find_duplicates_no_duplicates(self, sample_dataframe):
        """Test duplicate detection with no duplicates"""
        result = find_duplicates(sample_dataframe)

        assert result['has_duplicates'] == False
        assert result['duplicate_count'] == 0
        assert len(result['duplicate_rows']) == 0
        assert result['unique_rows'] == 5

    def test_find_duplicates_with_duplicates(self, sample_dataframe_with_duplicates):
        """Test duplicate detection with duplicates"""
        result = find_duplicates(sample_dataframe_with_duplicates)

        assert result['has_duplicates'] == True
        assert result['duplicate_count'] == 1
        assert result['total_rows'] == 5
        assert result['unique_rows'] == 4


@pytest.mark.unit
class TestOutliers:
    """Tests for outlier detection"""

    def test_detect_outliers_with_outliers(self, sample_dataframe_with_outliers):
        """Test outlier detection with outliers present"""
        result = detect_outliers(sample_dataframe_with_outliers, 'with_outliers')

        assert 'column' in result
        assert result['column'] == 'with_outliers'
        assert 'total_outliers' in result
        assert result['total_outliers'] > 0
        assert 'lower_bound' in result
        assert 'upper_bound' in result
        assert 'q1' in result
        assert 'q3' in result
        assert 'iqr' in result

    def test_detect_outliers_invalid_column(self, sample_dataframe):
        """Test outlier detection with invalid column name"""
        with pytest.raises(ValueError, match="Column .* not found"):
            detect_outliers(sample_dataframe, 'nonexistent_column')

    def test_detect_outliers_non_numeric_column(self, sample_dataframe):
        """Test outlier detection with non-numeric column"""
        with pytest.raises(ValueError, match="Column .* is not numeric"):
            detect_outliers(sample_dataframe, 'name')


@pytest.mark.unit
class TestDataTypes:
    """Tests for data type checking"""

    def test_check_data_types(self, sample_dataframe):
        """Test data type checking"""
        result = check_data_types(sample_dataframe)

        assert 'column_types' in result
        assert 'numeric_columns' in result
        assert 'categorical_columns' in result
        assert 'datetime_columns' in result
        assert 'total_columns' in result

        assert result['total_columns'] == 5
        assert len(result['numeric_columns']) == 3  # id, age, salary
        assert len(result['categorical_columns']) == 2  # name, department

    def test_get_basic_info(self, sample_dataframe):
        """Test basic DataFrame info retrieval"""
        result = get_basic_info(sample_dataframe)

        assert result['shape'] == (5, 5)
        assert len(result['columns']) == 5
        assert 'dtypes' in result
        assert 'memory_usage' in result
        assert result['total_nulls'] == 0


@pytest.mark.unit
class TestColumnStatistics:
    """Tests for column statistics"""

    def test_get_column_statistics_numeric(self, sample_dataframe):
        """Test statistics for numeric column"""
        result = get_column_statistics(sample_dataframe, 'age')

        assert result['type'] == 'numeric'
        assert result['count'] == 5
        assert result['mean'] == 35.0
        assert result['median'] == 35.0
        assert result['min'] == 25.0
        assert result['max'] == 45.0
        assert 'std' in result
        assert 'q25' in result
        assert 'q75' in result

    def test_get_column_statistics_categorical(self, sample_dataframe):
        """Test statistics for categorical column"""
        result = get_column_statistics(sample_dataframe, 'department')

        assert result['type'] == 'categorical'
        assert result['count'] == 5
        assert result['unique_values'] == 3
        assert 'frequency_counts' in result
        assert result['frequency_counts']['HR'] == 2
        assert result['frequency_counts']['IT'] == 2

    def test_get_column_statistics_invalid_column(self, sample_dataframe):
        """Test statistics with invalid column name"""
        with pytest.raises(ValueError, match="Column .* not found"):
            get_column_statistics(sample_dataframe, 'nonexistent')


@pytest.mark.unit
class TestDataExport:
    """Tests for data export functionality"""

    def test_export_dataframe_csv(self, sample_dataframe):
        """Test CSV export"""
        content, mime_type, extension = export_dataframe(sample_dataframe, 'csv')

        assert mime_type == 'text/csv'
        assert extension == 'csv'
        assert isinstance(content, bytes)
        assert b'Alice' in content
        assert b'Bob' in content

    def test_export_dataframe_json(self, sample_dataframe):
        """Test JSON export"""
        content, mime_type, extension = export_dataframe(sample_dataframe, 'json')

        assert mime_type == 'application/json'
        assert extension == 'json'
        assert isinstance(content, bytes)
        assert b'Alice' in content

    def test_export_dataframe_excel(self, sample_dataframe):
        """Test Excel export"""
        content, mime_type, extension = export_dataframe(sample_dataframe, 'excel')

        assert mime_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        assert extension == 'xlsx'
        assert isinstance(content, bytes)
        assert len(content) > 0

    def test_export_dataframe_invalid_format(self, sample_dataframe):
        """Test export with invalid format"""
        with pytest.raises(ValueError, match="Unsupported export format"):
            export_dataframe(sample_dataframe, 'invalid_format')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
