from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView

# Импорты для обслуживания медиа-файлов (фото в карточках)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Главная страница сайта — всегда форма входа (login.html)
    path('', LoginView.as_view(
        template_name='login.html',
        redirect_authenticated_user=True,
    ), name='login'),
    
    # Кнопка «Выход»
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    
    # Все страницы библиотеки промптов
    path('list/', include('content.urls')),
]

# ====================== ОБСЛУЖИВАНИЕ МЕДИА-ФАЙЛОВ ======================
# Фото будут отображаться только в режиме DEBUG=True
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
