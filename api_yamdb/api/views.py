import django_filters

from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import (CharFilter, DjangoFilterBackend,
                                           NumberFilter)

from rest_framework import filters, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from reviews.models import Category, Genre, Review, Title

from .permissions import (IsAdminOrReadOnly, IsAuthorOrReadOnly,
                          IsModeratorOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitlesCreateSerializer, TitlesSerializer)
from .core import CustomViewSet


class CharFilterInFilter(django_filters.CharFilter,
                         django_filters.BaseInFilter):
    pass


class TitleFilter(django_filters.FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains')
    category = CharFilter(field_name='category__slug')
    genre = CharFilterInFilter(field_name='genre__slug', lookup_expr='in')
    year = NumberFilter(field_name='year')

    class Meta:
        model = Title
        fields = ['name', 'year', 'category', 'genre']


class TitlesViewSet(viewsets.ModelViewSet):
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)

    def get_queryset(self):
        return Title.objects.all().annotate(
            rating=Avg('reviews__score'),
        ).select_related('category')

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PATCH':
            return TitlesCreateSerializer
        return TitlesSerializer


class GenreViewSet(CustomViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)
    lookup_field = ('slug')


class CategoryViewSet(CustomViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)
    lookup_field = ('slug')


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly,
                          IsModeratorOrReadOnly
                          | IsAuthorOrReadOnly]

    def get_queryset(self):
        review = get_object_or_404(
            Review.objects.select_related('author', 'title'),
            pk=self.kwargs.get("review_id")
        )
        return review.comments.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(
            Review.objects.select_related('author', 'title'),
            id=review_id, title=title_id
        )
        serializer.save(author=self.request.user, review=review)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly,
                          IsModeratorOrReadOnly
                          | IsAuthorOrReadOnly]

    def get_queryset(self):
        title = get_object_or_404(
            Title.objects.select_related('category'),
            pk=self.kwargs.get("title_id")
        )
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(
            Title.objects.select_related('category'),
            id=title_id
        )
        serializer.save(author=self.request.user, title=title)
