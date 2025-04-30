from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('Student', 'Student'),
        ('Staff', 'Staff'),
        ('Admin', 'Admin'),
    ]
    
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"


class Student(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    
    LEVEL_CHOICES = [
        ('100', '100 Level'),
        ('200', '200 Level'),
        ('300', '300 Level'),
        ('400', '400 Level'),
        ('500', '500 Level'),
        ('PG', 'Postgraduate'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    matric_number = models.CharField(max_length=20, unique=True)
    faculty = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    level = models.CharField(max_length=3, choices=LEVEL_CHOICES)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    guardian_name = models.CharField(max_length=100, blank=True)
    guardian_phone = models.CharField(max_length=15, blank=True)
    guardian_email = models.EmailField(blank=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.matric_number})"


class EmergencyContact(models.Model):
    student = models.OneToOneField(Student, related_name='emergency_contact', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.name} - Contact for {self.student.matric_number}"
