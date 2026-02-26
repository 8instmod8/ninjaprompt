from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']

    def __str__(self):
        return self.name


class Group(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название группы")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    categories = models.ManyToManyField(Category, related_name='groups', verbose_name="Категории в группе")
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
        related_name='cards',
        verbose_name="Категория"
    )
    group = models.ForeignKey(
        Group, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='cards',
        verbose_name="Группа (необязательно)"
    )
    
    photo = models.ImageField(upload_to='photos/', verbose_name="Фото")
    full_text = models.TextField(verbose_name="Текст для копирования")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Карточка"
        verbose_name_plural = "Карточки"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.category.name} — {self.full_text[:50]}..."


class CopyLog(models.Model):
    """Лог каждого копирования"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    content_item = models.ForeignKey(ContentItem, on_delete=models.CASCADE)
    copied_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        verbose_name = "Лог копирования"
        verbose_name_plural = "Логи копирований"
        ordering = ['-copied_at']

    def __str__(self):
        return f"{self.user} скопировал {self.content_item} в {self.copied_at}"