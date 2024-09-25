from rest_framework import serializers

from . import models


class BaseCollectionSerializer(serializers.ModelSerializer):
    """Base collection serializer"""

    class Meta:
        model = models.Collection
        fields = ("id", "name", "description", "created_in", "updated_in")


class BaseLinkSerializer(serializers.ModelSerializer):
    """Base link serializer"""

    class Meta:
        model = models.Link
        fields = ("id", "title", "description", "link", "image", "type_of_link", 
                  "created_in", "updated_in")


class ListLinkSerializer(serializers.ModelSerializer):
    """List link serializer"""

    class Meta:
        model = models.Link
        fields = ["title", "description", "link", "image", "collections", "created_in", "updated_in"]


class CreateLinkSerializer(serializers.ModelSerializer):
    """Create link serializer"""

    class Meta:
        model = models.Link
        fields = ["link"]


class LinkSerializer(serializers.ModelSerializer):
    """Link serializer"""

    collections = BaseCollectionSerializer(many=True)

    class Meta:
        model = models.Link
        fields = ("id", "title", "description", "link", "image", "type_of_link", 
                  "created_in", "updated_in", "collections")


class UpdateLinkSerializer(serializers.ModelSerializer):
    """Update link serializer"""

    class Meta:
        model = models.Link
        fields = ["title", "description", "image", "collections"]


class CollectionSerializer(serializers.ModelSerializer):
    """Collection serializer"""

    links = BaseLinkSerializer(many=True)

    class Meta:
        model = models.Collection
        fields = ("id", "name", "description", "created_in", "updated_in", "links")


class CreateCollectionSerializer(serializers.ModelSerializer):
    """Create collection serializer"""

    class Meta:
        model = models.Collection
        fields = ["name", "description"]


class UpdateCollectionSerializer(serializers.ModelSerializer):
    """Update collection serializer"""

    class Meta:
        model = models.Collection
        fields = ["name", "description"]