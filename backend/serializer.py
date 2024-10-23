from rest_framework import serializers
from api.models import Procedimiento

class ImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Procedimiento
        fields = ['Diagrama_Flujo','image_url']

    def get_image_url(self, obj):
        return obj.Diagrama_Flujo.url if obj.Diagrama_Flujo else None
