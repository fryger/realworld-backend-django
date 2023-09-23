from django.db import models

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin

from .managers import UserManager

class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(
        unique=True,
        max_length=255,
        blank=False,
    )

    bio =models.TextField(max_length=255,blank=True)

    image = models.URLField(blank=True)

    # All these field declarations are copied as-is
    # from `AbstractUser`
    # first_name = models.CharField(
    #     _('first name'),
    #     max_length=30,
    #     blank=True,
    # )
    # last_name = models.CharField(
    #     _('last name'),
    #     max_length=150,
    #     blank=True,
    # )
    # is_staff = models.BooleanField(
    #     _('staff status'),
    #     default=False,
    #     help_text=_(
    #         'Designates whether the user can log into '
    #         'this admin site.'
    #     ),
    # )
    # is_active = models.BooleanField(
    #     _('active'),
    #     default=True,
    #     help_text=_(
    #         'Designates whether this user should be '
    #         'treated as active. Unselect this instead '
    #         'of deleting accounts.'
    #     ),
    # )
    # date_joined = models.DateTimeField(
    #     _('date joined'),
    #     default=timezone.now,
    # )

    # Add additional fields here if needed

    objects = UserManager()

    USERNAME_FIELD = 'email'