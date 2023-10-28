from rest_framework import serializers
from rest_framework.authentication import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, FollowingUser, Article, ArticleFavorited, Comment


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "email",
            "password",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def run_validation(self, data):
        email = data.get("email")
        password = data.get("password")

        if email and password:
            user = authenticate(
                request=self.context.get("request"), email=email, password=password
            )

            if not user:
                msg = _("Unable to log in with provided credentials.")
                raise serializers.ValidationError(msg, code="authorization")
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code="authorization")

        data["user"] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField("user_token")

    def user_token(self, user):
        return get_tokens_for_user(user)["access"]

    class Meta:
        model = User
        fields = ["username", "email", "password", "bio", "image", "token"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User(username=validated_data["username"], email=validated_data["email"])
        user.set_password(validated_data["password"])
        user.save()
        return user


class ProfileSerializer(serializers.ModelSerializer):
    following = serializers.SerializerMethodField("_following")

    def _following(self, obj):
        user = self.context.get("request").user

        following = FollowingUser.objects.filter(user=user, following=obj).exists()

        if self.context.get("request").method == "POST" and not following:
            FollowingUser.objects.create(user=user, following=obj)

            return True

        if self.context.get("request").method == "DELETE" and following:
            FollowingUser.objects.get(user=user, following=obj).delete()

            return False

        return following

    class Meta:
        model = User
        fields = ["username", "bio", "image", "following"]

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)

    #     return {"profile": data}


class ArticleSerializer(serializers.ModelSerializer):
    author = ProfileSerializer(read_only=True)
    favorited = serializers.SerializerMethodField("_favorited")
    favoritesCount = serializers.SerializerMethodField("_count_favorited")

    def _favorited(self, article) -> bool:
        user = self.context.get("request").user

        favorited = ArticleFavorited.objects.filter(user=user, article=article)

        if (
            self.context.get("favorite")
            and self.context.get("request").method == "POST"
            and not favorited
        ):
            ArticleFavorited.objects.create(user=user, article=article)

            return True

        if (
            self.context.get("favorite")
            and self.context.get("request").method == "DELETE"
            and favorited
        ):
            ArticleFavorited.objects.get(user=user, article=article).delete()

            return False

        return bool(favorited)

    def _count_favorited(self, article) -> int:
        count = ArticleFavorited.objects.filter(article=article).count()

        return count

    class Meta:
        model = Article
        fields = [
            "slug",
            "title",
            "description",
            "body",
            "tagList",
            "createdAt",
            "updatedAt",
            "favorited",
            "favoritesCount",
            "author",
        ]

    def create(self, validated_data):
        user = self.context.get("request").user

        validated_data["author"] = user

        return super().create(validated_data)

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)

    #     return {"article": data}


class CommentSerializer(serializers.ModelSerializer):
    author = ProfileSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "createdAt", "updatedAt", "body", "author"]

    def create(self, validated_data):
        user = self.context.get("request").user
        slug = self.context.get("slug")

        article = Article.objects.get(slug=slug)

        validated_data["author"] = user
        validated_data["article"] = article

        return super().create(validated_data)
