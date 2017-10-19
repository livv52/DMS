from rest_framework import serializers

from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    documents = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='document-detail'
    )

    class Meta:
        model = Document
        fields = (
        'pk', 'name', 'owner', 'type', 'keywords', 'description', 'user', 'creation_time', 'status', 'path', 'folder')
