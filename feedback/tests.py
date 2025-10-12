"""
Comprehensive test suite for feedback app
"""

import json
from django.test import TestCase, Client
from django.urls import reverse


class FeedbackViewsTestCase(TestCase):
    """Test case for feedback app views"""
    
    def setUp(self):
        """Set up test client"""
        self.client = Client()
    
    def test_feedback_index_get(self):
        """Test GET request to feedback index"""
        response = self.client.get(reverse('feedback:index'))
        self.assertEqual(response.status_code, 200)
        
        # Check that page contains expected elements
        self.assertContains(response, 'Contact & Feedback')
        self.assertContains(response, 'Send Feedback')
        self.assertContains(response, 'feedback-form')
        
        # Check for developer info
        self.assertContains(response, 'Developer Info')
        self.assertContains(response, 'Thrilok')
        self.assertContains(response, 'thriloke96@gmail.com')
    
    def test_submit_feedback_valid_json(self):
        """Test submitting valid feedback via JSON"""
        feedback_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Test Feedback',
            'message': 'This is a test feedback message.'
        }
        
        response = self.client.post(
            reverse('feedback:submit_feedback'),
            json.dumps(feedback_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        
        self.assertTrue(response_data['success'])
        self.assertIn('Thank you for your feedback', response_data['message'])
    
    def test_submit_feedback_missing_fields(self):
        """Test submitting feedback with missing required fields"""
        feedback_data = {
            'email': 'test@example.com',
            'message': 'Missing name field'
        }
        
        response = self.client.post(
            reverse('feedback:submit_feedback'),
            json.dumps(feedback_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        
        self.assertFalse(response_data['success'])
        self.assertIn('Please fill in all required fields', response_data['error'])
