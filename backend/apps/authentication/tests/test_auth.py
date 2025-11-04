import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.authentication.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_data():
    return {
        'email': 'test@example.com',
        'password': 'TestPass123!',
        'password_confirm': 'TestPass123!',
        'first_name': 'Test',
        'last_name': 'User'
    }


@pytest.mark.django_db
class TestUserRegistration:
    
    def test_register_success(self, api_client, user_data):
        url = reverse('register')
        response = api_client.post(url, user_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'user' in response.data
        assert response.data['user']['email'] == user_data['email']
        
        # Verify user created in database
        user = User.objects.get(email=user_data['email'])
        assert user.first_name == user_data['first_name']
        assert user.is_verified is False
    
    def test_register_duplicate_email(self, api_client, user_data):
        # Create user first
        User.objects.create_user(
            email=user_data['email'],
            password=user_data['password']
        )
        
        # Try to register again
        url = reverse('register')
        response = api_client.post(url, user_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_register_password_mismatch(self, api_client, user_data):
        user_data['password_confirm'] = 'DifferentPassword123!'
        
        url = reverse('register')
        response = api_client.post(url, user_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_register_weak_password(self, api_client, user_data):
        user_data['password'] = '123'
        user_data['password_confirm'] = '123'
        
        url = reverse('register')
        response = api_client.post(url, user_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserLogin:
    
    @pytest.fixture
    def registered_user(self, user_data):
        user = User.objects.create_user(
            email=user_data['email'],
            password=user_data['password'],
            first_name=user_data['first_name']
        )
        return user
    
    def test_login_success(self, api_client, registered_user, user_data):
        url = reverse('login')
        response = api_client.post(url, {
            'email': user_data['email'],
            'password': user_data['password']
        }, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access_token' in response.data
        assert 'refresh_token' in response.data
        assert 'user' in response.data
        assert response.data['user']['email'] == user_data['email']
    
    def test_login_invalid_credentials(self, api_client, registered_user):
        url = reverse('login')
        response = api_client.post(url, {
            'email': registered_user.email,
            'password': 'WrongPassword123!'
        }, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_login_nonexistent_user(self, api_client):
        url = reverse('login')
        response = api_client.post(url, {
            'email': 'nonexistent@example.com',
            'password': 'SomePassword123!'
        }, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_login_inactive_user(self, api_client, registered_user, user_data):
        registered_user.is_active = False
        registered_user.save()
        
        url = reverse('login')
        response = api_client.post(url, {
            'email': user_data['email'],
            'password': user_data['password']
        }, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestJWTAuthentication:
    
    @pytest.fixture
    def authenticated_client(self, api_client, user_data):
        user = User.objects.create_user(
            email=user_data['email'],
            password=user_data['password']
        )
        
        # Login to get tokens
        url = reverse('login')
        response = api_client.post(url, {
            'email': user_data['email'],
            'password': user_data['password']
        }, format='json')
        
        access_token = response.data['access_token']
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        return api_client, user
    
    def test_access_protected_endpoint(self, authenticated_client):
        client, user = authenticated_client
        
        url = reverse('user-profile')
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user.email
    
    def test_access_without_token(self, api_client):
        url = reverse('user-profile')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_refresh_token(self, api_client, user_data):
        # Login first
        user = User.objects.create_user(
            email=user_data['email'],
            password=user_data['password']
        )
        
        login_url = reverse('login')
        login_response = api_client.post(login_url, {
            'email': user_data['email'],
            'password': user_data['password']
        }, format='json')
        
        refresh_token = login_response.data['refresh_token']
        
        # Refresh token
        refresh_url = reverse('refresh-token')
        refresh_response = api_client.post(refresh_url, {
            'refresh_token': refresh_token
        }, format='json')
        
        assert refresh_response.status_code == status.HTTP_200_OK
        assert 'access_token' in refresh_response.data
        assert 'refresh_token' in refresh_response.data