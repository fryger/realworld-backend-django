from .models import User
from .serializers import RegisterUserSerializer

from rest_framework import status
from rest_framework import generics
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


class WrapUnwrapDataMixin:
    wrapper_key  = ""

    def create(self, request, *args, **kwargs):

        try:
            serializer = self.get_serializer(data=request.data.get(self.wrapper_key, {}))
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)

            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        
        except serializers.ValidationError as e:

            return Response({self.wrapper_key:e.detail}, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(WrapUnwrapDataMixin,generics.CreateAPIView):
    wrapper_key = "user"

    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterUserSerializer




        