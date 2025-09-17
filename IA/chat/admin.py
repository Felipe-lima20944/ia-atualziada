from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import (
    User, PerfilUsuario, PersonalidadeIA, ModeloIA,
    Conversa, Mensagem, HistoricoTreinamento,
    Plano, Assinatura, Transacao, UsoDeTokens
)

# Inlines para facilitar a visualização e edição de dados relacionados
class PerfilUsuarioInline(admin.StackedInline):
    """Permite editar o perfil do usuário diretamente na página do usuário."""
    model = PerfilUsuario
    can_delete = False
    verbose_name = "perfil"
    verbose_name_plural = "perfis"

class TransacaoInline(admin.StackedInline):
    """Permite ver e adicionar transações diretamente na página da assinatura."""
    model = Transacao
    extra = 0
    verbose_name = "transação"
    verbose_name_plural = "transações"
    readonly_fields = ('data_transacao', 'id_transacao_gateway')

class AssinaturaInline(admin.StackedInline):
    """Permite editar a assinatura do usuário diretamente na página do usuário."""
    model = Assinatura
    can_delete = False
    verbose_name = "assinatura"
    verbose_name_plural = "assinaturas"
    fields = ('plano', 'status', 'data_renovacao', 'data_inicio', 'data_cancelamento')
    readonly_fields = ('data_inicio',)
    autocomplete_fields = ['plano']


@admin.register(User)
class CustomUserAdmin(AuthUserAdmin):
    """
    Personaliza a administração do modelo de usuário para incluir
    os campos personalizados e inlines de perfil e assinatura.
    """
    inlines = [PerfilUsuarioInline, AssinaturaInline]

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
        (
            _("Preferências do usuário"),
            {
                "fields": (
                    "permite_coleta_dados",
                    "tema_escuro",
                    "ultima_atividade",
                ),
            },
        ),
    )

    list_display = (
        'username',
        'email',
        'is_staff',
        'is_active',
        'get_plano',
        'ultima_atividade',
    )
    list_filter = (
        'is_staff',
        'is_superuser',
        'is_active',
        'groups',
        'assinatura__plano',
        'assinatura__status'
    )
    search_fields = ('username', 'email')
    readonly_fields = ('last_login', 'date_joined', 'ultima_atividade',)
    
    @admin.display(description='Plano')
    def get_plano(self, obj):
        """Exibe o nome do plano da assinatura do perfil do usuário."""
        try:
            return obj.assinatura.plano.nome
        except (AttributeError, Assinatura.DoesNotExist):
            return "Nenhum"


