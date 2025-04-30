from django.contrib import admin
from .models import Hostel, Room, Amenity, HostelImage, RoomImage

# Register your models here.
admin.site.register(Hostel)
admin.site.register(Room)
admin.site.register(Amenity)
admin.site.register(HostelImage)
admin.site.register(RoomImage)
