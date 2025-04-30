from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import RegisterView, UserViewSet, StudentViewSet, EmergencyContactViewSet

# Create a router for viewsets
router = DefaultRouter()
router.register('users', UserViewSet)
router.register('students', StudentViewSet)
router.register('emergency-contacts', EmergencyContactViewSet)

urlpatterns = [
    # Registration endpoint
    path('register/', RegisterView.as_view(), name='register'),
]

# Add router URLs to urlpatterns
urlpatterns += router.urls 