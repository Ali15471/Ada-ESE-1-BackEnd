import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from posts.models import Post

# Create your tests here.


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user(db):
    user = User.objects.create_user(
        username="testuser", email="testuser@example.com", password="TestPassword123!"
    )
    return user


@pytest.fixture
def other_user(db):
    user = User.objects.create_user(
        username="otheruser", email="otheruser@example.com", password="TestPassword123!"
    )
    return user


@pytest.fixture
def authenticated_client(api_client, create_user):
    response = api_client.post(
        "/api/auth/login/", {"username": "testuser", "password": "TestPassword123!"}
    )
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')
    return api_client


@pytest.fixture
def authenticated_client_other(api_client, other_user):
    response = api_client.post(
        "/api/auth/login/", {"username": "otheruser", "password": "TestPassword123!"}
    )
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')
    return api_client


@pytest.fixture
def create_post(db, create_user):
    post = Post.objects.create(
        title="Test Post",
        content="This is a test post.",
        author=create_user,
        status="PUBLISHED",
    )
    return post


@pytest.fixture
def create_draft_post(db, create_user):
    post = Post.objects.create(
        title="Draft Post",
        content="This is a draft post.",
        author=create_user,
        status="DRAFT",
    )
    return post


@pytest.mark.django_db
def test_unauthenticated_user_only_sees_published_posts(
    api_client, create_post, create_draft_post
):
    response = api_client.get("/api/posts/")
    assert response.status_code == 200
    titles = [post["title"] for post in response.data]
    assert "Test Post" in titles


@pytest.mark.django_db
def test_authenticated_user_can_see_own_draft_posts(
    authenticated_client, create_draft_post
):
    response = authenticated_client.get("/api/posts/")
    assert response.status_code == 200
    titles = [post["title"] for post in response.data]
    assert "Draft Post" in titles


@pytest.mark.django_db
def test_create_post(authenticated_client):
    response = authenticated_client.post(
        "/api/posts/",
        {"title": "New Post", "content": "This is a new post.", "status": "PUBLISHED"},
        format="json",
    )
    assert response.status_code == 201
    post = Post.objects.get(title="New Post")
    assert post.content == "This is a new post."
    assert post.author.username == "testuser"


@pytest.mark.django_db
def test_only_author_can_update_post(authenticated_client_other, create_post):
    response = authenticated_client_other.put(
        f"/api/posts/{create_post.id}/",
        {
            "title": "Hacked Post",
        },
        format="json",
    )
    assert response.status_code == 403
    create_post.refresh_from_db()
    assert create_post.title == "Test Post"


@pytest.mark.django_db
def test_only_author_can_delete_post(authenticated_client_other, create_post):
    response = authenticated_client_other.delete(f"/api/posts/{create_post.id}/")
    assert response.status_code == 403
    assert Post.objects.filter(id=create_post.id).exists()
