# content/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db import models

from .models import ContentItem, Group, Subcategory, Category
from django.core.paginator import Paginator
from .forms import BulkImportForm

import os
from openpyxl import load_workbook
import zipfile
from django.conf import settings
from django.utils.text import slugify
from transliterate import translit

def home(request):
    from .models import ContentItem, ContentItemPhoto

    # Динамическое количество промптов
    total_prompts = ContentItem.objects.count()

    # Фото только из нужных категорий
    photos = ContentItemPhoto.objects.filter(
        content_item__category__slug__in=['photo-sessions', 'man-photo-sessions']
    ).select_related('content_item').order_by('-created_at')[:15]

    photo_urls = [photo.photo.url for photo in photos if photo.photo]

    return render(request, 'content/home.html', {
        'total_prompts': total_prompts,
        'photo_urls': photo_urls,
    })

@require_POST
@ratelimit(key='user', rate='10/m', block=True)
def copy_content(request, pk):
    try:
        item = ContentItem.objects.get(pk=pk)
        return JsonResponse({'success': True, 'text': item.full_text})
    except ContentItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Запись не найдена'}, status=404)


def content_list(request):
    items = ContentItem.objects.select_related(
        'category', 'subcategory__category', 'group'
    ).prefetch_related('photos').order_by('-created_at')  # ← оптимизация

    paginator = Paginator(items, 20)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    top_categories = Category.objects.filter(order__gt=0).order_by('order')
    categories = Subcategory.objects.select_related('category').order_by('category__order', 'name')

    return render(request, 'content/list.html', {
        'items': page_obj,
        'top_categories': top_categories,
        'categories': categories,
        'paginator': paginator,
        'page_obj': page_obj,
        'is_admin': request.user.is_superuser,
    })


def category_detail(request, slug):
    """Топ-категория"""
    top_category = get_object_or_404(Category, slug=slug)

    items = ContentItem.objects.filter(
        models.Q(category=top_category) | models.Q(subcategory__category=top_category)
    ).select_related(
        'category', 'subcategory__category', 'group'
    ).prefetch_related('photos').order_by('-created_at')  # ← оптимизация

    paginator = Paginator(items, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    top_categories = Category.objects.filter(order__gt=0).order_by('order')
    subcategories = Subcategory.objects.filter(category=top_category).order_by('name')

    return render(request, 'content/category_detail.html', {
        'category': top_category,
        'top_category': top_category,
        'is_top_category': True,
        'items': page_obj,
        'categories': subcategories,
        'top_categories': top_categories,
        'paginator': paginator,
        'page_obj': page_obj,
        'is_admin': request.user.is_superuser,
    })


def subcategory_detail(request, category_slug, subcategory_slug):
    """Подкатегория"""
    top_category = get_object_or_404(Category, slug=category_slug)
    subcategory = get_object_or_404(Subcategory, slug=subcategory_slug, category=top_category)

    items = ContentItem.objects.filter(subcategory=subcategory)\
        .select_related('category', 'group')\
        .prefetch_related('photos').order_by('-created_at')  # ← оптимизация

    paginator = Paginator(items, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    top_categories = Category.objects.filter(order__gt=0).order_by('order')
    subcategories = Subcategory.objects.filter(category=top_category).order_by('name')

    return render(request, 'content/category_detail.html', {
        'category': subcategory,
        'top_category': top_category,
        'is_top_category': False,
        'items': page_obj,
        'categories': subcategories,
        'top_categories': top_categories,
        'paginator': paginator,
        'page_obj': page_obj,
        'is_admin': request.user.is_superuser,
    })


def group_detail(request, slug):
    group = get_object_or_404(Group, slug=slug)
    items = ContentItem.objects.filter(group=group)\
        .select_related('category', 'subcategory__category')\
        .prefetch_related('photos').order_by('-created_at')  # ← оптимизация

    top_categories = Category.objects.filter(order__gt=0).order_by('order')
    categories = Subcategory.objects.select_related('category').order_by('category__order', 'name')

    return render(request, 'content/group_detail.html', {
        'group': group,
        'items': items,  # здесь не пагинация (оставил как было)
        'categories': categories,
        'top_categories': top_categories,
        'is_admin': request.user.is_superuser,
    })


# ====================== Bulk Import ======================
@staff_member_required
def bulk_import_view(request):
    """Массовый импорт — поддержка нескольких фото через запятую"""
    if request.method == 'POST':
        form = BulkImportForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']
            photos_zip = request.FILES.get('photos_zip')

            if photos_zip:
                extract_path = os.path.join(settings.MEDIA_ROOT, 'photos')
                os.makedirs(extract_path, exist_ok=True)
                with zipfile.ZipFile(photos_zip, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
                messages.info(request, "✅ Фотографии успешно распакованы")

            wb = load_workbook(excel_file, data_only=True)
            sheet = wb.active

            created = 0
            errors = []

            for row_num, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
                values = [str(cell).strip() if cell is not None else '' for cell in row]

                filename = values[0] if len(values) > 0 else ''
                category_name = values[1] if len(values) > 1 else ''
                subcategory_name = values[2] if len(values) > 2 else ''
                group_name = values[3] if len(values) > 3 else ''
                prompt = values[4] if len(values) > 4 else ''
                photos_str = values[5] if len(values) > 5 else ''  # ← НОВОЕ: несколько фото через запятую

                if not filename or not category_name or not prompt:
                    errors.append(f"Строка {row_num}: filename, category и prompt — обязательны")
                    continue

                try:
                    category = Category.objects.get(name__iexact=category_name)
                except Category.DoesNotExist:
                    errors.append(f"Строка {row_num}: категория «{category_name}» не найдена")
                    continue

                # ... (код создания subcategory и group — оставь как был)

                # Создаём карточку
                item = ContentItem.objects.create(
                    category=category,
                    subcategory=subcategory,
                    group=group,
                    full_text=prompt
                )

                # Добавляем фото (несколько через запятую или одно)
                photo_files = [f.strip() for f in photos_str.split(',') if f.strip()] if photos_str else [filename]
                
                for idx, photo_file in enumerate(photo_files):
                    photo_path = os.path.join('photos', photo_file)
                    full_path = os.path.join(settings.MEDIA_ROOT, photo_path)
                    
                    if os.path.exists(full_path):
                        ContentItemPhoto.objects.create(
                            content_item=item,
                            photo=photo_path,
                            order=idx
                        )
                    else:
                        errors.append(f"Строка {row_num}: файл {photo_file} не найден")

                created += 1

            if created:
                messages.success(request, f'✅ Успешно создано {created} карточек.')
            if errors:
                for err in errors[:15]:
                    messages.error(request, err)

            return redirect('admin:content_contentitem_changelist')

    else:
        form = BulkImportForm()

    return render(request, 'content/bulk_import.html', {'form': form})

