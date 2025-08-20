from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'tasks', views.TaskViewSet, basename='task')

# Define URL patterns
urlpatterns = [
    # API endpoints from router
    path('api/', include(router.urls)),

    # Authentication endpoints
    path('api/auth/register/', views.register_user, name='auth-register'),
    path('api/auth/login/', views.login_user, name='auth-login'),
    path('api/auth/logout/', views.logout_user, name='auth-logout'),
    path('api/auth/profile/', views.user_profile, name='auth-profile'),

    # Dashboard endpoints
    path('api/dashboard/', views.dashboard_summary, name='dashboard-summary'),
]
