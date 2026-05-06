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

    # === Новое поле ===
    DISPLAY_TYPE_CHOICES = [
        ('single', 'Одиночное фото'),
        ('carousel', 'Карусель'),
        ('slider', 'Шторка (До/После)'),
    ]

    display_type = models.CharField(
        max_length=20,
        choices=DISPLAY_TYPE_CHOICES,
        default='single',
        verbose_name="Тип отображения карточек"
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
        verbose_name="Фото"
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
        """Удаляем файл при удалении записи"""
        if self.photo:
            try:
                if os.path.isfile(self.photo.path):
                    os.remove(self.photo.path)
            except Exception:
                pass
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

    # Legacy-поле (будет удалено после data migration)
    photo = models.ImageField(
        upload_to='photos/',
        verbose_name="Фото (устарело)",
        null=True,
        blank=True,
        editable=False
    )

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

    @property
    def main_photo(self):
       first = self.photos.first()
       if first:
           return first.photo  # объект ImageField
       if self.photo:
           return self.photo  # legacy
       return None

    @property
    def has_multiple_photos(self):
        """Проверка для условного рендеринга"""
        return self.photos.count() > 1

    @property
    def display_type(self):
        """Тип отображения карточки"""
        if self.effective_category:
            return self.effective_category.display_type
        return 'single'

    @property
    def is_ugc(self):
        return self.display_type == 'carousel'

    @property
    def is_upscale(self):
        return self.display_type == 'slider'
    
    def delete(self, *args, **kwargs):
        """Удаляем все связанные фото при удалении карточки"""
        # Удаляем все фото из ContentItemPhoto
        for photo in self.photos.all():
            photo.delete()
        
        # Удаляем legacy фото
        if self.photo:
            try:
                if os.path.isfile(self.photo.path):
                    os.remove(self.photo.path)
            except Exception:
                pass
        super().delete(*args, **kwargs)


# ====================== Signals ======================
@receiver(post_delete, sender=ContentItem)
def delete_legacy_photo_on_delete(sender, instance, **kwargs):
    """Дополнительная гарантия для legacy-поля"""
    if instance.photo:
        try:
            if os.path.isfile(instance.photo.path):
                os.remove(instance.photo.path)
        except Exception:
            pass


@receiver(post_delete, sender=ContentItemPhoto)
def delete_photo_file(sender, instance, **kwargs):
    """Удаление файла новой модели"""
    if instance.photo:
        try:
            if os.path.isfile(instance.photo.path):
                os.remove(instance.photo.path)
        except Exception:
            pass
