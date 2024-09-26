from urllib.error import HTTPError

from django.db.models import Count
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, response, status, decorators, exceptions
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

from . import models, serializers, permissions, services, add_test_data
from apps.user.models import User


@method_decorator(name="get", decorator=swagger_auto_schema(tags=["link"]))
@method_decorator(name="post", decorator=swagger_auto_schema(tags=["link"]))
class ListLinkView(generics.ListCreateAPIView):
    """List link and create link endpoint"""

    queryset = models.Link.objects.all().prefetch_related("collections")
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return serializers.CreateLinkSerializer
        elif self.request.method == "GET":
            return serializers.LinkSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            serializer = services.add_data_by_link(serializer, request.user)
        except HTTPError:
            raise exceptions.PermissionDenied("This site has prohibited this action")
    
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


@method_decorator(name="get", decorator=swagger_auto_schema(tags=["link"]))
@method_decorator(name="put", decorator=swagger_auto_schema(tags=["link"]))
@method_decorator(name="patch", decorator=swagger_auto_schema(tags=["link"]))
@method_decorator(name="delete", decorator=swagger_auto_schema(tags=["link"]))
class LinkView(generics.RetrieveUpdateDestroyAPIView):
    """Link endpoint"""

    queryset = models.Link.objects.all().prefetch_related("collections")
    lookup_field = "id"

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH", "POST"):
            return serializers.UpdateLinkSerializer
        elif self.request.method == "GET":
            return serializers.LinkSerializer
    
    def get_permissions(self):
        permission_list = [IsAuthenticated]
        
        if self.request.method in ("PUT", "PATCH", "POST", "DELETE"):
            permission_list.append(permissions.IsOwner)
        
        return [permission() for permission in permission_list]
    
    def perform_update(self, serializer):
        serializer.save(updated_in = timezone.now())
 


@method_decorator(name="get", decorator=swagger_auto_schema(tags=["collection"]))
@method_decorator(name="post", decorator=swagger_auto_schema(tags=["collection"]))
class CollectionsView(generics.ListCreateAPIView):
    """List and create collections endpoint"""

    queryset = models.Collection.objects.all().prefetch_related("links")
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return serializers.CreateCollectionSerializer
        elif self.request.method == "GET":
            return serializers.CollectionSerializer
    
    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user)


@method_decorator(name="get", decorator=swagger_auto_schema(tags=["collection"]))
@method_decorator(name="put", decorator=swagger_auto_schema(tags=["collection"]))
@method_decorator(name="patch", decorator=swagger_auto_schema(tags=["collection"]))
@method_decorator(name="delete", decorator=swagger_auto_schema(tags=["collection"]))
class CollectionView(generics.RetrieveUpdateDestroyAPIView):
    """Collection endpoint"""

    queryset = models.Collection.objects.all().prefetch_related("links")
    lookup_field = "id"

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH", "POST"):
            return serializers.UpdateCollectionSerializer
        elif self.request.method == "GET":
            return serializers.CollectionSerializer
    
    def get_permissions(self):
        permission_list = [IsAuthenticated]
        
        if self.request.method in ("PUT", "PATCH", "POST", "DELETE"):
            permission_list.append(permissions.IsOwner)
        
        return [permission() for permission in permission_list]
    
    def perform_update(self, serializer):
        serializer.save(updated_in = timezone.now())


@decorators.api_view(["GET"])
def add_test_data_for_testing(request):
    """Add test data for testing the project"""

    add_test_data.add_test_data()
    return response.Response({"detail": "Test data added successfully."})


@decorators.api_view(["GET"])
def sql_request(request):
    """SQL request"""

    users = User.objects.all().prefetch_related("link_set").annotate(count_links=Count("link_set")).order_by(
        "-count_links", "created_in")[:10]
    
    serializer = serializers.SQLRequestSerializer(users, many=True)
    return response.Response(serializer.data)