from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, filters, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Sum, Q
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal
from .models import Application, Payment
from .serializers import (
    ApplicationSerializer, ApplicationDetailSerializer, 
    ApplicationCreateSerializer, PaymentSerializer,
    PaymentCreateSerializer
)
from hostels.models import Hostel, Room
from accounts.models import User, Student


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to view/edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Allow admin users
        if request.user.is_staff:
            return True
        
        # Check if the object has a student field (Application)
        if hasattr(obj, 'student'):
            return obj.student == request.user
        
        # Check if the object has an application field (Payment)
        if hasattr(obj, 'application'):
            return obj.application.student == request.user
        
        return False


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_status', 'room__hostel']
    ordering_fields = ['application_date', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ApplicationCreateSerializer
        elif self.action == 'retrieve':
            return ApplicationDetailSerializer
        return ApplicationSerializer
    
    def get_queryset(self):
        user = self.request.user
        # Admin can see all applications
        if user.is_staff:
            return Application.objects.all()
        # Regular users can only see their own applications
        return Application.objects.filter(student=user)
    
    @action(detail=False, methods=['get'])
    def my_applications(self, request):
        """Get all applications for the current user"""
        applications = Application.objects.filter(student=request.user)
        serializer = self.get_serializer(applications, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an application"""
        application = self.get_object()
        
        # Check if application can be cancelled
        if application.status not in ['Pending', 'Approved']:
            return Response(
                {"detail": "Cannot cancel this application."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        application.status = 'Cancelled'
        application.save()
        
        serializer = self.get_serializer(application)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """
        Get statistics for the admin dashboard:
        - Total students count
        - Gender distribution
        - Occupancy rate
        - Pending applications
        - Revenue statistics
        - Hostel occupancy data
        - Recent applications
        - Recent activities
        """
        if not request.user.is_staff:
            return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
            
        # Basic statistics
        total_students = User.objects.filter(user_type='Student').count()
        total_hostels = Hostel.objects.count()
        total_rooms = Room.objects.count()
        occupied_rooms = Room.objects.filter(is_available=False).count()
        occupancy_rate = round((occupied_rooms / total_rooms * 100)) if total_rooms > 0 else 0
        
        # Gender statistics
        male_students = Student.objects.filter(gender='Male').count()
        female_students = Student.objects.filter(gender='Female').count()
        gender_distribution = [
            {"name": "Male", "value": male_students, "fill": "#4F46E5"},
            {"name": "Female", "value": female_students, "fill": "#EC4899"}
        ]
        
        # Application statistics
        pending_applications = Application.objects.filter(status='Pending').count()
        approved_applications = Application.objects.filter(status='Approved').count()
        rejected_applications = Application.objects.filter(status='Rejected').count()
        
        # Financial statistics
        revenue_collected = Application.objects.aggregate(
            total=Coalesce(Sum('amount_paid'), Decimal('0'))
        )['total']
        outstanding_payments = Application.objects.filter(
            payment_status__in=['Unpaid', 'Partially Paid']
        ).aggregate(
            total=Coalesce(Sum('room__price'), Decimal('0')) - Coalesce(Sum('amount_paid'), Decimal('0'))
        )['total']
        
        # Hostel occupancy data
        hostel_occupancy = []
        for hostel in Hostel.objects.all():
            hostel_rooms = Room.objects.filter(hostel=hostel)
            total_rooms = hostel_rooms.count()
            occupied = hostel_rooms.filter(is_available=False).count()
            available = total_rooms - occupied
            
            hostel_occupancy.append({
                "name": hostel.name,
                "total": total_rooms,
                "occupied": occupied,
                "available": available,
            })
        
        # Recent applications (last 10)
        recent_apps = Application.objects.order_by('-application_date')[:10]
        recent_applications = []
        for app in recent_apps:
            # Ensure profile picture is a URL string, not binary data
            profile_pic = "/placeholder.svg?height=32&width=32"
            if hasattr(app.student, 'profile_picture') and app.student.profile_picture:
                # If it's a FileField or ImageField, get the URL
                if hasattr(app.student.profile_picture, 'url'):
                    profile_pic = app.student.profile_picture.url
                # Otherwise, ensure it's a string
                elif isinstance(app.student.profile_picture, str):
                    profile_pic = app.student.profile_picture
            
            recent_applications.append({
                "id": f"APP-{app.id}",
                "student": {
                    "name": app.student.get_full_name() or app.student.username,
                    "matricNumber": getattr(app.student.student, 'matric_number', 'N/A') if hasattr(app.student, 'student') else 'N/A',
                    "avatar": profile_pic
                },
                "hostel": app.room.hostel.name,
                "roomType": app.room.room_type,
                "dateApplied": app.application_date.strftime("%b %d, %Y"),
                "status": app.status.lower()
            })
        
        # Recent activities (last 7 days)
        activities = []
        
        # New applications
        recent_new_apps = Application.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).order_by('-created_at')[:5]
        
        for app in recent_new_apps:
            activities.append({
                "id": f"act-app-{app.id}",
                "action": "New application submitted",
                "user": app.student.get_full_name() or app.student.username,
                "time": self._get_time_ago(app.created_at),
                "icon": "FileText"
            })
        
        # Recent payments
        recent_payments = Payment.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7),
            status='Completed'
        ).order_by('-created_at')[:5]
        
        for payment in recent_payments:
            activities.append({
                "id": f"act-pay-{payment.id}",
                "action": "Payment received",
                "user": payment.application.student.get_full_name() or payment.application.student.username,
                "time": self._get_time_ago(payment.created_at),
                "icon": "CheckCircle2"
            })
        
        # Sort activities by time
        activities = sorted(activities, key=lambda x: self._parse_time_ago(x["time"]))[:5]
        
        return Response({
            "stats": {
                "totalStudents": total_students,
                "totalHostels": total_hostels,
                "totalRooms": total_rooms,
                "occupiedRooms": occupied_rooms,
                "pendingApplications": pending_applications,
                "approvedApplications": approved_applications,
                "rejectedApplications": rejected_applications,
                "maleStudents": male_students,
                "femaleStudents": female_students,
                "occupancyRate": occupancy_rate,
                "revenueCollected": f"NGN {revenue_collected:,.2f}",
                "outstandingPayments": f"NGN {outstanding_payments:,.2f}",
            },
            "hostelOccupancy": hostel_occupancy,
            "genderDistribution": gender_distribution,
            "recentApplications": recent_applications,
            "recentActivities": activities
        })
    
    def _get_time_ago(self, dt):
        """Helper method to format time ago string"""
        now = timezone.now()
        diff = now - dt
        
        if diff.days > 0:
            if diff.days == 1:
                return "Yesterday"
            elif diff.days < 7:
                return f"{diff.days} days ago"
            else:
                return dt.strftime("%b %d, %Y")
        
        hours = diff.seconds // 3600
        if hours > 0:
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        
        minutes = (diff.seconds % 3600) // 60
        if minutes > 0:
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        
        return "Just now"
    
    def _parse_time_ago(self, time_str):
        """Helper method to parse time ago string for sorting"""
        now = timezone.now()
        
        if time_str == "Just now":
            return now
        elif time_str == "Yesterday":
            return now - timedelta(days=1)
        elif "minute" in time_str:
            minutes = int(time_str.split()[0])
            return now - timedelta(minutes=minutes)
        elif "hour" in time_str:
            hours = int(time_str.split()[0])
            return now - timedelta(hours=hours)
        elif "day" in time_str:
            days = int(time_str.split()[0])
            return now - timedelta(days=days)
        else:
            # Handle date format
            try:
                return datetime.strptime(time_str, "%b %d, %Y")
            except:
                return now - timedelta(days=7)  # Default to 7 days ago if parsing fails


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_method', 'application']
    ordering_fields = ['payment_date', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        return PaymentSerializer
    
    def get_queryset(self):
        user = self.request.user
        # Admin can see all payments
        if user.is_staff:
            return Payment.objects.all()
        # Regular users can only see their own payments
        return Payment.objects.filter(application__student=user)
    
    @action(detail=False, methods=['get'])
    def my_payments(self, request):
        """Get all payments for the current user"""
        payments = Payment.objects.filter(application__student=request.user)
        serializer = self.get_serializer(payments, many=True)
        return Response(serializer.data)
