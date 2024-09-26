import opengraph_py3

from django.db import models

class TypeOfLink(models.TextChoices):
    """Choose time"""

    WEBSITE = "website"
    BOOK = "book"
    ARTICLE = "article"
    MUSIC = "music"
    VIDEO = "video"


def get_title(data: dict) -> str:
    """Get title from dict"""

    try:
        return data["title"]
    except KeyError:
        return "Empty"


def get_type_of_list(data: dict) -> str:
    """Get type of link from dict"""

    _type_of_link = data["type"].split(".")[0]

    if _type_of_link.capitalize() in TypeOfLink.labels:
        return _type_of_link
    
    return TypeOfLink.WEBSITE


def get_dict_with_data_from_link(link: str) -> dict:
    """Get a dict with data from a link"""

    data = opengraph_py3.OpenGraph(url=link, scrape=True)
    
    result = {
        "title": get_title(data),
        "description": data["description"],
        "image": data["image"],
        "link": data["url"],
        "type_of_link": get_type_of_list(data),
    }

    return result


def add_data_by_link(serializer, user) -> dict:
    """Get info by a link and add they to the serializer data"""

    data = get_dict_with_data_from_link(serializer.validated_data["link"])
    serializer.validated_data["title"] = data["title"]
    serializer.validated_data["description"] = data["description"]
    serializer.validated_data["image"] = data["image"]
    serializer.validated_data["type_of_link"] = data["type_of_link"]
    serializer.validated_data["user_id"] = user
    return serializer
