from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.response import Response
from django.http import HttpResponse
import pandas as pd
import json
import io
from datetime import datetime

from .serializers import (
    FileUploadSerializer, ChartGenerationSerializer, AnalysisSerializer,
    PreprocessingSerializer, DataFrameInfoSerializer, ChartDataSerializer,
    AnalysisResultSerializer, ExportSerializer
)
from utils import (
    get_dataframe_info, generate_chart, perform_analysis,
    apply_preprocessing_operation, export_dataframe
)

# SECURITY FIX #4 & #6: Import secure utilities
from security_utils import (
    serialize_dataframe_to_json,
    deserialize_dataframe_from_json,
    validate_uploaded_file,
    log_security_event
)


# SECURITY FIX #6: Define custom rate throttle classes
class FileUploadThrottle(AnonRateThrottle):
    """Rate limiting for file uploads - 10 per hour"""
    rate = '10/hour'


class APIThrottle(AnonRateThrottle):
    """Rate limiting for general API calls - 100 per hour"""
    rate = '100/hour'


@api_view(['POST'])
@permission_classes([AllowAny])  # Keep AllowAny for now, but add throttling
@throttle_classes([FileUploadThrottle])  # SECURITY FIX #6: Add rate limiting
def upload_file(request):
    """Upload CSV file and store in session

    SECURITY IMPROVEMENTS:
    - Rate limited to 10 uploads per hour
    - Comprehensive file validation (MIME type, content, size)
    - Secure JSON serialization instead of pickle
    - Security event logging
    """
    try:
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data['file']

            # SECURITY FIX #8: Comprehensive file validation
            is_valid, error_message = validate_uploaded_file(
                file,
                allowed_extensions=['csv'],
                max_size_mb=10
            )

            if not is_valid:
                log_security_event('api_file_upload_rejected', request, {
                    'filename': file.name,
                    'reason': error_message
                })
                return Response({
                    'error': error_message
                }, status=status.HTTP_400_BAD_REQUEST)

            # Read CSV file
            df = pd.read_csv(file)

            # SECURITY FIX #4: Use secure JSON serialization instead of pickle
            df_json = serialize_dataframe_to_json(df)

            # Store in session
            request.session['dataframe'] = df_json
            request.session['original_dataframe'] = df_json
            request.session['file_uploaded'] = True
            request.session['upload_time'] = datetime.now().isoformat()
            request.session['filename'] = file.name

            # Log successful upload
            log_security_event('api_file_uploaded', request, {
                'filename': file.name,
                'size': file.size
            })

            # Get dataframe info
            info = get_dataframe_info(df)

            return Response({
                'message': 'File uploaded successfully',
                'filename': file.name,
                'dataframe_info': info
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        log_security_event('api_file_upload_error', request, {
            'error': str(e)
        })
        return Response({
            'error': 'Error processing file. Please check the file format and try again.'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
@throttle_classes([APIThrottle])  # SECURITY FIX #6: Add rate limiting
def get_dataframe_info_api(request):
    """Get current dataframe information

    SECURITY: Rate limited, secure deserialization
    """
    try:
        if 'dataframe' not in request.session:
            return Response({
                'error': 'No dataframe found. Please upload a file first.'
            }, status=status.HTTP_404_NOT_FOUND)

        # SECURITY FIX #4: Use secure JSON deserialization
        df_json = request.session['dataframe']
        df = deserialize_dataframe_from_json(df_json)
        info = get_dataframe_info(df)

        return Response({
            'dataframe_info': info,
            'filename': request.session.get('filename', 'Unknown'),
            'upload_time': request.session.get('upload_time')
        }, status=status.HTTP_200_OK)

    except Exception as e:
        # SECURITY FIX #14: Don't expose internal details in production
        return Response({
            'error': 'Error retrieving dataframe information.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([APIThrottle])  # SECURITY FIX #6
def generate_chart_api(request):
    """Generate interactive chart"""
    try:
        if 'dataframe' not in request.session:
            return Response({
                'error': 'No dataframe found. Please upload a file first.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ChartGenerationSerializer(data=request.data)
        if serializer.is_valid():
            # SECURITY FIX #4: Secure JSON deserialization
            df = deserialize_dataframe_from_json(request.session['dataframe'])
            
            chart_data = generate_chart(
                df=df,
                chart_type=serializer.validated_data['chart_type'],
                x_column=serializer.validated_data.get('x_column'),
                y_column=serializer.validated_data.get('y_column'),
                color_column=serializer.validated_data.get('color_column')
            )
            
            return Response({
                'chart_html': chart_data['chart_html'],
                'chart_config': chart_data.get('chart_config', {})
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({
            'error': f'Error generating chart: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([APIThrottle])  # SECURITY FIX #6
def perform_analysis_api(request):
    """Perform data analysis"""
    try:
        if 'dataframe' not in request.session:
            return Response({
                'error': 'No dataframe found. Please upload a file first.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = AnalysisSerializer(data=request.data)
        if serializer.is_valid():
            # SECURITY FIX #4: Secure JSON deserialization
            df = deserialize_dataframe_from_json(request.session['dataframe'])
            
            analysis_result = perform_analysis(
                df=df,
                analysis_type=serializer.validated_data['analysis_type']
            )
            
            return Response({
                'analysis_type': serializer.validated_data['analysis_type'],
                'result': analysis_result
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({
            'error': f'Error performing analysis: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([APIThrottle])  # SECURITY FIX #6
def apply_preprocessing(request):
    """Apply preprocessing operation"""
    try:
        if 'dataframe' not in request.session:
            return Response({
                'error': 'No dataframe found. Please upload a file first.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PreprocessingSerializer(data=request.data)
        if serializer.is_valid():
            # SECURITY FIX #4: Secure JSON deserialization
            df = deserialize_dataframe_from_json(request.session['dataframe'])

            # Apply preprocessing operation
            result = apply_preprocessing_operation(df, serializer.validated_data)

            if result['success']:
                # SECURITY FIX #4: Update session with secure JSON serialization
                request.session['dataframe'] = serialize_dataframe_to_json(result['dataframe'])
                
                # Get updated info
                info = get_dataframe_info(result['dataframe'])
                
                return Response({
                    'message': result['message'],
                    'dataframe_info': info
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': result['message']
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({
            'error': f'Error applying preprocessing: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
@throttle_classes([APIThrottle])  # SECURITY FIX #6
def get_column_values(request):
    """Get unique values for a column"""
    try:
        if 'dataframe' not in request.session:
            return Response({
                'error': 'No dataframe found. Please upload a file first.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        column = request.GET.get('column')
        if not column:
            return Response({
                'error': 'Column parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # SECURITY FIX #4: Secure JSON deserialization
        df = deserialize_dataframe_from_json(request.session['dataframe'])
        
        if column not in df.columns:
            return Response({
                'error': f'Column "{column}" not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        unique_values = df[column].unique().tolist()
        # Handle NaN values
        unique_values = [str(v) if pd.notna(v) else 'NaN' for v in unique_values]
        
        return Response({
            'column': column,
            'unique_values': unique_values[:100]  # Limit to 100 values
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'error': f'Error getting column values: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
@throttle_classes([APIThrottle])  # SECURITY FIX #6
def export_data(request, format):
    """Export dataframe in specified format"""
    try:
        if 'dataframe' not in request.session:
            return Response({
                'error': 'No dataframe found. Please upload a file first.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if format not in ['csv', 'json', 'excel']:
            return Response({
                'error': 'Invalid format. Supported formats: csv, json, excel'
            }, status=status.HTTP_400_BAD_REQUEST)

        # SECURITY FIX #4: Secure JSON deserialization
        df = deserialize_dataframe_from_json(request.session['dataframe'])
        filename = request.session.get('filename', 'processed_data')
        
        # Generate export file
        file_content, content_type, file_extension = export_dataframe(df, format)
        
        response = HttpResponse(file_content, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="processed_{filename}.{file_extension}"'
        
        return response
    
    except Exception as e:
        return Response({
            'error': f'Error exporting data: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([APIThrottle])  # SECURITY FIX #6
def reset_data(request):
    """Reset dataframe to original state"""
    try:
        if 'original_dataframe' not in request.session:
            return Response({
                'error': 'No original dataframe found. Please upload a file first.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Reset to original dataframe
        request.session['dataframe'] = request.session['original_dataframe']

        # SECURITY FIX #4: Secure JSON deserialization
        df = deserialize_dataframe_from_json(request.session['dataframe'])
        info = get_dataframe_info(df)
        
        return Response({
            'message': 'Data reset to original state successfully',
            'dataframe_info': info
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'error': f'Error resetting data: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])  
@permission_classes([AllowAny])
def health_check(request):
    """API health check endpoint"""
    return Response({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    }, status=status.HTTP_200_OK)
