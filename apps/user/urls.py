from django.urls import path

from . import views

urlpatterns = [
    path('sign-in/', views.SignInView.as_view(), name='sign-in'),
    path('sign-up/', views.SignUpView.as_view(), name='sign-up'),
    path('sign-out/', views.SignOutView.as_view(), name='sign-out'),
    path("profile/try_to_reset_password/", views.TryToResetPasswordView.as_view(), name="try-to-reset-password"),
    path("profile/<slug:username>/", views.ProfileView.as_view(), name="user-detail"),
    path("token/refresh/", views.RefreshTokenView.as_view(), name="refresh-tokens"),
    path("reset_password/<str:email>/<str:secret_key>/", views.ResetPasswordView.as_view(), name="reset-password"),
    path("profile/<slug:username>/change_password/", views.ChangePasswordView.as_view(), name="change-password"),
]