@admin.register(Plano)
class PlanoAdmin(admin.ModelAdmin):
    """Personalização do admin para o modelo Plano."""
    list_display = ('nome', 'preco_mensal', 'tokens_mensais', 'limite_conversas', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('nome',)
    filter_horizontal = ('personalidades_exclusivas',)


@admin.register(Assinatura)
class AssinaturaAdmin(admin.ModelAdmin):
    """Personalização do admin para o modelo Assinatura."""
    inlines = [TransacaoInline]
    list_display = ('usuario', 'plano', 'status', 'data_inicio', 'data_renovacao', 'data_cancelamento')
    list_filter = ('plano', 'status')
    search_fields = ('usuario__username', 'plano__nome')
    readonly_fields = ('data_inicio',)
    autocomplete_fields = ['usuario', 'plano']


@admin.register(Transacao)
class TransacaoAdmin(admin.ModelAdmin):
    """Admin para o novo modelo de Transação."""
    list_display = ('assinatura', 'valor', 'status', 'data_transacao')
    list_filter = ('status', 'data_transacao')
    search_fields = ('assinatura__usuario__username', 'id_transacao_gateway')
    readonly_fields = ('data_transacao', 'id_transacao_gateway')
    autocomplete_fields = ['assinatura']


@admin.register(UsoDeTokens)
class UsoDeTokensAdmin(admin.ModelAdmin):
    """Admin para o novo modelo de Uso de Tokens."""
    list_display = ('usuario', 'mes_ano', 'tokens_consumidos')
    list_filter = ('mes_ano',)
    search_fields = ('usuario__username', 'mes_ano')
    readonly_fields = ('mes_ano',)
    autocomplete_fields = ['usuario']


@admin.register(PersonalidadeIA)
class PersonalidadeIAAdmin(admin.ModelAdmin):
    """Personalização do admin para o modelo PersonalidadeIA."""
    # <<== Adicionando o campo 'modelo_ia' às listas de exibição e edição
    list_display = ('nome', 'descricao', 'ativo', 'alinhamento', 'modelo_ia')
    list_filter = ('ativo', 'alinhamento', 'modelo_ia')
    search_fields = ('nome', 'descricao', 'tom', 'prompt_sistema')
    readonly_fields = ('criado_em',)
    fields = (
        'nome', 'descricao', 'prompt_sistema', 'alinhamento', 'tom',
        'foto_ia', 'etica', 'empatia', 'restricoes', 'ativo',
        'modelo_ia', # <<== O campo agora está na tupla de 'fields'
        'criado_em'
    )
    # Adicionando o autocomplete para o campo modelo_ia para melhorar a usabilidade
    autocomplete_fields = ['modelo_ia']


@admin.register(ModeloIA)
class ModeloIAAdmin(admin.ModelAdmin):
    """Personalização do admin para o modelo ModeloIA."""
    list_display = ('nome', 'provedor', 'contexto_max', 'ativo', 'custo_input_mil_tokens', 'custo_output_mil_tokens')
    list_filter = ('ativo', 'provedor')
    search_fields = ('nome', 'provedor',)
    fields = ('nome', 'provedor', 'contexto_max', 'custo_input_mil_tokens', 'custo_output_mil_tokens', 'ativo')


@admin.register(Conversa)
class ConversaAdmin(admin.ModelAdmin):
    """Personalização do admin para o modelo Conversa com mensagens inlines."""
    list_display = (
        'titulo',
        'usuario',
        'personalidade',
        'modelo_ia',
        'total_mensagens',
        'total_tokens',
        'modificado_em',
        'excluida',
        'compartilhavel', # NOVO: Exibe o status de compartilhamento na lista
    )
    list_filter = (
        'excluida', 
        'compartilhavel', # NOVO: Filtra por conversas compartilháveis
        'criado_em', 
        'modificado_em', 
        'personalidade', 
        'modelo_ia',
    )
    search_fields = ('titulo', 'usuario__username')
    readonly_fields = (
        'id', 
        'uuid_compartilhamento', # NOVO: Torna o UUID somente leitura
        'total_mensagens', 
        'total_tokens', 
        'criado_em', 
        'modificado_em', 
        'excluida_em',
    )
    fields = (
        'usuario', 
        'titulo', 
        'personalidade', 
        'modelo_ia', 
        'temperatura', 
        'excluida',
        'uuid_compartilhamento', # NOVO: Exibe o UUID no formulário
        'compartilhavel', # NOVO: Permite ao admin marcar como compartilhável
    )
    autocomplete_fields = ['usuario', 'personalidade', 'modelo_ia']

@admin.register(Mensagem)
class MensagemAdmin(admin.ModelAdmin):
    """Personalização do admin para o modelo Mensagem."""
    list_display = (
        'conversa',
        'papel',
        'tipo_conteudo',
        'texto_curto',
        'tokens_utilizados',
        'criado_em',
        'feedback',
    )
    list_filter = ('papel', 'tipo_conteudo', 'feedback', 'criado_em')
    search_fields = ('texto', 'conversa__titulo')
    readonly_fields = ('id', 'tokens_utilizados', 'custo_estimado', 'criado_em', 'feedback')
    autocomplete_fields = ['conversa', 'parent_mensagem']

    @admin.display(description='Texto')
    def texto_curto(self, obj):
        """Exibe um resumo do texto da mensagem."""
        return obj.texto[:75] + '...' if len(obj.texto or '') > 75 else obj.texto


@admin.register(HistoricoTreinamento)
class HistoricoTreinamentoAdmin(admin.ModelAdmin):
    """Personalização do admin para o modelo HistoricoTreinamento."""
    list_display = ('conversa', 'modelo_destino', 'utilizado_em', 'anonimizada')
    list_filter = ('anonimizada', 'modelo_destino', 'utilizado_em')
    search_fields = ('conversa__titulo',)
    readonly_fields = ('utilizado_em',)
    autocomplete_fields = ['conversa']