import json
import pandas as pd
from django.test import TestCase, Client
from django.urls import reverse
from django.http import HttpRequest
from security_utils import serialize_dataframe_to_json


class EDAViewsTestCase(TestCase):
    """Test cases for EDA app views"""
    
    def setUp(self):
        self.client = Client()
        self.eda_url = reverse('eda:index')
        self.generate_chart_url = reverse('eda:generate_chart')
        self.analyze_data_url = reverse('eda:analyze_data')
        
        # Create sample DataFrame for testing
        self.sample_data = {
            'numeric_col1': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'numeric_col2': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
            'categorical_col': ['A', 'B', 'C', 'A', 'B', 'C', 'A', 'B', 'C', 'A'],
            'string_col': ['apple', 'banana', 'cherry', 'apple', 'banana', 
                          'cherry', 'apple', 'banana', 'cherry', 'apple'],
            'mixed_col': [1, 2, 'text', 4, 5, 6, 'data', 8, 9, 10]
        }
        self.df = pd.DataFrame(self.sample_data)
        
        # Store DataFrame in session using secure JSON serialization
        session = self.client.session
        session['df_data'] = serialize_dataframe_to_json(self.df)
        session['df_uploaded'] = True
        session['df_filename'] = 'test_data.csv'
        session['df_shape'] = list(self.df.shape)  # Convert tuple to list for JSON
        session['df_columns'] = list(self.df.columns)
        session.save()
    
    def test_eda_page_with_data(self):
        """Test EDA page loads with data in session"""
        response = self.client.get(self.eda_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Exploratory Data Analysis')
        self.assertNotContains(response, 'No Data Found')
        
        # Check that columns are passed to template
        self.assertIn('numeric_columns', response.context)
        self.assertIn('categorical_columns', response.context)
    
    def test_eda_page_without_data(self):
        """Test EDA page without data in session"""
        # Clear session
        session = self.client.session
        session.flush()
        
        response = self.client.get(self.eda_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No Data Found')
    
    def test_generate_bar_chart(self):
        """Test bar chart generation"""
        chart_data = {
            'chart_type': 'bar',
            'options': {
                'column': 'categorical_col'
            }
        }
        
        response = self.client.post(
            self.generate_chart_url,
            json.dumps(chart_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success'))
        self.assertIn('chart_data', data)
        self.assertIn('layout', data)
    
    def test_generate_line_chart(self):
        """Test line chart generation"""
        chart_data = {
            'chart_type': 'line',
            'options': {
                'x_column': 'numeric_col1',
                'y_column': 'numeric_col2'
            }
        }
        
        response = self.client.post(
            self.generate_chart_url,
            json.dumps(chart_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success'))
        self.assertIn('chart_data', data)
    
    def test_generate_histogram(self):
        """Test histogram generation"""
        chart_data = {
            'chart_type': 'histogram',
            'options': {
                'column': 'numeric_col1',
                'bins': 5
            }
        }
        
        response = self.client.post(
            self.generate_chart_url,
            json.dumps(chart_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success'))
    
    def test_generate_pie_chart(self):
        """Test pie chart generation"""
        chart_data = {
            'chart_type': 'pie',
            'options': {
                'column': 'categorical_col'
            }
        }
        
        response = self.client.post(
            self.generate_chart_url,
            json.dumps(chart_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success'))
    
    def test_generate_scatter_plot(self):
        """Test scatter plot generation"""
        chart_data = {
            'chart_type': 'scatter',
            'options': {
                'x_column': 'numeric_col1',
                'y_column': 'numeric_col2'
            }
        }
        
        response = self.client.post(
            self.generate_chart_url,
            json.dumps(chart_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success'))
    
    def test_generate_box_plot(self):
        """Test box plot generation"""
        chart_data = {
            'chart_type': 'box',
            'options': {
                'column': 'numeric_col1'
            }
        }
        
        response = self.client.post(
            self.generate_chart_url,
            json.dumps(chart_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success'))
    
    def test_generate_heatmap(self):
        """Test heatmap generation"""
        chart_data = {
            'chart_type': 'heatmap',
            'options': {}
        }
        
        response = self.client.post(
            self.generate_chart_url,
            json.dumps(chart_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success'))
    
    def test_generate_area_chart(self):
        """Test area chart generation"""
        chart_data = {
            'chart_type': 'area',
            'options': {
                'x_column': 'numeric_col1',
                'y_column': 'numeric_col2'
            }
        }
        
        response = self.client.post(
            self.generate_chart_url,
            json.dumps(chart_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success'))
    
    def test_invalid_chart_type(self):
        """Test invalid chart type handling"""
        chart_data = {
            'chart_type': 'invalid_chart',
            'options': {}
        }
        
        response = self.client.post(
            self.generate_chart_url,
            json.dumps(chart_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data.get('success'))
        self.assertIn('error', data)
    
    def test_chart_generation_without_data(self):
        """Test chart generation without data in session"""
        # Clear session
        session = self.client.session
        session.flush()
        
        chart_data = {
            'chart_type': 'bar',
            'options': {'column': 'test'}
        }
        
        response = self.client.post(
            self.generate_chart_url,
            json.dumps(chart_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data.get('success'))
        self.assertIn('error', data)
    
    def test_show_data_analysis(self):
        """Test show data analysis"""
        analysis_data = {
            'analysis_type': 'show_data',
            'options': {}
        }
        
        response = self.client.post(
            self.analyze_data_url,
            json.dumps(analysis_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success'))
        self.assertIn('html', data)
    
    def test_missing_values_analysis(self):
        """Test missing values analysis"""
        analysis_data = {
            'analysis_type': 'missing_values',
            'options': {}
        }
        
        response = self.client.post(
            self.analyze_data_url,
            json.dumps(analysis_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success'))
        self.assertIn('html', data)
    
    def test_duplicates_analysis(self):
        """Test duplicates analysis"""
        analysis_data = {
            'analysis_type': 'duplicates',
            'options': {}
        }
        
        response = self.client.post(
            self.analyze_data_url,
            json.dumps(analysis_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success'))
    
    def test_outliers_analysis(self):
        """Test outliers analysis"""
        analysis_data = {
            'analysis_type': 'outliers',
            'options': {
                'column': 'numeric_col1'
            }
        }
        
        response = self.client.post(
            self.analyze_data_url,
            json.dumps(analysis_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success'))
    
    def test_data_types_analysis(self):
        """Test data types analysis"""
        analysis_data = {
            'analysis_type': 'data_types',
            'options': {}
        }
        
        response = self.client.post(
            self.analyze_data_url,
            json.dumps(analysis_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success'))
    
    def test_invalid_analysis_type(self):
        """Test invalid analysis type handling"""
        analysis_data = {
            'analysis_type': 'invalid_analysis',
            'options': {}
        }
        
        response = self.client.post(
            self.analyze_data_url,
            json.dumps(analysis_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data.get('success'))
        self.assertIn('error', data)
    
    def test_analysis_without_data(self):
        """Test analysis without data in session"""
        # Clear session
        session = self.client.session
        session.flush()
        
        analysis_data = {
            'analysis_type': 'show_data',
            'options': {}
        }
        
        response = self.client.post(
            self.analyze_data_url,
            json.dumps(analysis_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data.get('success'))
        self.assertIn('error', data)