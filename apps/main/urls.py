from django.urls import path

from . import views

urlpatterns = [
    path("asql_request/", views.sql_request, name="sql-request"),
    path("add_test_data/", views.add_test_data_for_testing, name="add-test-data"),
    path("links/", views.ListLinkView.as_view(), name="link-list"),
    path("links/<int:id>/", views.LinkView.as_view(), name="link-detail"),
    path("collections/", views.CollectionsView.as_view(), name="collection-list"),
    path("collections/<int:id>", views.CollectionView.as_view(), name="collection-detail"),
]