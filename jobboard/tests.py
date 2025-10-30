# jobboard/tests.py
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Job, Company

User = get_user_model()

class JobBoardTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='pass123')
        self.other = User.objects.create_user(username='bob', password='pass123')

    def test_register_creates_default_company(self):
        url = reverse('register')
        data = {'username': 'charlie', 'password': 'password123', 'email': 'c@test.com'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
   
        user = User.objects.get(username='charlie')
    
        self.assertTrue(Company.objects.filter(created_by=user, name__icontains='Default Company for charlie').exists())

    def test_prevent_duplicate_application(self):

        company = Company.objects.create(name='C1', description='d', created_by=self.user)
        job = Job.objects.create(title='J1', description='d', company=company, location='Remote')

        self.client.login(username='bob', password='pass123')  # or use JWT

        apply_url = reverse('job-apply', kwargs={'pk': job.id})
        resp1 = self.client.post(apply_url, {'cover_letter':'hi'})
        self.assertIn(resp1.status_code, (201, 200))

        resp2 = self.client.post(apply_url, {'cover_letter':'again'})
        self.assertEqual(resp2.status_code, 400)
        self.assertIn('already applied', str(resp2.data).lower())
