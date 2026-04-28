# content/models.py
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
import os


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Описание")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок в фильтрах")

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

    photo = models.ImageField(upload_to='photos/', verbose_name="Фото")
    full_text = models.TextField(verbose_name="Текст для копирования")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Карточка"
        verbose_name_plural = "Карточки"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.effective_category.name} — {self.full_text[:60]}..."

    @property
    def effective_category(self):
        """Используется в шаблонах и админке"""
        if self.subcategory:
            return self.subcategory.category
        return self.category

    def delete(self, *args, **kwargs):
        """Удаляем файл фото при удалении карточки"""
        if self.photo:
            try:
                if os.path.isfile(self.photo.path):
                    os.remove(self.photo.path)
            except Exception:
                pass  # файл уже удалён или ошибка доступа
        super().delete(*args, **kwargs)


# ====================== Signal для queryset.delete() ======================
@receiver(post_delete, sender=ContentItem)
def delete_photo_on_delete(sender, instance, **kwargs):
    """Дополнительная гарантия удаления файла"""
    if instance.photo:
        try:
            if os.path.isfile(instance.photo.path):
                os.remove(instance.photo.path)
        except Exception:
            pass
