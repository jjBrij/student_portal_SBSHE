# website_content/serializers.py

from rest_framework import serializers
from .models import WebsiteContent, Menu

class WebsiteContentSerializer(serializers.ModelSerializer):
    """Serializer for Website Content"""
    menu_name = serializers.CharField(source='menu.name', read_only=True)
    file_url = serializers.SerializerMethodField()
    file_type = serializers.SerializerMethodField()
    
    class Meta:
        model = WebsiteContent
        fields = [
            'id',
            'menu',
            'menu_name',
            'name',
            'short_name',
            'serial_number',
            'file',
            'file_url',
            'file_type',
            'short_intro',
            'intro',
            'description',
            'date',
            'url_link',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None
    
    def get_file_type(self, obj):
        if obj.file:
            ext = obj.file.name.split('.')[-1].lower()
            allowed_types = ['pdf', 'doc', 'docx', 'ppt', 'pptx', 'jpg', 'jpeg', 'png', 'webp']
            if ext in allowed_types:
                return ext
        return None

class MenuSerializer(serializers.ModelSerializer):
    """Serializer for Menu"""
    class Meta:
        model = Menu
        fields = ['id', 'name', 'parent', 'is_active', 'created_at', 'updated_at']