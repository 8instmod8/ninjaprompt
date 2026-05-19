# content/admin.py
from django.contrib import admin
from django import forms
from django.urls import path
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError
from django.core.cache import cache

from .models import (
    Category, Subcategory, Group, ContentItem, 
    ContentItemPhoto, DisplayType, VideoCard, VideoCardReference
)
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
            return mark_safe(f'<img src="{obj.photo.url}" style="max-height: 80px; max-width: 120px;">')
        return "—"
    photo_preview.short_description = 'Превью'

class ContentItemAdminForm(forms.ModelForm):
    """Форма с надёжной сменой категории"""
    class Meta:
        model = ContentItem
        fields = ['category', 'subcategory', 'group', 'display_type', 'full_text']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['category'].queryset = Category.objects.order_by('order', 'name')

        # Определяем категорию из POST (если пользователь меняет) или из instance
        category_id = None
        if self.data and self.data.get('category'):
            try:
                category_id = int(self.data.get('category'))
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.category:
            category_id = self.instance.category.id

        # Фильтруем подкатегории под текущую категорию
        if category_id:
            self.fields['subcategory'].queryset = Subcategory.objects.filter(
                category_id=category_id
            ).order_by('name')
        else:
            self.fields['subcategory'].queryset = Subcategory.objects.select_related('category').order_by(
                'category__order', 'category__name', 'name'
            )

        # Если категория изменилась — очищаем подкатегорию (чтобы не было конфликта)
        if self.instance.pk and category_id:
            old_category_id = self.instance.category_id if self.instance.category_id else None
            if old_category_id and old_category_id != category_id:
                # Категория реально изменилась — сбрасываем подкатегорию
                self.initial['subcategory'] = None
                if self.data:
                    self.data = self.data.copy()
                    self.data['subcategory'] = ''

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        subcategory = cleaned_data.get('subcategory')

        # Если выбрана подкатегория — принудительно ставим её родительскую категорию
        if subcategory:
            cleaned_data['category'] = subcategory.category

        # Проверка целостности
        if subcategory and category and subcategory.category_id != category.id:
            raise ValidationError({
                'subcategory': 'Подкатегория не принадлежит выбранной категории.'
            })

        return cleaned_data

@admin.register(ContentItem)
class ContentItemAdmin(admin.ModelAdmin):
    form = ContentItemAdminForm
    inlines = [ContentItemPhotoInline]

    list_display = (
        'id', 'effective_category_safe', 'subcategory', 'group',
        'display_type', 'created_at', 'photo_preview_safe', 'photo_count'
    )
    list_display_links = ('id', 'effective_category_safe')
    list_filter = ('display_type', 'category', 'subcategory__category', 'group', 'created_at')
    search_fields = ('full_text', 'category__name', 'subcategory__name', 'group__name')
    ordering = ('-created_at',)

    readonly_fields = ('created_at',)

    fieldsets = (
        ('Привязка к категории', {
            'fields': ('category', 'subcategory', 'group'), 
        }),
	('Отображение фото', {
      	    'fields': ('display_type',),
    	    'description': '''
        	<strong>Правила количества фото:</strong><br>
        	• Одиночное — ровно 1 фото<br>
        	• Карусель — минимум 2 фото<br>
        	• Шторка — ровно 2 фото
    		''',
	}),
        ('Промпт', {
            'fields': ('full_text',),
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

    # Безопасные методы для list_display
    def effective_category_safe(self, obj):
        try:
            return obj.effective_category
        except:
            return "—"
    effective_category_safe.short_description = 'Категория'
    effective_category_safe.admin_order_field = 'category'

    def photo_preview_safe(self, obj):
        try:
            first = obj.photos.first()
            photo = first.photo if first else getattr(obj, 'photo', None)
            if photo:
                return mark_safe(f'<img src="{photo.url}" style="max-height: 60px;">')
        except:
            pass
        return "—"
    photo_preview_safe.short_description = 'Фото'

    def photo_count(self, obj):
        try:
            return obj.photos.count()
        except:
            return 0
    photo_count.short_description = 'Кол-во фото'

    def save_related(self, request, form, formsets, change):
        """Сохраняем inline-фото + сбрасываем кэш (срабатывает после save_model)"""
        super().save_related(request, form, formsets, change)
        cache.clear()

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'display_type', 'order')
    list_editable = ('display_type', 'order')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'category')
    list_filter = ('category',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('subcategories',)


class VideoCardReferenceInline(admin.TabularInline):
    model = VideoCardReference
    extra = 1
    fields = ['photo', 'order']

@admin.register(VideoCard)
class VideoCardAdmin(admin.ModelAdmin):
    list_display = ['id', 'prompt_description', 'category', 'created_at', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['prompt_description', 'copy_text']
    inlines = [VideoCardReferenceInline]
    fieldsets = (
        (None, {
            'fields': ('category', 'subcategory', 'group', 'video', 'video_poster')
        }),
        ('Тексты', {
            'fields': ('prompt_description', 'copy_text')
        }),
        ('Настройки', {
            'fields': ('is_active',)
        }),
    )