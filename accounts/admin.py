from django.contrib import admin
from .models import User, Student, EmergencyContact

# Register your models here.
admin.site.register(User)
admin.site.register(Student)
admin.site.register(EmergencyContact)
