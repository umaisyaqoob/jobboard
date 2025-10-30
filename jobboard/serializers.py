
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Company, Job, JobApplication

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password']
        )
        return user

class CompanySerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.id')

    class Meta:
        model = Company
        fields = ('id', 'name', 'description', 'created_by', 'created_at')

class JobSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all())
    company_details = CompanySerializer(source='company', read_only=True)

    class Meta:
        model = Job
        fields = ('id', 'title', 'description', 'company', 'company_details', 'location', 'created_at')

class JobApplicationSerializer(serializers.ModelSerializer):
    applicant = serializers.ReadOnlyField(source='applicant.id')

    class Meta:
        model = JobApplication
        fields = ('id', 'job', 'applicant', 'cover_letter', 'applied_at')
        read_only_fields = ('applied_at', 'applicant')

    def validate(self, data):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return data
        job = data.get('job')
        applicant = request.user

        if JobApplication.objects.filter(job=job, applicant=applicant).exists():
            raise serializers.ValidationError("You have already applied to this job.")
        return data

    def create(self, validated_data):
        request = self.context['request']
        validated_data['applicant'] = request.user
        return super().create(validated_data)
