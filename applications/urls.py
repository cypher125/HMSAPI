from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from .views import ApplicationViewSet, PaymentViewSet

# Main router
router = DefaultRouter()
router.register('applications', ApplicationViewSet, basename='applications')

# Nested router for payments under applications
applications_router = NestedDefaultRouter(router, 'applications', lookup='application')
applications_router.register('payments', PaymentViewSet, basename='application-payments')

urlpatterns = []

# Add router URLs to urlpatterns
urlpatterns += router.urls
urlpatterns += applications_router.urls 