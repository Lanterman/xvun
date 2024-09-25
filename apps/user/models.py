import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


AbstractUser._meta.get_field('username').max_length = 50
AbstractUser._meta.get_field('username').help_text = _(
            "Required. 50 characters or fewer. Letters, digits and @/./+/-/_ only."
        )


class User(AbstractUser):
    """User model"""

    created_in: datetime.datetime = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(_('email address'), blank=False, help_text="Required.", unique=True, 
                              error_messages={"unique": _("A user with that email already exists.")})
    hashed_password: str = models.CharField("password", max_length=128, help_text="Required.")

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('user-detail', kwargs={'username': self.username})