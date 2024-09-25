from django.db import models
import opengraph_py3

class TypeOfLink(models.TextChoices):
    """Choose time"""

    WEBSITE = "website"
    BOOK = "book"
    ARTICLE = "article"
    MUSIC = "music"
    VIDEO = "video"


def add_data_by_link(serializer, user) -> dict:
    """Get info by a link and add they to the serializer data"""

    data = opengraph_py3.OpenGraph(url=serializer.validated_data["link"])

    serializer.validated_data["title"] = data["title"]
    serializer.validated_data["description"] = data["description"]
    serializer.validated_data["image"] = data["image"]
    serializer.validated_data["user_id"] = user

    try:
        serializer.validated_data["type_of_link"] = data["type"]
    except KeyError:
        serializer.validated_data["type_of_link"] = TypeOfLink.WEBSITE
    
    return serializer
