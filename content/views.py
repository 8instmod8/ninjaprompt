from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django_ratelimit.decorators import ratelimit
from .models import ContentItem, Group, Category
from django.core.paginator import Paginator

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect
from django.contrib import messages
from openpyxl import load_workbook
import os
from .forms import BulkImportForm
from django.utils.text import slugify
from django.utils import timezone
import zipfile
from django.conf import settings


@login_required
@require_POST
@ratelimit(key='user', rate='10/m', block=True)
def copy_content(request, pk):
    try:
        item = ContentItem.objects.get(pk=pk)
        return JsonResponse({'success': True, 'text': item.full_text})
    except ContentItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Запись не найдена'}, status=404)


@login_required
def content_list(request):
    # Все карточки вместе (групповые + одиночные) с сортировкой по дате
    all_items = ContentItem.objects.select_related('category', 'group').order_by('-created_at')

    # Пагинация — 20 карточек на страницу
    paginator = Paginator(all_items, 20)
    page_number = request.GET.get('page', 1)
    items_page = paginator.get_page(page_number)

    categories = Category.objects.all()

    return render(request, 'content/list.html', {
        'items': items_page,
        'categories': categories,
        'is_admin': request.user.is_superuser,
        'paginator': paginator,
        'page_obj': items_page,
    })


@login_required
def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    items = ContentItem.objects.filter(category=category).select_related('group')
    categories = Category.objects.all()

    # Пагинация — 20 карточек на страницу
    paginator = Paginator(items, 20)
    page_number = request.GET.get('page')
    items_page = paginator.get_page(page_number)

    return render(request, 'content/category_detail.html', {
        'category': category,
        'items': items_page,
        'categories': categories,
        'is_admin': request.user.is_superuser,
        'paginator': paginator,
        'page_obj': items_page,
    })


@login_required
def group_detail(request, slug):
    group = get_object_or_404(Group, slug=slug)
    items = ContentItem.objects.filter(group=group).select_related('category')
    categories = Category.objects.all()

    return render(request, 'content/group_detail.html', {
        'group': group,
        'items': items,
        'categories': categories,
        'is_admin': request.user.is_superuser
    })


@staff_member_required
def bulk_import_view(request):
    if request.method == 'POST':
        form = BulkImportForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']
            photos_zip = request.FILES.get('photos_zip')

            # Распаковка фотографий из ZIP
            if photos_zip:
                extract_path = os.path.join(settings.MEDIA_ROOT, 'photos')
                os.makedirs(extract_path, exist_ok=True)
                with zipfile.ZipFile(photos_zip, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
                messages.info(request, "✅ Фотографии из ZIP успешно распакованы")

            wb = load_workbook(excel_file, data_only=True)
            sheet = wb.active

            created = 0
            errors = []

            for row_num, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
                values = [str(cell).strip() if cell is not None else '' for cell in row]

                filename = values[0]
                category_input = values[1]
                group_name = values[2] if len(values) > 2 else ''
                prompt = values[3] if len(values) > 3 else ''

                if not filename or not category_input or not prompt:
                    errors.append(f"Строка {row_num}: не заполнены обязательные поля")
                    continue

                try:
                    category = Category.objects.get(slug__iexact=category_input)
                except Category.DoesNotExist:
                    errors.append(f"Строка {row_num}: категория «{category_input}» не найдена")
                    continue

                group = None
                if group_name:
                    group = Group.objects.filter(name__iexact=group_name).first()
                    if not group:
                        from transliterate import translit
                        try:
                            base_slug = translit(group_name, 'ru', reversed=True)
                            base_slug = slugify(base_slug)
                        except:
                            base_slug = slugify(group_name)

                        if not base_slug:
                            base_slug = "group-" + str(int(timezone.now().timestamp()))

                        slug = base_slug
                        counter = 2
                        while Group.objects.filter(slug=slug).exists():
                            slug = f"{base_slug}-{counter}"
                            counter += 1

                        group = Group.objects.create(
                            name=group_name,
                            slug=slug,
                            description=f"Автоматически создана при импорте ({timezone.now().strftime('%d.%m.%Y')})"
                        )
                        messages.info(request, f'Создана новая группа: "{group_name}" → slug: {slug}')

                photo_path = os.path.join('photos', filename)
                full_path = os.path.join(settings.MEDIA_ROOT, photo_path)

                if not os.path.exists(full_path):
                    errors.append(f"Строка {row_num}: файл не найден — {filename}")
                    continue

                ContentItem.objects.create(
                    category=category,
                    group=group,
                    photo=photo_path,
                    full_text=prompt
                )
                created += 1

            if created:
                messages.success(request, f'✅ Успешно создано {created} карточек.')
            if errors:
                messages.error(request, f'❌ Найдено ошибок: {len(errors)}')
                for err in errors[:20]:
                    messages.error(request, err)
                if len(errors) > 20:
                    messages.error(request, f'... и ещё {len(errors)-20} ошибок')

            return redirect('admin:content_contentitem_changelist')

    else:
        form = BulkImportForm()

    return render(request, 'content/bulk_import.html', {'form': form})