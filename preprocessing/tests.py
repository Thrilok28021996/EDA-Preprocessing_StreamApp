"""
Comprehensive test suite for preprocessing app
"""

import json
import pandas as pd
import numpy as np
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.sessions.middleware import SessionMiddleware
from utils import update_dataframe_in_session


class PreprocessingViewsTestCase(TestCase):
    """Test case for preprocessing app views"""
    
    def setUp(self):
        """Set up test client and sample DataFrame"""
        self.client = Client()
        
        # Create sample DataFrame for testing
        self.sample_data = {
            'numeric_col': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'text_col': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'],
            'missing_col': [1, 2, np.nan, 4, 5, np.nan, 7, 8, 9, 10],
            'duplicate_col': [1, 1, 2, 2, 3, 3, 4, 5, 6, 7]
        }
        self.df = pd.DataFrame(self.sample_data)
        
        # Set up session with DataFrame
        self.setup_session_with_dataframe()
    
    def setup_session_with_dataframe(self):
        """Helper to set up session with sample DataFrame"""
        # Make a request to initialize session
        response = self.client.get('/')
        
        # Add DataFrame to session manually
        session = self.client.session
        success = update_dataframe_in_session(type('Request', (), {'session': session})(), self.df)
        session['df_uploaded'] = True
        session['df_filename'] = 'test.csv'
        session['df_shape'] = self.df.shape
        session['df_columns'] = list(self.df.columns)
        session.save()
    
    def test_preprocessing_index_with_data(self):
        """Test preprocessing index page with uploaded data"""
        response = self.client.get(reverse('preprocessing:index'))
        self.assertEqual(response.status_code, 200)
        
        # Check that page shows data information
        self.assertContains(response, 'Current Dataset')
        self.assertContains(response, 'Column Types')
        self.assertContains(response, 'Data Preview')
        
        # Check that preprocessing options are available
        self.assertContains(response, 'Select Columns')
        self.assertContains(response, 'Drop Columns')
        self.assertContains(response, 'Replace Values')
        self.assertContains(response, 'Remove Duplicates')
        self.assertContains(response, 'Filter Data')
    
    def test_preprocessing_index_without_data(self):
        """Test preprocessing index page without uploaded data"""
        # Clear session
        self.client.session.flush()
        
        response = self.client.get(reverse('preprocessing:index'))
        self.assertEqual(response.status_code, 200)
        
        # Should show warning about no data
        self.assertContains(response, 'Please upload a CSV file')
        self.assertContains(response, 'No Data Found')
    
    def test_apply_preprocessing_select_columns(self):
        """Test column selection preprocessing"""
        data = {
            'operation': 'select_columns',
            'params': {
                'columns': ['numeric_col', 'text_col']
            }
        }
        
        response = self.client.post(
            reverse('preprocessing:apply_preprocessing'),
            json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['new_shape'][1], 2)  # Should have 2 columns
        self.assertIn('successfully', response_data['message'])
    
    def test_export_data_csv(self):
        """Test exporting data as CSV"""
        response = self.client.get(reverse('preprocessing:export_data', args=['csv']))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'text/csv')
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn('processed_data.csv', response['Content-Disposition'])
