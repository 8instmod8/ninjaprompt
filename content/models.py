# content/models.py
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
import os


class DisplayType(models.TextChoices):
    """Единый источник правды для типов отображения """
    SINGLE = 'single', 'Одиночное фото'
    CAROUSEL = 'carousel', 'Карусель'
    SLIDER = 'slider', 'Шторка (До/После)'


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Описание")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок в фильтрах")

    display_type = models.CharField(
        max_length=20,
        choices=DisplayType.choices,
        default=DisplayType.SINGLE,
        verbose_name="Тип отображения по умолчанию",
        help_text="Используется как значение по умолчанию при создании новых карточек"
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='subcategories',
        verbose_name="Верхнеуровневая категория"
    )
    name = models.CharField(max_length=100, verbose_name="Название подкатегории")
    slug = models.SlugField(verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Подкатегория"
        verbose_name_plural = "Подкатегории"
        ordering = ['name']
        unique_together = [['category', 'slug']]

    def __str__(self):
        return f"{self.category.name} → {self.name}"


class Group(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название группы")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    subcategories = models.ManyToManyField(
        Subcategory,
        related_name='groups',
        blank=True,
        verbose_name="Подкатегории в группе"
    )
    description = models.TextField(blank=True, verbose_name="Описание группы")

    class Meta:
        verbose_name = "Группа карточек"
        verbose_name_plural = "Группы карточек"
        ordering = ['name']

    def __str__(self):
        return self.name


class ContentItemPhoto(models.Model):
    """Модель для хранения нескольких фото на одну карточку"""
    content_item = models.ForeignKey(
        'ContentItem',
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name="Карточка"
    )
    photo = models.ImageField(
        upload_to='photos/multiple/%Y/%m/%d/',
        verbose_name="Фото",
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp', 'gif'])],
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок отображения")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Фото карточки"
        verbose_name_plural = "Фото карточек"
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"Фото #{self.order} для {self.content_item}"

    def delete(self, *args, **kwargs):
        """Файл удаляется автоматически через сигнал post_delete"""
        super().delete(*args, **kwargs)


class ContentItem(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='direct_cards',
        verbose_name="Категория",
        null=True,
        blank=True
    )
    subcategory = models.ForeignKey(
        Subcategory,
        on_delete=models.CASCADE,
        related_name='cards',
        verbose_name="Подкатегория",
        null=True,
        blank=True
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cards',
        verbose_name="Группа"
    )

    display_type = models.CharField(
        max_length=20,
        choices=DisplayType.choices,
        default=DisplayType.SINGLE,
        verbose_name="Тип отображения фото",
        help_text="Выбирается индивидуально для каждой карточки (независимо от категории)",
    )

    full_text = models.TextField(verbose_name="Текст для копирования")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Карточка"
        verbose_name_plural = "Карточки"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['category', 'subcategory']),
        ]

    def __str__(self):
        return f"{self.effective_category.name if self.effective_category else 'Без категории'} — {self.full_text[:60]}..."

    @property
    def effective_category(self):
        if self.subcategory:
            return self.subcategory.category
        return self.category

    @property
    def main_photo(self):
        first = self.photos.first()
        return first.photo if first else None

    @property
    def has_multiple_photos(self):
        return self.photos.count() > 1

    @property
    def is_ugc(self):
        return self.display_type == DisplayType.CAROUSEL

    @property
    def is_upscale(self):
        return self.display_type == DisplayType.SLIDER

    def delete(self, *args, **kwargs):
        """Удаляем все связанные фото при удалении карточки"""
        for photo in self.photos.all():
            photo.delete()
        super().delete(*args, **kwargs)


# === ВИДЕО-КАРТОЧКИ ===

class VideoCard(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, null=True, blank=True,
        related_name='video_cards', verbose_name="Категория"
    )
    subcategory = models.ForeignKey(
        Subcategory, on_delete=models.CASCADE, null=True, blank=True,
        related_name='video_cards', verbose_name="Подкатегория"
    )
    group = models.ForeignKey(
        Group, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='video_cards', verbose_name="Группа"
    )

    video = models.FileField(
        upload_to='videos/%Y/%m/%d/',
        verbose_name="Видео файл",
        validators=[FileExtensionValidator(['mp4', 'webm', 'mov'])],
    )
    video_poster = models.ImageField(
        upload_to='videos/posters/%Y/%m/%d/',
        blank=True, null=True,
        verbose_name="Постер (превью)",
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])],
    )

    prompt_description = models.TextField(
        verbose_name="Описание промпта (для отображения)"
    )
    copy_text = models.TextField(
        verbose_name="Текст для копирования"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        verbose_name = "Видео-карточка"
        verbose_name_plural = "Видео-карточки"
        ordering = ['-created_at']

    def __str__(self):
        return f"Видео: {self.prompt_description[:60]}..."


class VideoCardReference(models.Model):
    """Референсные фото к видео-карточке"""
    video_card = models.ForeignKey(
        VideoCard, on_delete=models.CASCADE,
        related_name='references', verbose_name="Видео-карточка"
    )
    photo = models.ImageField(
        upload_to='videos/references/%Y/%m/%d/',
        verbose_name="Референсное фото",
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])],
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")

    class Meta:
        verbose_name = "Референс видео-карточки"
        verbose_name_plural = "Референсы видео-карточек"
        ordering = ['order']

    def __str__(self):
        return f"Референс #{self.order}"


# ====================== Signals ======================
@receiver(post_delete, sender=ContentItemPhoto)
def delete_photo_file(sender, instance, **kwargs):
    """Удаление файла при удалении ContentItemPhoto"""
    if instance.photo:
        try:
            if os.path.isfile(instance.photo.path):
                os.remove(instance.photo.path)
        except Exception:
            pass