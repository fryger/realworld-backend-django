from django.urls import path
from .views import RegisterView, LoginView, UserView


urlpatterns = [
    path("users", RegisterView.as_view()),
    path("users/login", LoginView.as_view()),
    path("user", UserView.as_view()),
]
