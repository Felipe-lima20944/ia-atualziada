# Arquivo: core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # URL para a página inicial
    path('', views.home, name='home'),
    
    # URL para a página 'Sobre'
    path('sobre/', views.about, name='about'),
    
    # URL para a página 'Contato', agora apontando para a nova view `contact_view`
    path('contato/', views.contact_view, name='contact'),
    
    path('blog/', views.blog, name='blog'),
    
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),

    path('blog/', views.blog, name='blog'),
    # NOVO: Rota para listar posts por categoria.
    # O <slug:category_slug> captura o slug da categoria na URL.
    path('blog/categoria/<slug:category_slug>/', views.blog, name='blog_by_category'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),

]
