import os
import tempfile
import pandas as pd
import pickle
from io import StringIO
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages import get_messages
from utils import get_dataframe_from_session, optimize_dataframe_memory


class HomeViewsTestCase(TestCase):
    """Test cases for home app views"""
    
    def setUp(self):
        self.client = Client()
        self.upload_url = reverse('home:upload_csv')
        self.home_url = reverse('home:index')
        
        # Create sample CSV data
        self.sample_csv_content = """name,age,city,salary
John,25,New York,50000
Jane,30,Los Angeles,60000
Bob,35,Chicago,55000
Alice,28,Houston,52000"""
        
        self.large_csv_content = """id,value,category,score
""" + "\n".join([f"{i},{i*10},cat_{i%5},{i*0.1}" for i in range(1000)])
        
    def create_csv_file(self, content, filename='test.csv'):
        """Helper method to create CSV file for testing"""
        return SimpleUploadedFile(
            filename, 
            content.encode('utf-8'), 
            content_type='text/csv'
        )
    
    def test_home_page_loads(self):
        """Test that home page loads successfully"""
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'EDA & Preprocessing')
        self.assertContains(response, 'Thrilok E')
    
    def test_valid_csv_upload(self):
        """Test successful CSV file upload"""
        csv_file = self.create_csv_file(self.sample_csv_content)
        
        response = self.client.post(self.upload_url, {'csv_file': csv_file})
        self.assertEqual(response.status_code, 302)  # Redirect after successful upload
        
        # Check session data
        session = self.client.session
        self.assertTrue(session.get('df_uploaded'))
        self.assertEqual(session.get('df_filename'), 'test.csv')
        self.assertEqual(session.get('df_shape'), (4, 4))  # 4 rows, 4 columns
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('uploaded successfully' in str(m) for m in messages))
    
    def test_invalid_file_extension(self):
        """Test upload with invalid file extension"""
        txt_file = SimpleUploadedFile('test.txt', b'not a csv', content_type='text/plain')
        
        response = self.client.post(self.upload_url, {'csv_file': txt_file})
        self.assertEqual(response.status_code, 302)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('valid CSV file' in str(m) for m in messages))
    
    def test_no_file_selected(self):
        """Test upload without selecting a file"""
        response = self.client.post(self.upload_url, {})
        self.assertEqual(response.status_code, 302)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('No file selected' in str(m) for m in messages))
    
    def test_empty_csv_file(self):
        """Test upload of empty CSV file"""
        empty_csv = self.create_csv_file("")
        
        response = self.client.post(self.upload_url, {'csv_file': empty_csv})
        self.assertEqual(response.status_code, 302)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('empty' in str(m) for m in messages))
    
    def test_large_csv_processing(self):
        """Test processing of large CSV files"""
        large_csv = self.create_csv_file(self.large_csv_content, 'large_test.csv')
        
        response = self.client.post(self.upload_url, {'csv_file': large_csv})
        self.assertEqual(response.status_code, 302)
        
        # Check that file was processed successfully
        session = self.client.session
        self.assertTrue(session.get('df_uploaded'))
        self.assertEqual(session.get('df_shape'), (1000, 4))
    
    @override_settings(FILE_UPLOAD_MAX_MEMORY_SIZE=1024)  # 1KB limit for testing
    def test_file_size_limit(self):
        """Test file size limit enforcement"""
        large_content = "col1,col2\n" + "test,data\n" * 100  # Creates file larger than 1KB
        large_csv = self.create_csv_file(large_content)
        
        response = self.client.post(self.upload_url, {'csv_file': large_csv})
        self.assertEqual(response.status_code, 302)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('File size too large' in str(m) for m in messages))
    
    def test_malformed_csv(self):
        """Test upload of malformed CSV"""
        malformed_csv = self.create_csv_file("invalid,csv\ndata\nextra,data,too,many,columns")
        
        response = self.client.post(self.upload_url, {'csv_file': malformed_csv})
        self.assertEqual(response.status_code, 302)
        
        # Should still process but may have warnings
        session = self.client.session
        # The processing should handle malformed CSV gracefully
    
    def test_get_dataframe_from_session(self):
        """Test utility function for getting DataFrame from session"""
        # Upload a CSV first
        csv_file = self.create_csv_file(self.sample_csv_content)
        self.client.post(self.upload_url, {'csv_file': csv_file})
        
        # Create a mock request with session data
        from django.http import HttpRequest
        request = HttpRequest()
        request.session = self.client.session
        
        df = get_dataframe_from_session(request)
        self.assertIsNotNone(df)
        self.assertEqual(df.shape, (4, 4))
        self.assertIn('name', df.columns)
    
    def test_get_dataframe_from_empty_session(self):
        """Test getting DataFrame from empty session"""
        from django.http import HttpRequest
        request = HttpRequest()
        request.session = {}
        
        df = get_dataframe_from_session(request)
        self.assertIsNone(df)


class DataFrameOptimizationTestCase(TestCase):
    """Test cases for DataFrame optimization functions"""
    
    def setUp(self):
        # Create test DataFrame with various data types
        self.test_data = {
            'int_col': [1, 2, 3, 4, 5] * 20,  # Integer column
            'float_col': [1.1, 2.2, 3.3, 4.4, 5.5] * 20,  # Float column
            'string_col': ['A', 'B', 'C', 'A', 'B'] * 20,  # Categorical-like strings
            'mixed_col': ['1', '2', '3', 'text', 'data'] * 20,  # Mixed data
            'large_int': [1000000, 2000000, 3000000, 4000000, 5000000] * 20  # Large integers
        }
        self.df = pd.DataFrame(self.test_data)
    
    def test_optimize_dataframe_dtypes(self):
        """Test DataFrame data type optimization"""
        original_memory = self.df.memory_usage(deep=True).sum()
        optimized_df = optimize_dataframe_memory(self.df)
        optimized_memory = optimized_df.memory_usage(deep=True).sum()
        
        # Optimization should not increase memory usage
        self.assertLessEqual(optimized_memory, original_memory)
        
        # Check that string column with limited unique values becomes categorical
        self.assertEqual(str(optimized_df['string_col'].dtype), 'category')
        
        # Verify data integrity
        pd.testing.assert_frame_equal(
            self.df.reset_index(drop=True), 
            optimized_df.reset_index(drop=True), 
            check_dtype=False
        )
    
    def test_numeric_optimization(self):
        """Test numeric data type optimization"""
        # Create DataFrame with unnecessarily large numeric types
        numeric_df = pd.DataFrame({
            'small_int': pd.Series([1, 2, 3], dtype='int64'),
            'small_float': pd.Series([1.1, 2.2, 3.3], dtype='float64')
        })
        
        optimized = optimize_dataframe_memory(numeric_df)
        
        # Should downcast to smaller types
        self.assertIn(optimized['small_int'].dtype, ['int8', 'int16', 'int32'])
        self.assertIn(optimized['small_float'].dtype, ['float32'])
    
    def test_categorical_conversion(self):
        """Test conversion of appropriate string columns to categorical"""
        # Create DataFrame with high cardinality string column (should not convert)
        high_cardinality_df = pd.DataFrame({
            'unique_strings': [f'unique_{i}' for i in range(100)]
        })
        
        optimized = optimize_dataframe_memory(high_cardinality_df)
        
        # Should not convert high cardinality strings to categorical
        self.assertEqual(str(optimized['unique_strings'].dtype), 'object')