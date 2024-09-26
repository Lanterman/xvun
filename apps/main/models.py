import datetime

from typing import Optional

from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from config import settings
from .services import TypeOfLink


User = settings.AUTH_USER_MODEL


class Collection(models.Model):
    """Collection model"""

    name: str = models.CharField(_("name"), max_length=250, help_text="Required.", unique=True)
    description: str = models.CharField(_("description"), max_length=250, blank=True)
    created_in: datetime.datetime = models.DateTimeField(auto_now_add=True)
    updated_in: datetime.datetime = models.DateTimeField(blank=True, null=True)
    user_id = models.ForeignKey(to=User, verbose_name="user", on_delete=models.CASCADE, related_name="collection_set")

    class Meta:
        verbose_name = _("Collection")
        verbose_name_plural = _("Collections")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('collection-detail', kwargs={'name': self.name})


class Link(models.Model):
    """Link model"""

    title: str = models.CharField(_("title"), max_length=250, help_text="Required.")
    description: str = models.CharField(_("description"), max_length=250, help_text="Required.")
    link: str = models.CharField(_("link"), max_length=200, help_text="Required.", unique=True)
    image: bytes = models.ImageField(_("image"), blank=True, upload_to="link/")
    type_of_link: str = models.CharField(_("type"), max_length=250, default=TypeOfLink.WEBSITE, help_text="Required.", 
                                         choices=TypeOfLink.choices)
    created_in: datetime.datetime = models.DateTimeField(auto_now_add=True)
    updated_in: datetime.datetime = models.DateTimeField(blank=True, null=True)
    user_id = models.ForeignKey(to=User, verbose_name="user", on_delete=models.CASCADE, related_name="link_set")
    collections: Optional[list[Collection]] = models.ManyToManyField(to=Collection, related_name="links", 
                                                                     help_text="Required", blank=True)

    class Meta:
        verbose_name = _("Link")
        verbose_name_plural = _("Links")

    def __str__(self):
        return f"{self.title} - {self.link}"

    def get_absolute_url(self):
        return reverse('link-detail', kwargs={'id': self.id})
