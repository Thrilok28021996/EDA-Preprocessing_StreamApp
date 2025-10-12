from rest_framework import serializers
from django.core.files.uploadedfile import InMemoryUploadedFile
import pandas as pd
import json


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    
    def validate_file(self, value):
        if not value.name.endswith('.csv'):
            raise serializers.ValidationError("Only CSV files are allowed.")
        if value.size > 10 * 1024 * 1024:  # 10MB limit
            raise serializers.ValidationError("File size cannot exceed 10MB.")
        return value


class ChartGenerationSerializer(serializers.Serializer):
    chart_type = serializers.ChoiceField(choices=[
        'bar', 'line', 'histogram', 'pie', 'scatter', 'box', 'heatmap', 'area'
    ])
    x_column = serializers.CharField(required=False, allow_blank=True)
    y_column = serializers.CharField(required=False, allow_blank=True)
    color_column = serializers.CharField(required=False, allow_blank=True)


class AnalysisSerializer(serializers.Serializer):
    analysis_type = serializers.ChoiceField(choices=[
        'show_data', 'missing_values', 'duplicates', 'outliers', 'data_types', 'column_stats'
    ])


class PreprocessingSerializer(serializers.Serializer):
    operation = serializers.ChoiceField(choices=[
        'select_columns', 'drop_columns', 'replace_values', 'remove_duplicates',
        'handle_missing_values', 'filter_data', 'reset_data'
    ])
    columns = serializers.ListField(child=serializers.CharField(), required=False)
    column = serializers.CharField(required=False)
    old_value = serializers.CharField(required=False, allow_blank=True)
    new_value = serializers.CharField(required=False, allow_blank=True)
    missing_strategy = serializers.ChoiceField(
        choices=['drop', 'fill_mean', 'fill_median', 'fill_mode', 'fill_value'],
        required=False
    )
    fill_value = serializers.CharField(required=False, allow_blank=True)
    filter_conditions = serializers.JSONField(required=False)


class DataFrameInfoSerializer(serializers.Serializer):
    shape = serializers.ListField(child=serializers.IntegerField())
    columns = serializers.ListField(child=serializers.CharField())
    dtypes = serializers.DictField()
    memory_usage = serializers.CharField()
    null_counts = serializers.DictField()


class ChartDataSerializer(serializers.Serializer):
    chart_html = serializers.CharField()
    chart_config = serializers.JSONField()


class AnalysisResultSerializer(serializers.Serializer):
    analysis_type = serializers.CharField()
    result = serializers.JSONField()


class ExportSerializer(serializers.Serializer):
    format = serializers.ChoiceField(choices=['csv', 'json', 'excel'])