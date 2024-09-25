from django.urls import path

from . import views

urlpatterns = [
    path("links/", views.ListLinkView.as_view(), name="link-list"),
    path("links/<int:id>/", views.LinkView.as_view(), name="link-detail"),
]