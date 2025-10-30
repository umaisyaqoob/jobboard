# jobboard/views.py
from rest_framework import viewsets, generics, status, permissions, filters
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from django.shortcuts import get_object_or_404
from .models import Company, Job, JobApplication
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from .serializers import (
    RegisterSerializer, CompanySerializer, JobSerializer, JobApplicationSerializer
)
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db.models import Q

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

# Company creation (authenticated users only)
class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        qs = Company.objects.all()
        owner = self.request.query_params.get('owner')
        if owner:
            qs = qs.filter(created_by__id=owner)
        return qs


class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.select_related('company').all()
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['location', 'company__name', 'title']

    def get_queryset(self):
        qs = Job.objects.select_related('company').all()
        location = self.request.query_params.get('location')
        company = self.request.query_params.get('company')
        if location:
            qs = qs.filter(location__icontains=location)
        if company:
            qs = qs.filter(company__id=company)
        return qs

    def perform_create(self, serializer):
        company = serializer.validated_data['company']
        if company.created_by != self.request.user:
            raise PermissionDenied("You are not allowed to create jobs for this company.")
        serializer.save()

class ApplyToJobView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk, format=None):
        job = get_object_or_404(Job, pk=pk)
        serializer = JobApplicationSerializer(data=request.data, context={'request': request})
        # Ensure job is present in payload or set it explicitly
        if 'job' not in request.data:
        
            mutable_data = request.data.copy()
            mutable_data['job'] = job.id
            serializer = JobApplicationSerializer(data=mutable_data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
