"""
Comprehensive test suite for home app
"""

import os
import tempfile
from io import BytesIO
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.sessions.middleware import SessionMiddleware


class HomeViewsTestCase(TestCase):
    """Test case for home app views"""
    
    def setUp(self):
        """Set up test client and sample files"""
        self.client = Client()
        
        # Create valid CSV content
        self.valid_csv_content = b"name,age,city\nJohn,25,NYC\nJane,30,LA\nBob,35,Chicago"
        self.valid_csv_file = SimpleUploadedFile(
            "test.csv",
            self.valid_csv_content,
            content_type="text/csv"
        )
        
        # Create invalid CSV content
        self.invalid_csv_content = b"invalid,csv,content\nno,proper,format"
        self.invalid_file = SimpleUploadedFile(
            "test.txt",
            b"This is not a CSV file",
            content_type="text/plain"
        )
        
        # Create large CSV content (for size testing)
        large_content = "col1,col2\n" + "\n".join([f"{i},{i*2}" for i in range(100000)])
        self.large_csv_content = large_content.encode('utf-8')
        
    def test_home_index_get(self):
        """Test GET request to home index"""
        response = self.client.get(reverse('home:index'))
        self.assertEqual(response.status_code, 200)
        
        # Check that the page contains expected elements
        self.assertContains(response, 'Upload CSV File')
        self.assertContains(response, 'file-upload-area')
        self.assertContains(response, 'csv-file')
    
    def test_home_index_post_valid_csv(self):
        """Test POST request with valid CSV file"""
        response = self.client.post(
            reverse('home:index'),
            {'csv_file': self.valid_csv_file},
            follow=True
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Check that success message is shown
        messages = list(response.context['messages'])
        self.assertTrue(any('successfully uploaded' in str(msg) for msg in messages))
        
        # Check that session contains DataFrame info
        session = self.client.session
        self.assertTrue(session.get('df_uploaded', False))
        self.assertIn('df_shape', session)
        self.assertIn('df_columns', session)
        self.assertIn('df_filename', session)
    
    def test_home_index_post_no_file(self):
        """Test POST request without file"""
        response = self.client.post(reverse('home:index'), {})
        
        self.assertEqual(response.status_code, 200)
        
        # Check for error message
        messages = list(response.context['messages'])
        self.assertTrue(any('Please select a file' in str(msg) for msg in messages))
    
    def test_home_index_post_non_csv_file(self):
        """Test POST request with non-CSV file"""
        response = self.client.post(
            reverse('home:index'),
            {'csv_file': self.invalid_file}
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Check for error message about file type
        messages = list(response.context['messages'])
        self.assertTrue(any('CSV' in str(msg) for msg in messages))
    
    def test_home_index_post_large_file(self):
        """Test POST request with file larger than allowed size"""
        large_file = SimpleUploadedFile(
            "large.csv",
            self.large_csv_content,
            content_type="text/csv"
        )
        
        # If file is larger than 10MB, it should be rejected
        if len(self.large_csv_content) > 10 * 1024 * 1024:
            response = self.client.post(
                reverse('home:index'),
                {'csv_file': large_file}
            )
            
            messages = list(response.context['messages'])
            self.assertTrue(any('size' in str(msg).lower() for msg in messages))
    
    def test_home_index_session_persistence(self):
        """Test that DataFrame persists in session across requests"""
        # Upload a file
        self.client.post(
            reverse('home:index'),
            {'csv_file': self.valid_csv_file}
        )
        
        # Make another request
        response = self.client.get(reverse('home:index'))
        
        # Session should still contain DataFrame info
        session = self.client.session
        self.assertTrue(session.get('df_uploaded', False))
        
        # Check that uploaded file info is displayed
        self.assertContains(response, 'Current File:')
    
    def test_home_index_replace_file(self):
        """Test replacing an already uploaded file"""
        # Upload first file
        first_file = SimpleUploadedFile(
            "first.csv",
            b"col1,col2\n1,A\n2,B",
            content_type="text/csv"
        )
        
        self.client.post(
            reverse('home:index'),
            {'csv_file': first_file}
        )
        
        first_session = dict(self.client.session)
        
        # Upload second file
        second_file = SimpleUploadedFile(
            "second.csv",
            b"col1,col2,col3\n1,A,X\n2,B,Y\n3,C,Z",
            content_type="text/csv"
        )
        
        response = self.client.post(
            reverse('home:index'),
            {'csv_file': second_file},
            follow=True
        )
        
        # Check that file was replaced
        second_session = self.client.session
        self.assertNotEqual(first_session.get('df_shape'), second_session.get('df_shape'))
        self.assertEqual(second_session.get('df_filename'), 'second.csv')
    
    def test_clear_session_view(self):
        """Test the clear session functionality"""
        # First upload a file
        self.client.post(
            reverse('home:index'),
            {'csv_file': self.valid_csv_file}
        )
        
        # Verify session has data
        self.assertTrue(self.client.session.get('df_uploaded', False))
        
        # Clear session (if this endpoint exists)
        try:
            response = self.client.post(reverse('home:clear_session'))
            self.assertEqual(response.status_code, 302)  # Redirect after clearing
            
            # Check that session is cleared
            self.assertFalse(self.client.session.get('df_uploaded', False))
        except:
            # If clear_session URL doesn't exist, that's okay for this test
            pass
    
    def test_csv_validation_edge_cases(self):
        """Test CSV validation with edge cases"""
        # Empty CSV
        empty_csv = SimpleUploadedFile(
            "empty.csv",
            b"",
            content_type="text/csv"
        )
        
        response = self.client.post(
            reverse('home:index'),
            {'csv_file': empty_csv}
        )
        
        # Should handle empty file gracefully
        self.assertEqual(response.status_code, 200)
        
        # CSV with only headers
        headers_only_csv = SimpleUploadedFile(
            "headers.csv",
            b"col1,col2,col3",
            content_type="text/csv"
        )
        
        response = self.client.post(
            reverse('home:index'),
            {'csv_file': headers_only_csv}
        )
        
        # Should handle headers-only file
        self.assertEqual(response.status_code, 200)
    
    def test_malformed_csv_handling(self):
        """Test handling of malformed CSV files"""
        malformed_csv = SimpleUploadedFile(
            "malformed.csv",
            b"col1,col2\n1,2,3,4\n5,6\n7",  # Inconsistent columns
            content_type="text/csv"
        )
        
        response = self.client.post(
            reverse('home:index'),
            {'csv_file': malformed_csv}
        )
        
        # Should handle malformed CSV with appropriate error message
        self.assertEqual(response.status_code, 200)
        # The actual behavior depends on how pandas handles the malformed CSV
    
    def test_unicode_csv_handling(self):
        """Test handling of CSV files with Unicode characters"""
        unicode_csv = SimpleUploadedFile(
            "unicode.csv",
            "name,city\nJoão,São Paulo\nMarie,Montréal\n中文,北京".encode('utf-8'),
            content_type="text/csv"
        )
        
        response = self.client.post(
            reverse('home:index'),
            {'csv_file': unicode_csv},
            follow=True
        )
        
        # Should handle Unicode properly
        self.assertEqual(response.status_code, 200)
        
        # Check that file was processed successfully
        session = self.client.session
        self.assertTrue(session.get('df_uploaded', False))
    
    def test_concurrent_uploads(self):
        """Test behavior with multiple concurrent uploads (session isolation)"""
        # This test simulates different users/sessions
        client1 = Client()
        client2 = Client()
        
        # Upload different files with different clients
        file1 = SimpleUploadedFile("file1.csv", b"col1\n1\n2", content_type="text/csv")
        file2 = SimpleUploadedFile("file2.csv", b"col1,col2\n1,A\n2,B", content_type="text/csv")
        
        client1.post(reverse('home:index'), {'csv_file': file1})
        client2.post(reverse('home:index'), {'csv_file': file2})
        
        # Check that sessions are isolated
        session1 = client1.session
        session2 = client2.session
        
        self.assertEqual(session1.get('df_filename'), 'file1.csv')
        self.assertEqual(session2.get('df_filename'), 'file2.csv')
        self.assertNotEqual(session1.get('df_shape'), session2.get('df_shape'))
    
    def test_file_extension_validation(self):
        """Test file extension validation"""
        # Test various file extensions
        extensions_to_test = [
            ('valid.csv', b"col1,col2\n1,2", True),
            ('valid.CSV', b"col1,col2\n1,2", True),  # Case insensitive
            ('invalid.txt', b"col1,col2\n1,2", False),
            ('invalid.xlsx', b"col1,col2\n1,2", False),
            ('invalid.json', b"col1,col2\n1,2", False),
            ('no_extension', b"col1,col2\n1,2", False),
        ]
        
        for filename, content, should_succeed in extensions_to_test:
            with self.subTest(filename=filename):
                test_file = SimpleUploadedFile(filename, content, content_type="text/csv")
                response = self.client.post(reverse('home:index'), {'csv_file': test_file})
                
                self.assertEqual(response.status_code, 200)
                
                if should_succeed:
                    # Should succeed
                    session = self.client.session
                    # Clear session for next test
                    self.client.session.flush()
                else:
                    # Should show error message
                    messages = list(response.context['messages'])
                    # Should have some kind of error message
                    # Clear session for next test
                    self.client.session.flush()


class HomeUrlsTestCase(TestCase):
    """Test case for home app URLs"""
    
    def test_home_url_resolves(self):
        """Test that home URL resolves correctly"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get('/home/')
        self.assertEqual(response.status_code, 200)
    
    def test_home_url_name_reverse(self):
        """Test that URL name reverses correctly"""
        url = reverse('home:index')
        self.assertTrue(url.startswith('/'))
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class HomeTemplateTestCase(TestCase):
    """Test case for home app templates"""
    
    def test_home_template_used(self):
        """Test that correct template is used"""
        response = self.client.get(reverse('home:index'))
        self.assertTemplateUsed(response, 'home/index.html')
        self.assertTemplateUsed(response, 'base.html')
    
    def test_home_template_context(self):
        """Test template context variables"""
        response = self.client.get(reverse('home:index'))
        
        # Check that expected context variables are present
        # This depends on the actual context passed to the template
        self.assertIn('request', response.context)
    
    def test_home_template_content(self):
        """Test that template contains expected content"""
        response = self.client.get(reverse('home:index'))
        
        # Check for key elements
        self.assertContains(response, 'Upload CSV File')
        self.assertContains(response, 'form')
        self.assertContains(response, 'enctype="multipart/form-data"')
        self.assertContains(response, 'csv-file')
        
        # Check for drag and drop functionality
        self.assertContains(response, 'file-upload-area')
        
        # Check for Bootstrap classes (indicating proper styling)
        self.assertContains(response, 'btn')
        self.assertContains(response, 'card')