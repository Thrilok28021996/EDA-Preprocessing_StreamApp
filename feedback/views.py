from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_http_methods
import json
import datetime
import logging

# Configure logging
logger = logging.getLogger(__name__)

# SECURITY FIX #5 & #12: Import sanitization utilities
from security_utils import (
    sanitize_email,
    sanitize_text_input,
    log_security_event,
    rate_limit
)


def index(request):
    """Feedback page with contact form"""
    context = {
        'info': {
            'Name': 'Thrilok',
            'Full_Name': 'Thrilok E',
            'Email': 'thriloke96@gmail.com',
            'Github': 'https://github.com/Thrilok28021996',
            'City': 'AndhraPradesh, India',
        }
    }
    return render(request, 'feedback/index.html', context)


@rate_limit(limit=5, window=300)  # SECURITY FIX #10: 5 submissions per 5 minutes
def submit_feedback(request):
    """Submit feedback with email notification

    SECURITY IMPROVEMENTS:
    - REMOVED @csrf_exempt - now uses proper CSRF protection
    - Added rate limiting (5 submissions per 5 minutes)
    - Input sanitization to prevent XSS and injection attacks
    - Email validation to prevent header injection
    - Security event logging
    """
    # CONSISTENCY FIX: Explicitly handle GET requests with proper error
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Only POST requests are allowed for feedback submission'
        }, status=200)  # Keep 200 status for frontend compatibility

    try:
        # Parse form data (could be JSON or form-encoded)
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST

        # SECURITY FIX #12: Sanitize all inputs
        try:
            name = sanitize_text_input(data.get('name', ''), max_length=100)
            email = sanitize_email(data.get('email', ''))
            message = sanitize_text_input(data.get('message', ''), max_length=5000)
            subject = sanitize_text_input(data.get('subject', 'EDA App Feedback'), max_length=200)
        except Exception as e:
            log_security_event('feedback_validation_failed', request, {
                'error': str(e)
            })
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

        # Validate required fields
        if not all([name, email, message]):
            return JsonResponse({
                'success': False,
                'error': 'Please fill in all required fields (Name, Email, Message)'
            })
        
        # Prepare email content
        email_subject = f"[EDA App Feedback] {subject}"
        email_body = f"""
New feedback received from EDA & Preprocessing Web Application:

From: {name}
Email: {email}
Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Subject: {subject}

Message:
{message}

---
This feedback was submitted through the EDA & Preprocessing Django Web Application.
        """.strip()
        
        # Try to send email (configured for development)
        try:
            # For development, we'll use console backend or simple SMTP
            recipient_email = 'thriloke96@gmail.com'
            
            send_mail(
                email_subject,
                email_body,
                settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@edaapp.com',
                [recipient_email],
                fail_silently=False,
            )
            
            # Store feedback in session for developer reference (since we don't have a database model)
            if 'feedback_submissions' not in request.session:
                request.session['feedback_submissions'] = []
            
            feedback_entry = {
                'name': name,
                'email': email,
                'subject': subject,
                'message': message,
                'timestamp': datetime.datetime.now().isoformat(),
                'ip_address': get_client_ip(request)
            }

            request.session['feedback_submissions'].append(feedback_entry)
            request.session.modified = True

            # SECURITY FIX #17: Log feedback submission
            log_security_event('feedback_submitted', request, {
                'name': name,
                'email': email,
                'subject': subject
            })

            # Success response
            return JsonResponse({
                'success': True,
                'message': 'Thank you for your feedback! Your message has been sent successfully.'
            })
        
        except Exception as email_error:
            # Email failed, but still store the feedback
            logger.warning(f"Email sending failed: {email_error}")
            
            # Store feedback locally even if email fails
            if 'feedback_submissions' not in request.session:
                request.session['feedback_submissions'] = []
            
            feedback_entry = {
                'name': name,
                'email': email,
                'subject': subject,
                'message': message,
                'timestamp': datetime.datetime.now().isoformat(),
                'ip_address': get_client_ip(request),
                'email_sent': False,
                'email_error': str(email_error)
            }
            
            request.session['feedback_submissions'].append(feedback_entry)
            request.session.modified = True
            
            return JsonResponse({
                'success': True, 
                'message': 'Thank you for your feedback! Your message has been recorded successfully.',
                'note': 'Email notification may not be configured in development mode.'
            })
    
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': f'Error processing feedback: {str(e)}'
        })


def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
