from functools import wraps
from .models import User, FollowingUser, Article, ArticleFavorited, Comment
from .serializers import (
    UserSerializer,
    LoginSerializer,
    ProfileSerializer,
    ArticleSerializer,
    CommentSerializer,
)

from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework import serializers
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.mixins import (
    RetrieveModelMixin,
    CreateModelMixin,
    ListModelMixin,
    DestroyModelMixin,
)
from rest_framework.generics import (
    GenericAPIView,
    CreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
)
from rest_framework.views import APIView


class RegisterView(APIView):
    wrapper_key = "user"
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data.get(self.wrapper_key, {}))

        if serializer.is_valid():
            serializer.save()

            return Response(
                {self.wrapper_key: serializer.data}, status=status.HTTP_201_CREATED
            )

        return Response(
            {self.wrapper_key: serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )


class LoginView(APIView):
    wrapper_key = "user"
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data.get(self.wrapper_key, {}))

        if serializer.is_valid():
            user = UserSerializer(serializer.validated_data["user"])

            return Response({self.wrapper_key: user.data}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserView(APIView):
    wrapper_key = "user"
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user)

        return Response({self.wrapper_key: serializer.data})

    def put(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user, request.data["user"], partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {self.wrapper_key: serializer.data}, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileSerializer
    lookup_field = "username"

    def get_object(self):
        username = self.kwargs[self.lookup_field]

        return User.objects.get(username=username)

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"profile": serializer.data})


class ProfileFollowView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileSerializer
    lookup_field = "username"

    def get_object(self):
        username = self.kwargs[self.lookup_field]

        return User.objects.get(username=username)

    def get_serializer(self, *args, **kwargs):
        context = {"request": self.request}
        return self.serializer_class(*args, context=context, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(instance=self.get_object())

        return Response({"profile": serializer.data}, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        serializer = self.get_serializer(instance=self.get_object())

        return Response({"profile": serializer.data}, status=status.HTTP_200_OK)


class ArticleView(CreateAPIView, ListAPIView, GenericAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ArticleSerializer

    article_limit = 20
    article_offset = 0

    def get_queryset(self):
        tag = self.request.GET.get("tag")
        author = self.request.GET.get("author")
        favorited = self.request.GET.get("favorited")
        limit = int(self.request.GET.get("limit", self.article_limit))
        offset = int(self.request.GET.get("offset", self.article_offset))

        queryset = Article.objects.all()

        if tag:
            queryset = queryset.filter(tagList__icontains=tag)

        if author:
            author_obj = User.objects.filter(username=author).first()

            queryset = queryset.filter(author=author_obj)

        if favorited:
            fav_by_user = User.objects.filter(username=favorited).first()

            favorite_articles = ArticleFavorited.objects.filter(
                user=fav_by_user
            ).values("article")

            queryset = queryset.filter(pk__in=favorite_articles)

        queryset = queryset.order_by("-createdAt")

        limited_queryset = queryset[offset : limit + offset]

        queryset_count = limited_queryset.count()

        return limited_queryset, queryset_count

    def get(self, request, *args, **kwargs):
        queryset, queryset_count = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({"articles": serializer.data, "articlesCount": queryset_count})

    def post(self, request, *args, **kwargs):
        modified_data = request.data.copy().get("article")

        serializer = self.get_serializer(data=modified_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(
            {"article": serializer.data},
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class ArticleDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    lookup_field = "slug"

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"article": serializer.data})

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data["article"], partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({"article": serializer.data})


class ArticleFavoriteView(GenericAPIView, RetrieveModelMixin):
    permission_classes = (IsAuthenticated,)
    serializer_class = ArticleSerializer
    queryset = Article.objects.all()
    lookup_field = "slug"

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["favorite"] = True
        return context

    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"article": serializer.data})

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"article": serializer.data})


class CommentView(GenericAPIView, CreateModelMixin, ListModelMixin, DestroyModelMixin):
    permission_classes = (IsAuthenticated,)
    serializer_class = CommentSerializer
    # queryset = Article.objects.all()
    lookup_field = "id"

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["slug"] = self.kwargs["slug"]
        return context

    def get_queryset(self):
        slug = self.kwargs["slug"]

        article = Article.objects.get(slug=slug)

        queryset = article.comment_set.all()

        return queryset

    def get_object(self):
        return super().get_object()

    def post(self, request, *args, **kwargs):
        modified_data = request.data.copy().get("comment")

        serializer = self.get_serializer(data=modified_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(
            {"comment": serializer.data},
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({"comments": serializer.data})

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
