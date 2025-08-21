from django.contrib import admin
from .models import Objeto
from django.utils.html import format_html


@admin.register(Objeto)
class ObjetoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "short_description",
        "image_preview",
        "user",
        "dt_object",
        "dt_create",
        "dt_modified",
    )
    list_display_links = ("id", "name")
    list_filter = ("dt_object", "dt_create", "user")
    search_fields = ("name", "description", "user__username")
    ordering = ("-dt_create",)
    readonly_fields = ("dt_create", "dt_modified", "image_preview")

    fieldsets = (
        ("Informações principais", {
            "fields": ("name", "description", "dt_object", "user")
        }),
        ("Mídia", {
            "fields": ("img_object", "image_preview")
        }),
        ("Datas", {
            "fields": ("dt_create", "dt_modified"),
            "classes": ("collapse",)  # esconde por padrão
        }),
    )

    def short_description(self, obj):
        return (obj.description[:50] + "...") if obj.description else "-"
    short_description.short_description = "Descrição"

    def image_preview(self, obj):
        if obj.img_object:
            return format_html('<img src="{}" width="70" style="border-radius:5px"/>', obj.img_object.url)
        return "-"
    image_preview.short_description = "Preview"


