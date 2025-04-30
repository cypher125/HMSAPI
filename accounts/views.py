from django.shortcuts import render
from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User, Student, EmergencyContact
from .serializers import (
    UserSerializer, UserCreateSerializer, StudentSerializer, 
    StudentDetailSerializer, EmergencyContactSerializer
)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserCreateSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return StudentDetailSerializer
        return StudentSerializer
    
    @action(detail=False, methods=['get'])
    def my_profile(self, request):
        try:
            student = Student.objects.get(user=request.user)
            serializer = StudentDetailSerializer(student)
            return Response(serializer.data)
        except Student.DoesNotExist:
            return Response(
                {"detail": "Student profile not found for this user."},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """Update or create the student profile for the current user."""
        user = request.user
        
        # Check if student profile exists
        student, created = Student.objects.get_or_create(user=user)
        
        # Use StudentSerializer for the update
        serializer = StudentSerializer(student, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            # Return the detailed representation
            detailed_serializer = StudentDetailSerializer(student)
            return Response(detailed_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmergencyContactViewSet(viewsets.ModelViewSet):
    queryset = EmergencyContact.objects.all()
    serializer_class = EmergencyContactSerializer
    
    def get_queryset(self):
        # Only allow users to see their own emergency contacts
        if self.request.user.is_staff:
            return EmergencyContact.objects.all()
        return EmergencyContact.objects.filter(student__user=self.request.user)
