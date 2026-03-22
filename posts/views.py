from django.shortcuts import models
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, filters
from .models import Post
from .serializers import PostSerializer
# Create your views here.

class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user

class PostListCreateView(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['title', 'content', 'author__username']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']


    def get_queryset(self):
        # Only show published posts to unauthenticated users, and all posts to authenticated users (including their own drafts)
        user = self.request.user
        queryset = Post.objects.all()

        if user.is_authenticated:
            queryset = queryset.filter(models.Q(status='PUBLISHED') | models.Q(author=self.request.user))
        else:
            queryset = queryset.filter(status='PUBLISHED')
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        queryset = Post.objects.all()

        if user.is_authenticated:
            queryset = queryset.filter(models.Q(status='PUBLISHED') | models.Q(author=self.request.user))
        else:
            queryset = queryset.filter(status='PUBLISHED')
        return queryset