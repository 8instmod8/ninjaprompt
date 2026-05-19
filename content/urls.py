from django.urls import path
from . import views

app_name = 'content'

urlpatterns = [
    path('', views.home, name='home'),    
    path('prompts/', views.content_list, name='content_list'), 

    # Группы — должны быть выше общих slug!
    path('group/<slug:slug>/', views.group_detail, name='group_detail'),
    
    # === ВИДЕО ===
    path('videos/', views.video_list, name='video_list'),
    path('api/copy-video/<int:pk>/', views.copy_video_card, name='copy_video_card'),
    
    path('<slug:slug>/', views.category_detail, name='category_detail'),
    path('<slug:category_slug>/<slug:subcategory_slug>/', 
         views.subcategory_detail, name='subcategory_detail'),
    
    path('api/copy/<int:pk>/', views.copy_content, name='copy_content'),
    path('api/me/', views.whoami, name='whoami'),
]
