import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from posts.models import Post
from comments.models import Comment

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
def authenticated_client(api_client, create_user):
    response = api_client.post(
        "/api/auth/login/",
        {"username": "testuser", "password": "TestPassword123!"},
        format="json",
    )
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')
    return api_client


@pytest.fixture
def other_user(db):
    user = User.objects.create_user(
        username="otheruser", email="otheruser@example.com", password="TestPassword123!"
    )
    return user


@pytest.fixture
def authenticated_client_other(api_client, other_user):
    response = api_client.post(
        "/api/auth/login/",
        {"username": "otheruser", "password": "TestPassword123!"},
        format="json",
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
def create_comment(db, create_user, create_post):
    comment = Comment.objects.create(
        content="This is a test comment.", author=create_user, post=create_post
    )
    return comment


@pytest.mark.django_db
def test_list_comments(api_client, create_post, create_comment):
    response = api_client.get(f"/api/posts/{create_post.id}/comments/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_create_comment_required_auth(authenticated_client, create_post):
    response = authenticated_client.post(
        f"/api/posts/{create_post.id}/comments/",
        {"content": "This is a new comment."},
        format="json",
    )
    assert response.status_code == 201


@pytest.mark.django_db
def test_create_comment_unauthenticated(api_client, create_post):
    response = api_client.post(
        f"/api/posts/{create_post.id}/comments/",
        {"content": "This is a new comment."},
        format="json",
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_delete_comment_by_other_user(authenticated_client_other, create_comment):
    # Attempt to delete the comment created by testuser
    response = authenticated_client_other.delete(
        f"/api/posts/{create_comment.post.id}/comments/{create_comment.id}/"
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_post_scoped_comments(api_client, create_post, create_comment):
    # Create another post and comment
    other_post = Post.objects.create(
        title="Other Post",
        content="This is another post.",
        author=create_comment.author,
        status="PUBLISHED",
    )
    Comment.objects.create(
        content="Comment for other post.", author=create_comment.author, post=other_post
    )

    response = api_client.get(f"/api/posts/{create_post.id}/comments/")
    assert response.status_code == 200
    # Ensure only comments for the specific post are returned
    for comment in response.data:
        assert comment["post"] == create_post.id
