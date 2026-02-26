from django.contrib import admin
from django.urls import path
from .models import Category, Group, ContentItem
from .views import bulk_import_view


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('categories',)


@admin.register(ContentItem)
class ContentItemAdmin(admin.ModelAdmin):
    list_display = ('category', 'group', 'created_at')
    list_filter = ('category', 'group')
    search_fields = ('full_text',)

    # Шаблон с кнопкой импорта
    change_list_template = 'content/contentitem_changelist.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('bulk-import/', bulk_import_view, name='bulk_import'),
        ]
        return custom_urls + urls