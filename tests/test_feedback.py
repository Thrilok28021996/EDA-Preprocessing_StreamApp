import json
from django.test import TestCase, Client
from django.urls import reverse


class FeedbackViewsTestCase(TestCase):
    """Test cases for feedback app views"""
    
    def setUp(self):
        self.client = Client()
        self.feedback_url = reverse('feedback:index')
        self.submit_feedback_url = reverse('feedback:submit_feedback')
    
    def test_feedback_page_loads(self):
        """Test that feedback page loads successfully"""
        response = self.client.get(self.feedback_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Contact & Feedback')
        self.assertContains(response, 'Thrilok E')
        self.assertContains(response, 'Send Feedback')
    
    def test_feedback_page_context(self):
        """Test feedback page context variables"""
        response = self.client.get(self.feedback_url)
        self.assertIn('info', response.context)
        
        info = response.context['info']
        self.assertEqual(info['Full_Name'], 'Thrilok E')
        self.assertEqual(info['Email'], 'thriloke96@gmail.com')
        self.assertIn('github.com', info['Github'])
    
    def test_valid_feedback_submission_json(self):
        """Test valid feedback submission with JSON data"""
        feedback_data = {
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'subject': 'Bug Report',
            'message': 'I found a bug in the chart generation feature.'
        }
        
        response = self.client.post(
            self.submit_feedback_url,
            json.dumps(feedback_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success'))
        self.assertIn('message', data)
        self.assertIn('Thank you', data['message'])
    
    def test_valid_feedback_submission_form_data(self):
        """Test valid feedback submission with form data"""
        feedback_data = {
            'name': 'Jane Smith',
            'email': 'jane.smith@example.com',
            'subject': 'Feature Request',
            'message': 'Please add more chart types to the EDA section.'
        }
        
        response = self.client.post(self.submit_feedback_url, feedback_data)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success'))
        self.assertIn('message', data)
    
    def test_feedback_submission_missing_required_fields(self):
        """Test feedback submission with missing required fields"""
        incomplete_data = {
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            # Missing message field
        }
        
        response = self.client.post(
            self.submit_feedback_url,
            json.dumps(incomplete_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data.get('success'))
        self.assertIn('error', data)
        self.assertIn('required fields', data['error'])
    
    def test_feedback_submission_invalid_email(self):
        """Test feedback submission with invalid email"""
        invalid_email_data = {
            'name': 'John Doe',
            'email': 'invalid-email',  # Invalid email format
            'subject': 'Bug Report',
            'message': 'Test message'
        }
        
        response = self.client.post(
            self.submit_feedback_url,
            json.dumps(invalid_email_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data.get('success'))
        self.assertIn('error', data)
        self.assertIn('valid email', data['error'])
    
    def test_feedback_submission_empty_fields(self):
        """Test feedback submission with empty required fields"""
        empty_data = {
            'name': '',
            'email': 'john.doe@example.com',
            'subject': 'Bug Report',
            'message': ''
        }
        
        response = self.client.post(
            self.submit_feedback_url,
            json.dumps(empty_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data.get('success'))
        self.assertIn('error', data)
    
    def test_feedback_submission_whitespace_fields(self):
        """Test feedback submission with whitespace-only fields"""
        whitespace_data = {
            'name': '   ',
            'email': 'john.doe@example.com',
            'subject': 'Bug Report',
            'message': '   '
        }
        
        response = self.client.post(
            self.submit_feedback_url,
            json.dumps(whitespace_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data.get('success'))
        self.assertIn('error', data)
    
    def test_feedback_submission_get_request(self):
        """Test feedback submission with GET request (should fail)"""
        response = self.client.get(self.submit_feedback_url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data.get('success'))
        self.assertIn('error', data)
        self.assertIn('POST requests', data['error'])
    
    def test_feedback_submission_long_message(self):
        """Test feedback submission with very long message"""
        long_message = 'A' * 5000  # Very long message
        feedback_data = {
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'subject': 'Bug Report',
            'message': long_message
        }
        
        response = self.client.post(
            self.submit_feedback_url,
            json.dumps(feedback_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        # Should still work, but might have a note about email configuration
        self.assertTrue(data.get('success'))
    
    def test_feedback_submission_special_characters(self):
        """Test feedback submission with special characters"""
        feedback_data = {
            'name': 'José María',
            'email': 'jose.maria@example.com',
            'subject': 'Feature Request',
            'message': 'Please add support for special characters: áéíóú, ñ, ç, etc.'
        }
        
        response = self.client.post(
            self.submit_feedback_url,
            json.dumps(feedback_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success'))
    
    def test_feedback_session_storage(self):
        """Test that feedback is stored in session"""
        feedback_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'Test message for session storage.'
        }
        
        response = self.client.post(
            self.submit_feedback_url,
            json.dumps(feedback_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success'))
        
        # Check that feedback is stored in session
        session = self.client.session
        self.assertIn('feedback_submissions', session)
        self.assertTrue(len(session['feedback_submissions']) > 0)
        
        # Verify feedback data
        stored_feedback = session['feedback_submissions'][0]
        self.assertEqual(stored_feedback['name'], 'Test User')
        self.assertEqual(stored_feedback['email'], 'test@example.com')
        self.assertIn('timestamp', stored_feedback)
        self.assertIn('ip_address', stored_feedback)
    
    def test_multiple_feedback_submissions(self):
        """Test multiple feedback submissions in same session"""
        # Submit first feedback
        feedback_data_1 = {
            'name': 'User One',
            'email': 'user1@example.com',
            'subject': 'First Feedback',
            'message': 'This is the first feedback.'
        }
        
        self.client.post(
            self.submit_feedback_url,
            json.dumps(feedback_data_1),
            content_type='application/json'
        )
        
        # Submit second feedback
        feedback_data_2 = {
            'name': 'User Two',
            'email': 'user2@example.com',
            'subject': 'Second Feedback',
            'message': 'This is the second feedback.'
        }
        
        response = self.client.post(
            self.submit_feedback_url,
            json.dumps(feedback_data_2),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success'))
        
        # Check that both feedbacks are stored
        session = self.client.session
        self.assertEqual(len(session['feedback_submissions']), 2)
    
    def test_feedback_email_failure_handling(self):
        """Test handling when email sending fails"""
        # This test assumes email backend is not properly configured
        feedback_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'Test message for email failure handling.'
        }
        
        response = self.client.post(
            self.submit_feedback_url,
            json.dumps(feedback_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success'))
        
        # Should still succeed even if email fails
        # May include a note about email configuration
        if 'note' in data:
            self.assertIn('development mode', data['note'])
    
    def test_feedback_with_system_info(self):
        """Test feedback submission with system information"""
        feedback_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Bug Report',
            'message': 'Bug report with system info.\n\n--- System Information ---\nBrowser: Mozilla/5.0\nScreen: 1920x1080'
        }
        
        response = self.client.post(
            self.submit_feedback_url,
            json.dumps(feedback_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success'))
        
        # Verify system info is preserved in session
        session = self.client.session
        stored_feedback = session['feedback_submissions'][-1]
        self.assertIn('System Information', stored_feedback['message'])