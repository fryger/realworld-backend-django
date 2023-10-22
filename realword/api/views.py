from functools import wraps
from .models import User, FollowingUser, Article, ArticleFavorited
from .serializers import (
    UserSerializer,
    LoginSerializer,
    ProfileSerializer,
    ArticleSerializer,
)

from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework import serializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.mixins import RetrieveModelMixin, CreateModelMixin
from rest_framework.generics import (
    GenericAPIView,
    CreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView,
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


class ArticleView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ArticleSerializer
    queryset = Article.objects.all()

    # def get_serializer(self, *args, **kwargs):
    #     context = {"request": self.request}
    #     return self.serializer_class(*args, context=context, **kwargs)

    def post(self, request, *args, **kwargs):
        modified_data = request.data.copy().get("article")

        serializer = self.get_serializer(data=modified_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class ArticleDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    lookup_field = "slug"

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data["article"], partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)


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
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
