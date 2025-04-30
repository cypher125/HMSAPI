from rest_framework import serializers
from .models import Application, Payment
from hostels.serializers import RoomSerializer
from accounts.serializers import UserSerializer


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['application']


class ApplicationSerializer(serializers.ModelSerializer):
    remaining_amount = serializers.ReadOnlyField()
    is_fully_paid = serializers.ReadOnlyField()
    
    class Meta:
        model = Application
        fields = '__all__'
        read_only_fields = ['student', 'application_date', 'status', 'payment_status', 'created_at', 'updated_at']


class ApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['room', 'special_requests']
    
    def create(self, validated_data):
        # Get the current user as the student
        user = self.context['request'].user
        application = Application.objects.create(student=user, **validated_data)
        return application


class ApplicationDetailSerializer(serializers.ModelSerializer):
    room = RoomSerializer(read_only=True)
    student = UserSerializer(read_only=True)
    payment = PaymentSerializer(read_only=True)
    remaining_amount = serializers.ReadOnlyField()
    is_fully_paid = serializers.ReadOnlyField()
    
    class Meta:
        model = Application
        fields = '__all__'


class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['amount', 'payment_method']
    
    def create(self, validated_data):
        # Try to get application from the nested URL
        application_pk = self.context['view'].kwargs.get('application_pk')
        if application_pk:
            try:
                application = Application.objects.get(pk=application_pk)
            except Application.DoesNotExist:
                raise serializers.ValidationError({'application': 'Application does not exist.'})
        else:
            # If not in URL, try from validated data or request body
            application = validated_data.pop('application', None)
            if not application:
                application_id = self.initial_data.get('application_id')
                if not application_id:
                    raise serializers.ValidationError({'application': 'This field is required.'})
                try:
                    application = Application.objects.get(pk=application_id)
                except Application.DoesNotExist:
                    raise serializers.ValidationError({'application': 'Application does not exist.'})
                    
        # Generate a unique reference
        import uuid
        reference = f"PAY-{uuid.uuid4().hex[:8].upper()}"
        
        payment = Payment.objects.create(
            application=application,
            reference=reference,
            **validated_data
        )
        return payment 