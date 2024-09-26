from gettext import ngettext
from django.contrib import messages
from django.contrib import admin

from . import models


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    """Collection admin"""

    list_display = ("id", "name", "user_id", "created_in")
    list_display_links = ("id", "name", "user_id", "created_in")
    fields = ("name", "description", "updated_in", "user_id")
    search_fields = ("name", )
    list_max_show_all = 250
    list_per_page = 150


@admin.register(models.Link)
class LinkAdmin(admin.ModelAdmin):
    """Link admin"""

    list_display = ("id", "title", "user_id", "type_of_link", "created_in")
    list_display_links = ("id", "title", "user_id", "type_of_link", "created_in")
    fields = ("title", "description", "link", "image", "type_of_link", 
              "updated_in", "user_id", "collections")
    search_fields = ("title ", )
    list_filter = ("type_of_link", )
    list_max_show_all = 250
    list_per_page = 150
    list_select_related = True
    raw_id_fields = ("collections", )
