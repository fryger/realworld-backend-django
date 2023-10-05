from django.urls import path
from .views import RegisterView, LoginView, UserView, ProfileView, ProfileFollowView


urlpatterns = [
    path("users", RegisterView.as_view()),
    path("users/login", LoginView.as_view()),
    path("user", UserView.as_view()),
    path("profiles/<str:username>", ProfileView.as_view()),
    path("profiles/<str:username>/follow", ProfileFollowView.as_view()),
]
