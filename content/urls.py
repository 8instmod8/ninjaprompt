from django.urls import path
from . import views

app_name = 'content'

urlpatterns = [
    # Это будет главная страница библиотеки — адрес /list/
    path('', views.content_list, name='content_list'),
    
    # Страница категории
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    
    # Страница группы
    path('group/<slug:slug>/', views.group_detail, name='group_detail'),
    
    # API для копирования промпта
    path('api/copy/<int:pk>/', views.copy_content, name='copy_content'),
    path('api/csrf/', views.get_csrf_token, name='get_csrf'),
]
