from django import forms

class BulkImportForm(forms.Form):
    excel_file = forms.FileField(
        label="Excel-файл (.xlsx)",
        help_text="Обязательные колонки: filename, category, prompt. Группа — необязательна."
    )
    
    photos_zip = forms.FileField(
        label="ZIP-архив с фотографиями (рекомендуется)",
        help_text="Все фото должны лежать в корне архива, без вложенных папок",
        required=False
    )