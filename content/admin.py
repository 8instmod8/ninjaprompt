# content/admin.py
from django.contrib import admin
from django import forms
from django.urls import path
from django.utils.safestring import mark_safe

from .models import Category, Subcategory, Group, ContentItem
from .views import bulk_import_view


class ContentItemAdminForm(forms.ModelForm):
    class Meta:
        model = ContentItem
        fields = ['category', 'subcategory', 'group', 'photo', 'full_text']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Категория
        self.fields['category'].queryset = Category.objects.order_by('order', 'name')

        # ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
        # Фильтрация подкатегорий в зависимости от выбранной категории
        category_id = None
        if self.instance.pk and self.instance.category:
            category_id = self.instance.category.id
        elif self.data and self.data.get('category'):
            try:
                category_id = int(self.data.get('category'))
            except (ValueError, TypeError):
                pass

        if category_id:
            self.fields['subcategory'].queryset = Subcategory.objects.filter(
                category_id=category_id
            ).order_by('name')
        else:
            # При создании новой карточки — показываем все
            self.fields['subcategory'].queryset = Subcategory.objects.select_related('category').order_by(
                'category__order', 'category__name', 'name'
            )
        # ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←

@admin.register(ContentItem)
class ContentItemAdmin(admin.ModelAdmin):
    form = ContentItemAdminForm

    list_display = ('id', 'effective_category', 'subcategory', 'group', 'created_at', 'photo_preview_list')
    list_display_links = ('id', 'effective_category')
    list_filter = ('category', 'subcategory__category', 'group', 'created_at')
    search_fields = ('full_text', 'category__name', 'subcategory__name', 'group__name')
    ordering = ('-created_at',)

    autocomplete_fields = ()

    fieldsets = (
        ('Привязка к категории', {
            'fields': ('category', 'subcategory'),
            'description': 'Выберите категорию — подкатегории отфильтруются'
        }),
        ('Фото', {
            'fields': ('photo', 'photo_preview'),
        }),
        ('Промпт', {
            'fields': ('full_text',),
        }),
        ('Группа (опционально)', {
            'fields': ('group',),
            'classes': ('collapse',),
        }),
        ('Метаданные', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    readonly_fields = ('created_at', 'photo_preview')
    change_list_template = 'content/contentitem_changelist.html'

    class Media:
        js = ('admin/js/jquery.init.js', 'content/js/category_subcategory_filter.js')

    # Методы...
    def effective_category(self, obj):
        return obj.effective_category if obj else '-'

    def photo_preview_list(self, obj):
        if obj and obj.photo:
            return mark_safe(f'<img src="{obj.photo.url}" style="max-height: 60px; border-radius: 6px;">')
        return "—"
    photo_preview_list.short_description = 'Фото'

    def photo_preview(self, obj=None):
        if not obj or not obj.pk or not obj.photo:
            return mark_safe('<p style="color:#666; font-style:italic;">Фото ещё не загружено</p>')
        return mark_safe(
            f'<img src="{obj.photo.url}" style="max-height: 380px; max-width: 100%; border-radius: 10px; border: 1px solid #ddd;">'
        )
    photo_preview.short_description = 'Текущее фото'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [path('bulk-import/', bulk_import_view, name='bulk_import')]
        return custom_urls + urls
