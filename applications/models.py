from django.db import models
from django.conf import settings
from hostels.models import Room


class Application(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Cancelled', 'Cancelled'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('Unpaid', 'Unpaid'),
        ('Partially Paid', 'Partially Paid'),
        ('Paid', 'Paid'),
        ('Refunded', 'Refunded'),
    ]
    
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='applications')
    application_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    payment_status = models.CharField(max_length=15, choices=PAYMENT_STATUS_CHOICES, default='Unpaid')
    check_in_date = models.DateField(null=True, blank=True)
    check_out_date = models.DateField(null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transaction_reference = models.CharField(max_length=100, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    special_requests = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-application_date']
    
    def __str__(self):
        return f"{self.student.username} - {self.room} - {self.status}"
    
    @property
    def remaining_amount(self):
        return self.room.price - self.amount_paid
    
    @property
    def is_fully_paid(self):
        return self.amount_paid >= self.room.price
    
    def save(self, *args, **kwargs):
        if self.is_fully_paid and self.payment_status != 'Paid':
            self.payment_status = 'Paid'
        elif self.amount_paid > 0 and self.amount_paid < self.room.price:
            self.payment_status = 'Partially Paid'
        super().save(*args, **kwargs)


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('Card', 'Card'),
        ('Bank Transfer', 'Bank Transfer'),
        ('Cash', 'Cash'),
    ]
    
    application = models.OneToOneField(Application, related_name='payment', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.reference} - ₦{self.amount} for {self.application}"
