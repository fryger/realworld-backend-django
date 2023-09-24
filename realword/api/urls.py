from django.urls import path, include
from .views import RegisterView


urlpatterns = [
    path("users",RegisterView.as_view())
]
