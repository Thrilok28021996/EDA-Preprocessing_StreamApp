from django.urls import path
from . import views

app_name = 'eda'

urlpatterns = [
    path('', views.index, name='index'),
    path('generate-chart/', views.generate_chart, name='generate_chart'),
    path('analyze/', views.analyze_data, name='analyze_data'),
]