"""
Comprehensive test suite for EDA app
"""

import json
import pandas as pd
import numpy as np
from django.test import TestCase, Client
from django.urls import reverse
from utils import update_dataframe_in_session


class EDAViewsTestCase(TestCase):
    """Test case for EDA app views"""
    
    def setUp(self):
        """Set up test client and sample DataFrame"""
        self.client = Client()
        
        # Create sample DataFrame for testing
        self.sample_data = {
            'numeric_col': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'text_col': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'],
            'missing_col': [1, 2, np.nan, 4, 5, np.nan, 7, 8, 9, 10],
            'category_col': ['X', 'Y', 'X', 'Y', 'Z', 'X', 'Y', 'Z', 'X', 'Y']
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
    
    def test_eda_index_with_data(self):
        """Test EDA index page with uploaded data"""
        response = self.client.get(reverse('eda:index'))
        self.assertEqual(response.status_code, 200)
        
        # Check that page shows data information
        self.assertContains(response, 'Exploratory Data Analysis')
        self.assertContains(response, 'Chart Generation')
        self.assertContains(response, 'Data Analysis')
        
        # Check that chart options are available
        self.assertContains(response, 'Bar Chart')
        self.assertContains(response, 'Line Chart')
        self.assertContains(response, 'Histogram')
        self.assertContains(response, 'Pie Chart')
    
    def test_eda_index_without_data(self):
        """Test EDA index page without uploaded data"""
        # Clear session
        self.client.session.flush()
        
        response = self.client.get(reverse('eda:index'))
        self.assertEqual(response.status_code, 200)
        
        # Should show warning about no data
        self.assertContains(response, 'Please upload a CSV file')
        self.assertContains(response, 'No Data Found')
