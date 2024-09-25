from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, response, status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

from . import models, serializers, permissions, services


@method_decorator(name="get", decorator=swagger_auto_schema(tags=["link"]))
@method_decorator(name="post", decorator=swagger_auto_schema(tags=["link"]))
class ListLinkView(generics.ListCreateAPIView):
    """List link and create link endpoint"""

    queryset = models.Link.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return serializers.CreateLinkSerializer
        elif self.request.method == "GET":
            return serializers.LinkSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        services.add_data_to_serializer_data(serializer)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


@method_decorator(name="get", decorator=swagger_auto_schema(tags=["link"]))
@method_decorator(name="put", decorator=swagger_auto_schema(tags=["link"]))
@method_decorator(name="patch", decorator=swagger_auto_schema(tags=["link"]))
@method_decorator(name="delete", decorator=swagger_auto_schema(tags=["link"]))
class LinkView(generics.RetrieveUpdateDestroyAPIView):
    """Link endpoint"""

    queryset = models.Link.objects.all()
    # lookup_field = "id"

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH", "POST"):
            return serializers.UpdateLinkSerializer
        elif self.request.method == "GET":
            return serializers.LinkSerializer
    
    def get_permissions(self):
        permission_list = [IsAuthenticated]
        
        if self.request.method in ("PUT", "PATCH", "POST"):
            permission_list.append(permissions.IsOwner)
        
        return [permission() for permission in self.permission_classes]
