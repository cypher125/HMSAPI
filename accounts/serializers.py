from rest_framework import serializers
from .models import User, Student, EmergencyContact
from django.contrib.auth.password_validation import validate_password


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'user_type', 'profile_picture', 'phone_number']
        read_only_fields = ['id']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'user_type', 'profile_picture', 'phone_number']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = '__all__'


class StudentSerializer(serializers.ModelSerializer):
    emergency_contacts = EmergencyContactSerializer(many=True, read_only=True)
    
    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = ['user']


class StudentDetailSerializer(serializers.ModelSerializer):
    emergency_contacts = EmergencyContactSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Student
        fields = '__all__' 