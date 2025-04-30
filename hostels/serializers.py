from rest_framework import serializers
from .models import Hostel, Room, Amenity, HostelImage, RoomImage


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = '__all__'


class HostelImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelImage
        fields = '__all__'


class RoomImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomImage
        fields = '__all__'


class RoomSerializer(serializers.ModelSerializer):
    images = RoomImageSerializer(many=True, read_only=True)
    available_beds = serializers.ReadOnlyField()
    is_full = serializers.ReadOnlyField()
    
    class Meta:
        model = Room
        fields = '__all__'
        read_only_fields = ['hostel']


class RoomDetailSerializer(serializers.ModelSerializer):
    images = RoomImageSerializer(many=True, read_only=True)
    available_beds = serializers.ReadOnlyField()
    is_full = serializers.ReadOnlyField()
    occupied_beds = serializers.ReadOnlyField()
    
    class Meta:
        model = Room
        fields = '__all__'


class HostelSerializer(serializers.ModelSerializer):
    images = HostelImageSerializer(many=True, read_only=True)
    available_rooms = serializers.ReadOnlyField()
    total_rooms = serializers.ReadOnlyField()
    
    class Meta:
        model = Hostel
        fields = '__all__'


class HostelDetailSerializer(serializers.ModelSerializer):
    images = HostelImageSerializer(many=True, read_only=True)
    rooms = RoomSerializer(many=True, read_only=True)
    available_rooms = serializers.ReadOnlyField()
    total_rooms = serializers.ReadOnlyField()
    
    class Meta:
        model = Hostel
        fields = '__all__' 