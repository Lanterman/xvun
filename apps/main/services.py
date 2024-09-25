from django.db import models


class TypeOfLink(models.TextChoices):
    """Choose time"""

    WEBSITE = "website"
    BOOK = "book"
    ARTICLE = "article"
    MUSIC = "music"
    VIDEO = "video"


def add_data_to_serializer_data(serializer) -> dict:
    """Get info by a link and add they to the serializer data"""

    
