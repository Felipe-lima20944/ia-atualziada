from django.urls import path
from . import views

urlpatterns = [
    # Rotas de visualização da sua aplicação
    path('', views.ChatView.as_view(), name='chat_list_or_new'),
    path('chat/<uuid:conversa_id>/', views.ChatView.as_view(), name='carregar_conversa'),
    path('home/', views.home_page, name='home_page'),
    path('recursos/', views.recursos, name='recursos'),
    path('planos/', views.planos, name='planos'),
    path('contato/', views.contato, name='contato'),

    # Rotas de API da sua aplicação
    path('api/conversas/', views.listar_conversas, name='listar_conversas'),
    path('api/conversa/<uuid:conversa_id>/', views.carregar_conversa, name='carregar_conversa_api'),
    path('api/conversa/excluir/', views.excluir_conversa_api, name='excluir_conversa_api'),
    path('api/limpar/', views.limpar_conversas, name='limpar_conversas'),
    path('api/personalidades/', views.listar_personalidades, name='listar_personalidades'),
    path('api/status/', views.status_servico, name='status_servico'),
    path('api/feedback/<uuid:mensagem_id>/', views.enviar_feedback, name='enviar_feedback'),
    path('api/imagem/gerar/', views.gerar_imagem_api, name='gerar_imagem_api'),

    # --- ROTAS DE COMPARTILHAMENTO CORRIGIDAS ---
    # Rota da API para o frontend solicitar o link de compartilhamento.
    path('api/chat/compartilhar/<uuid:conversa_id>/', views.ativar_compartilhamento, name='ativar_compartilhamento'),

    # Rota pública para visualização de uma conversa.
    path('compartilhar/<uuid:uuid_compartilhamento>/', views.visualizar_conversa_compartilhada, name='visualizar_conversa_compartilhada'),
]