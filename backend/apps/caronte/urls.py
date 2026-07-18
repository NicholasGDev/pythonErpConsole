# backend/apps/caronte/urls.py
from django.urls import path
from apps.caronte.views import (
    LoginView, RefreshView, LogoutView, InvalidateAllTokensView,
    UserListView, UserDetailView,
)

urlpatterns = [
    # Auth
    path('auth/login/',            LoginView.as_view(),             name='auth-login'),
    path('auth/refresh/',          RefreshView.as_view(),           name='auth-refresh'),
    path('auth/logout/',           LogoutView.as_view(),            name='auth-logout'),
    path('auth/invalidate-tokens/', InvalidateAllTokensView.as_view(), name='auth-invalidate'),

    # Users
    path('users/',                 UserListView.as_view(),          name='user-list'),
    path('users/<int:user_id>/',   UserDetailView.as_view(),        name='user-detail'),
]