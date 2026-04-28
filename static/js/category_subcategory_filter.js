// content/static/content/js/category_subcategory_filter.js
document.addEventListener('DOMContentLoaded', function() {
    const categoryField = document.getElementById('id_category');
    const subcategoryField = document.getElementById('id_subcategory');

    if (!categoryField || !subcategoryField) return;

    // Сохраняем все оригинальные варианты подкатегорий
    const allOptions = Array.from(subcategoryField.options);

    function filterSubcategories() {
        const selectedCategoryId = categoryField.value;
        
        // Очищаем текущий список
        subcategoryField.innerHTML = '<option value="">---------</option>';

        if (!selectedCategoryId) return;

        allOptions.forEach(option => {
            if (option.value === '') return;
            
            // data-category-id добавляется Django автоматически при render
            if (option.dataset.categoryId === selectedCategoryId || 
                option.dataset.categoryId === undefined) {  // fallback
                subcategoryField.appendChild(option.cloneNode(true));
            }
        });
    }

    // Событие изменения категории
    categoryField.addEventListener('change', filterSubcategories);

    // Инициализация при редактировании
    if (categoryField.value) {
        setTimeout(filterSubcategories, 300);
    }
});
