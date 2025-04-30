from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    HostelViewSet, RoomViewSet, AmenityViewSet,
    HostelImageViewSet, RoomImageViewSet
)

# Create a router for viewsets
router = DefaultRouter()
router.register('hostels', HostelViewSet)
router.register('rooms', RoomViewSet)
router.register('amenities', AmenityViewSet)
router.register('hostel-images', HostelImageViewSet)
router.register('room-images', RoomImageViewSet)

urlpatterns = []

# Add router URLs to urlpatterns
urlpatterns += router.urls 