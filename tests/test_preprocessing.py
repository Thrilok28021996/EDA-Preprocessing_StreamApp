import json
import pandas as pd
from django.test import TestCase, Client
from django.urls import reverse
from django.http import HttpResponse
from security_utils import serialize_dataframe_to_json, deserialize_dataframe_from_json


class PreprocessingViewsTestCase(TestCase):
    """Test cases for preprocessing app views"""
    
    def setUp(self):
        self.client = Client()
        self.preprocessing_url = reverse('preprocessing:index')
        self.apply_preprocessing_url = reverse('preprocessing:apply_preprocessing')
        self.get_column_values_url = reverse('preprocessing:get_column_values')
        self.export_csv_url = reverse('preprocessing:export_data', args=['csv'])
        self.export_json_url = reverse('preprocessing:export_data', args=['json'])
        
        # Create sample DataFrame for testing
        self.sample_data = {
            'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank', 'Grace', 'Henry', 'Ivy', 'Jack'],
            'age': [25, 30, 35, 25, 40, 30, 25, 45, 35, 30],
            'salary': [50000, 60000, 70000, 50000, 80000, 60000, 50000, 90000, 70000, 60000],
            'department': ['IT', 'HR', 'IT', 'Finance', 'IT', 'HR', 'Finance', 'IT', 'HR', 'Finance'],
            'missing_col': [1, None, 3, 4, None, 6, 7, None, 9, 10]
        }
        self.df = pd.DataFrame(self.sample_data)
        
        # Store DataFrame in session using secure JSON serialization
        session = self.client.session
        session['df_data'] = serialize_dataframe_to_json(self.df)
        session['original_df_data'] = serialize_dataframe_to_json(self.df)
        session['df_uploaded'] = True
        session['df_filename'] = 'test_data.csv'
        session['df_shape'] = list(self.df.shape)  # Convert tuple to list for JSON
        session['df_columns'] = list(self.df.columns)
        session.save()
    
    def test_preprocessing_page_with_data(self):
        """Test preprocessing page loads with data in session"""
        response = self.client.get(self.preprocessing_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Data Preprocessing')
        self.assertNotContains(response, 'No Data Found')
        
        # Check that context variables are set
        self.assertIn('df_info', response.context)
        self.assertIn('numeric_columns', response.context)
        self.assertIn('categorical_columns', response.context)
    
    def test_preprocessing_page_without_data(self):
        """Test preprocessing page without data in session"""
        # Clear session
        session = self.client.session
        session.flush()
        
        response = self.client.get(self.preprocessing_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No Data Found')
    
    def test_select_columns_operation(self):
        """Test select columns preprocessing operation"""
        operation_data = {
            'operation': 'select_columns',
            'params': {
                'columns': ['name', 'age', 'salary']
            }
        }
        
        response = self.client.post(
            self.apply_preprocessing_url,
            json.dumps(operation_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success'))
        self.assertEqual(data.get('new_shape'), [10, 3])  # 10 rows, 3 columns
    
    def test_drop_columns_operation(self):
        """Test drop columns preprocessing operation"""
        operation_data = {
            'operation': 'drop_columns',
            'params': {
                'columns': ['id', 'missing_col']
            }
        }
        
        response = self.client.post(
            self.apply_preprocessing_url,
            json.dumps(operation_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success'))
        self.assertEqual(data.get('new_shape'), [10, 4])  # 10 rows, 4 columns remaining
    
    def test_replace_values_operation(self):
        """Test replace values preprocessing operation"""
        operation_data = {
            'operation': 'replace_values',
            'params': {
                'column': 'department',
                'old_value': 'IT',
                'new_value': 'Technology'
            }
        }
        
        response = self.client.post(
            self.apply_preprocessing_url,
            json.dumps(operation_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success'))
        
        # Verify the replacement worked by checking session data
        session = self.client.session
        updated_df = deserialize_dataframe_from_json(session['df_data'])
        self.assertNotIn('IT', updated_df['department'].values)
        self.assertIn('Technology', updated_df['department'].values)
    
    def test_drop_duplicates_operation(self):
        """Test drop duplicates preprocessing operation"""
        # First add some duplicates to the data
        duplicate_data = self.sample_data.copy()
        duplicate_data['id'].extend([1, 2])
        duplicate_data['name'].extend(['Alice', 'Bob'])
        duplicate_data['age'].extend([25, 30])
        duplicate_data['salary'].extend([50000, 60000])
        duplicate_data['department'].extend(['IT', 'HR'])
        duplicate_data['missing_col'].extend([1, None])
        
        df_with_duplicates = pd.DataFrame(duplicate_data)
        session = self.client.session
        session['df_data'] = serialize_dataframe_to_json(df_with_duplicates)
        session.save()
        
        operation_data = {
            'operation': 'drop_duplicates',
            'params': {}
        }
        
        response = self.client.post(
            self.apply_preprocessing_url,
            json.dumps(operation_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success'))
    
    def test_drop_missing_values_operation(self):
        """Test drop missing values preprocessing operation"""
        operation_data = {
            'operation': 'drop_missing',
            'params': {
                'how': 'any',
                'subset': ['missing_col']
            }
        }
        
        response = self.client.post(
            self.apply_preprocessing_url,
            json.dumps(operation_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success'))
        
        # Should have fewer rows after dropping missing values
        self.assertLess(data.get('new_shape')[0], 10)
    
    def test_fill_missing_values_operation(self):
        """Test fill missing values preprocessing operation"""
        operation_data = {
            'operation': 'fill_missing',
            'params': {
                'method': 'constant',
                'constant_value': '999',
                'columns': ['missing_col']
            }
        }
        
        response = self.client.post(
            self.apply_preprocessing_url,
            json.dumps(operation_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success'))
    
    def test_filter_data_operation(self):
        """Test filter data preprocessing operation"""
        operation_data = {
            'operation': 'filter_data',
            'params': {
                'filters': [
                    {
                        'column': 'age',
                        'operator': 'greater_than',
                        'value': '30'
                    }
                ]
            }
        }
        
        response = self.client.post(
            self.apply_preprocessing_url,
            json.dumps(operation_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success'))
        
        # Should have fewer rows after filtering
        self.assertLess(data.get('new_shape')[0], 10)
    
    def test_reset_data_operation(self):
        """Test reset data preprocessing operation"""
        # First modify the data
        operation_data = {
            'operation': 'drop_columns',
            'params': {
                'columns': ['id']
            }
        }
        self.client.post(
            self.apply_preprocessing_url,
            json.dumps(operation_data),
            content_type='application/json'
        )
        
        # Then reset
        reset_data = {
            'operation': 'reset_data',
            'params': {}
        }
        
        response = self.client.post(
            self.apply_preprocessing_url,
            json.dumps(reset_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success'))
        self.assertEqual(data.get('new_shape'), [10, 6])  # Back to original shape
    
    def test_get_column_values(self):
        """Test get column values endpoint"""
        request_data = {
            'column': 'department'
        }
        
        response = self.client.post(
            self.get_column_values_url,
            json.dumps(request_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success'))
        self.assertIn('values', data)
        
        expected_values = ['IT', 'HR', 'Finance']
        for value in expected_values:
            self.assertIn(value, data['values'])
    
    def test_export_csv_data(self):
        """Test CSV export functionality"""
        response = self.client.get(self.export_csv_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment', response['Content-Disposition'])
    
    def test_export_json_data(self):
        """Test JSON export functionality"""
        response = self.client.get(self.export_json_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertIn('attachment', response['Content-Disposition'])
    
    def test_invalid_operation(self):
        """Test invalid preprocessing operation"""
        operation_data = {
            'operation': 'invalid_operation',
            'params': {}
        }
        
        response = self.client.post(
            self.apply_preprocessing_url,
            json.dumps(operation_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data.get('success'))
        self.assertIn('error', data)
    
    def test_preprocessing_without_data(self):
        """Test preprocessing operations without data in session"""
        # Clear session
        session = self.client.session
        session.flush()
        
        operation_data = {
            'operation': 'select_columns',
            'params': {
                'columns': ['name']
            }
        }
        
        response = self.client.post(
            self.apply_preprocessing_url,
            json.dumps(operation_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data.get('success'))
        self.assertIn('error', data)
    
    def test_export_without_data(self):
        """Test export without data in session"""
        # Clear session
        session = self.client.session
        session.flush()
        
        response = self.client.get(self.export_csv_url)
        self.assertEqual(response.status_code, 302)  # Redirect to home
    
    def test_complex_filter_operation(self):
        """Test complex filtering with multiple conditions"""
        operation_data = {
            'operation': 'filter_data',
            'params': {
                'filters': [
                    {
                        'column': 'age',
                        'operator': 'greater_than',
                        'value': '25'
                    },
                    {
                        'column': 'department',
                        'operator': 'equals',
                        'value': 'IT'
                    }
                ]
            }
        }
        
        response = self.client.post(
            self.apply_preprocessing_url,
            json.dumps(operation_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success'))
    
    def test_fill_missing_with_mean(self):
        """Test fill missing values with mean method"""
        operation_data = {
            'operation': 'fill_missing',
            'params': {
                'method': 'mean',
                'columns': ['missing_col']
            }
        }
        
        response = self.client.post(
            self.apply_preprocessing_url,
            json.dumps(operation_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success'))