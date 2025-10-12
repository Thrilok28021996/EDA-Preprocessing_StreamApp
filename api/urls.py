from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views

app_name = 'api'

urlpatterns = [
    # Authentication endpoints
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Health check
    path('health/', views.health_check, name='health_check'),
    
    # File operations
    path('upload/', views.upload_file, name='upload_file'),
    path('dataframe/info/', views.get_dataframe_info_api, name='get_dataframe_info'),
    path('dataframe/reset/', views.reset_data, name='reset_data'),
    
    # EDA operations
    path('chart/generate/', views.generate_chart_api, name='generate_chart'),
    path('analysis/perform/', views.perform_analysis_api, name='perform_analysis'),
    
    # Preprocessing operations
    path('preprocessing/apply/', views.apply_preprocessing, name='apply_preprocessing'),
    path('preprocessing/column-values/', views.get_column_values, name='get_column_values'),
    
    # Export operations
    path('export/<str:format>/', views.export_data, name='export_data'),
]