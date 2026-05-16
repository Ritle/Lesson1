from django.urls import path
from .import views

urlpatterns = [
    path('', views.index, name='index'),
    path('articles/', views.article_list, name='article_list'),
    path('article/<int:pk>/', views.article_detail, name='article_detail'),
    path('save/<int:pk>/', views.save_article, name='save_article'),
    path('unsave/<int:pk>/', views.unsave_article, name='unsave_article'),
    path('saved/', views.saved_articles, name='saved_articles')
]