from django.urls import path
from . import views

app_name = 'preprocessing'

urlpatterns = [
    path('', views.index, name='index'),
    path('apply/', views.apply_preprocessing, name='apply_preprocessing'),
    path('export/<str:format>/', views.export_data, name='export_data'),
    path('get-column-values/', views.get_column_values, name='get_column_values'),
    path('preview/', views.preview_operation, name='preview_operation'),
]