from django.shortcuts import render
from rest_framework import viewsets, filters, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import Hostel, Room, Amenity, HostelImage, RoomImage
from .serializers import (
    HostelSerializer, HostelDetailSerializer, RoomSerializer, 
    RoomDetailSerializer, AmenitySerializer,
    HostelImageSerializer, RoomImageSerializer
)


class AmenityViewSet(viewsets.ModelViewSet):
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    permission_classes = [permissions.AllowAny]


class HostelViewSet(viewsets.ModelViewSet):
    queryset = Hostel.objects.all()
    serializer_class = HostelSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['gender', 'location']
    search_fields = ['name', 'description', 'location']
    ordering_fields = ['name', 'capacity']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return HostelDetailSerializer
        return HostelSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['hostel', 'room_type', 'is_available', 'floor']
    search_fields = ['room_number', 'description']
    ordering_fields = ['price', 'room_number']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RoomDetailSerializer
        return RoomSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]


class HostelImageViewSet(viewsets.ModelViewSet):
    queryset = HostelImage.objects.all()
    serializer_class = HostelImageSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['hostel', 'is_primary']


class RoomImageViewSet(viewsets.ModelViewSet):
    queryset = RoomImage.objects.all()
    serializer_class = RoomImageSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['room', 'is_primary']
