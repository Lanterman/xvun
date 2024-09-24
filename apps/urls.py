from django.urls import path, include


urlpatterns = [
    path("", include("apps.main.urls")),
    path("auth/", include("apps.user.urls"))
]