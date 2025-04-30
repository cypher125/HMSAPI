from django.db import models
from django.utils.text import slugify


class Amenity(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True)  # For frontend icon reference
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Amenities"


class Hostel(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male Only'),
        ('Female', 'Female Only'),
        ('Mixed', 'Mixed'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
    capacity = models.PositiveIntegerField()
    image = models.ImageField(upload_to='hostel_images/', blank=True, null=True)
    warden_name = models.CharField(max_length=100, blank=True)
    warden_phone = models.CharField(max_length=15, blank=True)
    warden_email = models.EmailField(blank=True)
    facilities = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def available_rooms(self):
        return self.rooms.filter(is_available=True).count()
    
    @property
    def total_rooms(self):
        return self.rooms.count()


class HostelImage(models.Model):
    hostel = models.ForeignKey(Hostel, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='hostels/')
    is_primary = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Image for {self.hostel.name}"


class Room(models.Model):
    ROOM_TYPE_CHOICES = [
        ('Single', 'Single'),
        ('Double', 'Double'),
        ('Triple', 'Triple'),
        ('Quad', 'Quad'),
    ]
    
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=10)
    floor = models.CharField(max_length=10)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPE_CHOICES)
    capacity = models.PositiveSmallIntegerField()
    is_available = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    facilities = models.TextField(blank=True)
    image = models.ImageField(upload_to='room_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['hostel', 'room_number']
        ordering = ['hostel', 'room_number']
    
    def __str__(self):
        return f"{self.hostel.name} - Room {self.room_number}"
    
    @property
    def occupied_beds(self):
        return self.applications.filter(status='Approved').count()
    
    @property
    def available_beds(self):
        return self.capacity - self.occupied_beds
    
    @property
    def is_full(self):
        return self.occupied_beds >= self.capacity


class RoomImage(models.Model):
    room = models.ForeignKey(Room, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='rooms/')
    is_primary = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Image for {self.room.room_number} in {self.room.hostel.name}"
