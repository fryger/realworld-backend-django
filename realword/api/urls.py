from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    UserView,
    ProfileView,
    ProfileFollowView,
    ArticleView,
    ArticleDetailView,
    ArticleFavoriteView,
    CommentView,
)


urlpatterns = [
    path("users", RegisterView.as_view()),
    path("users/login", LoginView.as_view()),
    path("user", UserView.as_view()),
    path("profiles/<str:username>", ProfileView.as_view()),
    path("profiles/<str:username>/follow", ProfileFollowView.as_view()),
    path("articles", ArticleView.as_view()),
    path("articles/<str:slug>", ArticleDetailView.as_view()),
    path("articles/<str:slug>/favorite", ArticleFavoriteView.as_view()),
    path("articles/<str:slug>/comments", CommentView.as_view()),
    path("articles/<str:slug>/comments/<int:id>", CommentView.as_view()),
]
