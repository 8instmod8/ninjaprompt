# content/admin.py
from django.contrib import admin
from django import forms
from django.urls import path
from django.utils.safestring import mark_safe

from .models import Category, Subcategory, Group, ContentItem, ContentItemPhoto
from .views import bulk_import_view


class ContentItemPhotoInline(admin.TabularInline):
    model = ContentItemPhoto
    extra = 5
    max_num = 20
    fields = ('photo', 'order', 'photo_preview')
    readonly_fields = ('photo_preview',)
    ordering = ('order',)

    def photo_preview(self, obj=None):
        if obj and obj.photo:
            return mark_safe(f'<img src="{obj.photo.url}" style="max-height: 60px; border-radius: 4px;">')
        return "—"
    photo_preview.short_description = 'Превью'


class ContentItemAdminForm(forms.ModelForm):
    class Meta:
        model = ContentItem
        fields = ['category', 'subcategory', 'group', 'full_text']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['category'].queryset = Category.objects.order_by('order', 'name')

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
            self.fields['subcategory'].queryset = Subcategory.objects.select_related('category').order_by(
                'category__order', 'category__name', 'name'
            )


@admin.register(ContentItem)
class ContentItemAdmin(admin.ModelAdmin):
    form = ContentItemAdminForm
    inlines = [ContentItemPhotoInline]

    list_display = ('id', 'effective_category', 'subcategory', 'group', 
                    'created_at', 'photo_preview_list', 'photo_count')
    list_display_links = ('id', 'effective_category')
    list_filter = ('category', 'subcategory__category', 'group', 'created_at')
    search_fields = ('full_text', 'category__name', 'subcategory__name', 'group__name')
    ordering = ('-created_at',)

    readonly_fields = ('created_at', 'photo_preview_admin')

    fieldsets = (
        ('Привязка к категории', {
            'fields': ('category', 'subcategory'),
            'description': 'Выберите категорию — подкатегории отфильтруются'
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

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('bulk-import/', self.admin_site.admin_view(bulk_import_view), name='bulk_import'),
        ]
        return custom_urls + urls

    def photo_count(self, obj):
        return obj.photos.count() or 0
    photo_count.short_description = 'Кол-во фото'

    def photo_preview_list(self, obj):
        first = obj.photos.first()
        photo = first.photo if first else getattr(obj, 'photo', None)
        if photo:
            return mark_safe(f'<img src="{photo.url}" style="max-height: 60px; border-radius: 6px;">')
        return "—"
    photo_preview_list.short_description = 'Фото'

    def photo_preview_admin(self, obj=None):
        first = obj.photos.first() if obj else None
        photo = first.photo if first else getattr(obj, 'photo', None)
        if photo:
            return mark_safe(f'<img src="{photo.url}" style="max-height: 300px; border-radius: 8px;">')
        return "Нет фото"
    photo_preview_admin.short_description = 'Превью'
    
    actions = ['bulk_import_action']

    def bulk_import_action(self, request, queryset):
        from django.shortcuts import redirect
        return redirect('admin:content_contentitem_bulk_import')
    bulk_import_action.short_description = "📦 Массовый импорт"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'display_type', 'order')
    list_editable = ('display_type', 'order')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')
    search_fields = ('name',)

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Отображение', {
            'fields': ('display_type',),
            'description': 'Как будут отображаться карточки этой категории'
        }),
        ('Сортировка', {
            'fields': ('order',),
        }),
    )

@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'category')
    list_filter = ('category',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('subcategories',)
    search_fields = ('name',)
