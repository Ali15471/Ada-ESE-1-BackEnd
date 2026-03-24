from django.test import TestCase
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

# Create your tests here.

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user(db):
    user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpassword')
    return user

@pytest.fixture
def authenticated_client(api_client, create_user):
    response = api_client.post('/api/auth/login/', {'username': 'testuser', 'password': 'testpassword'})
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')
    return api_client

@pytest.mark.django_db
def test_user_registration_profile(api_client):
    response = api_client.post('/api/auth/register/', {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'newpassword'
    }, format='json')
    assert response.status_code == 201
    user = User.objects.get(username='newuser')
    assert hasattr(user, 'profile')

@pytest.mark.django_db
def test_duplicate_email_registration(api_client, create_user):
    User.objects.create_user(username='existinguser', email='existinguser@example.com', password='existingpassword')
    response = api_client.post('/api/auth/register/', {
        'username': 'newuser',
        'email': 'existinguser@example.com',
        'password': 'newpassword'
    }, format='json')
    assert response.status_code == 400

@pytest.mark.django_db
def test_user_login(api_client, create_user):
    response = api_client.post('/api/auth/login/', {
        'username': 'testuser',
        'password': 'testpassword'
    }, format='json')
    assert response.status_code == 200
    assert 'access' in response.data
    assert 'refresh' in response.data

@pytest.mark.django_db
def test_wrong_password_login(api_client, create_user):
    response = api_client.post('/api/auth/login/', {
        'username': 'testuser',
        'password': 'wrongpassword'
    }, format='json')
    assert response.status_code == 401

@pytest.mark.django_db
def test_me_endpoint(authenticated_client):
    response = authenticated_client.get('/api/auth/me/')
    assert response.status_code == 200
    assert response.data['username'] == 'testuser'

@pytest.mark.django_db
def test_me_endpoint_unauthenticated(api_client):
    response = api_client.get('/api/auth/me/')
    assert response.status_code == 401

@pytest.mark.django_db
def test_password_reset_returns_200(api_client, create_user):
    response = api_client.post('/api/auth/password-reset/', {
        'email': 'no_user@example.com'
    }, format='json')
    assert response.status_code == 200