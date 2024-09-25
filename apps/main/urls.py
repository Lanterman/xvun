from django.urls import path

from . import views

urlpatterns = [
    path("links/", views.ListLinkView.as_view(), name="link-list"),
    path("links/<int:id>/", views.LinkView.as_view(), name="link-detail"),
    path("collections/", views.CollectionsView.as_view(), name="collection-list"),
    path("collections/<int:id>", views.CollectionView.as_view(), name="collection-detail"),
]