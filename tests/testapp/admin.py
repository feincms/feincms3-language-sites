from content_editor.admin import ContentEditor
from django.contrib import admin
from feincms3 import plugins
from feincms3.admin import TreeAdmin

from testapp import models


@admin.register(models.Page)
class PageAdmin(ContentEditor, TreeAdmin):
    list_display = [
        "indented_title",
        "move_column",
        "is_active",
        "language_code",
        "page_type",
    ]
    list_filter = ["is_active"]
    list_editable = ["is_active"]
    prepopulated_fields = {"slug": ["title"]}
    raw_id_fields = ["parent"]
    inlines = [plugins.snippet.SnippetInline.create(model=models.Snippet)]
