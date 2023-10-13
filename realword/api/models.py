from django.db import models

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.text import slugify
from django.utils import timezone
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=80)

    email = models.EmailField(
        unique=True,
        max_length=255,
        blank=False,
    )

    bio = models.TextField(max_length=255, blank=True)

    image = models.URLField(blank=True)

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into " "this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be "
            "treated as active. Unselect this instead "
            "of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(
        _("date joined"),
        default=timezone.now,
    )

    # Add additional fields here if needed

    objects = UserManager()

    USERNAME_FIELD = "email"


class FollowingUser(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_follows"
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_followed"
    )

    def clean(self):
        if self.user == self.following:
            raise ValidationError(_("User cannot follows itself"))


class Article(models.Model):
    title = models.CharField(max_length=150)
    description = models.CharField(max_length=255)
    body = models.TextField()
    tagList = models.JSONField(default=list)
    slug = models.SlugField(unique=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.PROTECT)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title


class ArticleFavorited(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
