from django.db import models
import uuid
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    """
    Modelo de usuário personalizado. Mantém a compatibilidade com o sistema de autenticação
    do Django. Dados de perfil mais detalhados são armazenados em um modelo separado.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Resolvendo o conflito de relacionamento com a aplicação 'auth'
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions '
                  'granted to each of their groups.',
        related_name="chat_user_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="chat_user_permissions_set",
        related_query_name="user",
    )

    permite_coleta_dados = models.BooleanField(
        default=True,
        help_text="Se o usuário permite que suas conversas sejam usadas para melhorar o modelo."
    )

    tema_escuro = models.BooleanField(
        default=False,
        help_text="Se o usuário prefere o tema escuro na interface."
    )

    ultima_atividade = models.DateTimeField(
        auto_now=True,
        help_text="Data e hora da última atividade do usuário."
    )

    class Meta:
        verbose_name = "usuário"
        verbose_name_plural = "usuários"

    def __str__(self):
        return self.username


class PerfilUsuario(models.Model):
    """
    Modelo complementar ao usuário para dados de perfil mais específicos,
    como foto e informações pessoais.
    """
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil',
        help_text="O usuário associado a este perfil."
    )
    bio = models.TextField(
        blank=True,
        help_text="Uma breve biografia sobre o usuário."
    )
    foto_perfil = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True,
        help_text="Foto de perfil do usuário."
    )
    data_aniversario = models.DateField(
        blank=True,
        null=True,
        help_text="Data de aniversário do usuário."
    )

    class Meta:
        verbose_name = "perfil do usuário"
        verbose_name_plural = "perfis dos usuários"

    def __str__(self):
        return f"Perfil de {self.usuario.username}"


class ModeloIA(models.Model):
    """
    Modelo para gerenciar os diferentes modelos de IA utilizados.
    Isso permite armazenar metadados, como custo, de forma centralizada.
    """
    nome = models.CharField(
        max_length=100,
        unique=True,
        help_text="Nome do modelo de IA (ex: 'gemini-2.5-flash-preview')."
    )

    provedor = models.CharField(
        max_length=50,
        help_text="O provedor ou empresa responsável pelo modelo."
    )

    contexto_max = models.PositiveIntegerField(
        default=0,
        help_text="O número máximo de tokens que o modelo pode 'lembrar'."
    )

    custo_input_mil_tokens = models.DecimalField(
        max_digits=8,
        decimal_places=6,
        default=0.0,
        help_text="Custo estimado por 1000 tokens de entrada (em dólares)."
    )

    custo_output_mil_tokens = models.DecimalField(
        max_digits=8,
        decimal_places=6,
        default=0.0,
        help_text="Custo estimado por 1000 tokens de saída (em dólares)."
    )

    ativo = models.BooleanField(
        default=True,
        help_text="Se este modelo está ativo e disponível para uso."
    )

    class Meta:
        verbose_name = "modelo de IA"
        verbose_name_plural = "modelos de IA"
        ordering = ['nome']

    def __str__(self):
        return self.nome


class PersonalidadeIA(models.Model):
    """
    Modelo para definir diferentes personalidades que a IA pode assumir.
    Adicionado campo para foto ou avatar da personalidade.
    """
    nome = models.CharField(
        max_length=50,
        unique=True,
        help_text="Nome identificador da personalidade (ex: 'assistente', 'criativo')."
    )

    descricao = models.CharField(
        max_length=255,
        help_text="Descrição breve da personalidade e seu comportamento."
    )

    prompt_sistema = models.TextField(
        help_text="Instrução do sistema para guiar a personalidade da IA. Ex: 'Você é um assistente prestativo...'"
    )

    alinhamento = models.CharField(
        max_length=50,
        help_text="Alinhamento comportamental da IA (ex: 'ALINHADO', 'NEUTRO_MAL')."
    )

    tom = models.TextField(
        help_text="Tom de voz e estilo da IA (ex: 'Positivo, Ajudante, Empático')."
    )

    foto_ia = models.ImageField(
        upload_to='ai_personalities/',
        blank=True,
        null=True,
        help_text="Foto ou avatar da personalidade da IA."
    )

    etica = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Nível de ética da IA (0.0 = sem ética, 1.0 = totalmente ético)."
    )

    empatia = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Nível de empatia da IA (0.0 = sem empatia, 1.0 = totalmente empático)."
    )

    restricoes = models.TextField(
        help_text="Restrições e regras comportamentais específicas."
    )

    ativo = models.BooleanField(
        default=True,
        help_text="Se esta personalidade está disponível para uso."
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    modelo_ia = models.ForeignKey(
        ModeloIA,
        on_delete=models.SET_NULL,  # Ajuste para não apagar personalidades se o modelo for removido
        related_name='personalidades',
        null=True,  # Permite que seja nulo
        blank=True, # Permite que seja vazio no admin
        help_text="O modelo de IA associado a esta personalidade."
    )

    class Meta:
        verbose_name = "personalidade IA"
        verbose_name_plural = "personalidades IA"
        ordering = ['nome']

    def __str__(self):
        return self.nome


# --- MODELOS DE PLANO E ASSINATURA ---
class Plano(models.Model):
    """
    Define os diferentes planos de assinatura disponíveis para os usuários.
    """
    nome = models.CharField(
        max_length=50,
        unique=True,
        help_text="Nome do plano (ex: 'Grátis', 'Pro', 'Premium')."
    )
    descricao = models.TextField(
        help_text="Descrição detalhada dos benefícios do plano."
    )
    preco_mensal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Preço mensal do plano em R$."
    )
    tokens_mensais = models.PositiveIntegerField(
        default=0,
        help_text="Número de tokens de IA incluídos por mês."
    )
    limite_conversas = models.PositiveIntegerField(
        default=0,
        help_text="Limite de conversas ativas (0 = ilimitado)."
    )
    # Relação N:N para associar personalidades específicas a planos
    personalidades_exclusivas = models.ManyToManyField(
        PersonalidadeIA,
        blank=True,
        help_text="Personalidades de IA exclusivas para este plano."
    )
    ativo = models.BooleanField(
        default=True,
        help_text="Indica se o plano está disponível para novas assinaturas."
    )

    class Meta:
        verbose_name = "plano"
        verbose_name_plural = "planos"
        ordering = ['preco_mensal']

    def __str__(self):
        return self.nome


class Assinatura(models.Model):
    """
    Gerencia a assinatura de um usuário a um plano específico.
    """
    STATUS_CHOICES = [
        ('ativa', 'Ativa'),
        ('cancelada', 'Cancelada'),
        ('pendente', 'Pendente'),
        ('expirada', 'Expirada'),
    ]

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assinatura',
        help_text="O usuário que possui esta assinatura."
    )
    plano = models.ForeignKey(
        Plano,
        on_delete=models.SET_NULL,
        null=True,
        help_text="O plano ao qual o usuário está assinado."
    )
    data_inicio = models.DateTimeField(
        auto_now_add=True,
        help_text="Data de início da assinatura."
    )
    data_renovacao = models.DateTimeField(
        help_text="Próxima data de renovação da assinatura."
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='ativa',
        help_text="Status atual da assinatura."
    )
    data_cancelamento = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Data em que a assinatura foi cancelada, se aplicável."
    )

    class Meta:
        verbose_name = "assinatura"
        verbose_name_plural = "assinaturas"

    def __str__(self):
        return f"Assinatura de {self.usuario.username} - Plano {self.plano.nome if self.plano else 'Nenhum'}"


class Transacao(models.Model):
    """
    NOVO MODELO: Registra os detalhes de cada transação de pagamento.
    Mais detalhado que apenas um ID na Assinatura.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assinatura = models.ForeignKey(
        Assinatura,
        on_delete=models.CASCADE,
        related_name='transacoes',
        help_text="A assinatura à qual esta transação está vinculada."
    )
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Valor do pagamento."
    )
    data_transacao = models.DateTimeField(
        auto_now_add=True,
        help_text="Data e hora da transação."
    )
    id_transacao_gateway = models.CharField(
        max_length=255,
        unique=True,
        help_text="ID único da transação no gateway de pagamento (ex: Stripe)."
    )
    status = models.CharField(
        max_length=50,
        help_text="Status da transação (ex: 'sucesso', 'falha', 'pendente')."
    )

    class Meta:
        verbose_name = "transação"
        verbose_name_plural = "transações"
        ordering = ['-data_transacao']

    def __str__(self):
        return f"Transação {self.id_transacao_gateway} - {self.valor}"


class UsoDeTokens(models.Model):
    """
    NOVO MODELO: Controla o consumo mensal de tokens por usuário.
    Permite resetar o contador a cada ciclo de pagamento.
    """
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uso_tokens',
        help_text="O usuário que consumiu os tokens."
    )
    mes_ano = models.CharField(
        max_length=7,  # Ex: '2025-09'
        help_text="Mês e ano de referência para o consumo de tokens."
    )
    tokens_consumidos = models.PositiveIntegerField(
        default=0,
        help_text="Total de tokens consumidos neste mês."
    )

    class Meta:
        verbose_name = "uso de token"
        verbose_name_plural = "uso de tokens"
        unique_together = ('usuario', 'mes_ano')
        ordering = ['-mes_ano']

    def __str__(self):
        return f"Uso de tokens de {self.usuario.username} em {self.mes_ano}"


class Conversa(models.Model):
    """
    Representa uma única conversa de chat com metadados completos.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Identificador único da conversa."
    )

    titulo = models.CharField(
        max_length=255,
        default="Nova Conversa",
        help_text="Título da conversa para exibição na interface."
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conversas',
        help_text="O usuário proprietário desta conversa."
    )

    personalidade = models.ForeignKey(
        PersonalidadeIA,
        on_delete=models.PROTECT,
        related_name='conversas',
        help_text="A personalidade da IA usada nesta conversa."
    )
    
    personalidade_inicial = models.ForeignKey(
        PersonalidadeIA,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='conversas_iniciais',
        help_text="A personalidade da IA que iniciou a conversa."
    )

    modelo_ia = models.ForeignKey(
        ModeloIA,
        on_delete=models.PROTECT,
        related_name='conversas',
        help_text="O modelo de IA usado nesta conversa."
    )

    temperatura = models.FloatField(
        default=0.7,
        validators=[MinValueValidator(0.0), MaxValueValidator(2.0)],
        help_text="Valor de temperatura usado para a geração de respostas (0.0 a 2.0)."
    )

    total_mensagens = models.IntegerField(
        default=0,
        help_text="Número total de mensagens nesta conversa."
    )

    total_tokens = models.PositiveIntegerField(
        default=0,
        help_text="Número total de tokens utilizados nesta conversa."
    )

    criado_em = models.DateTimeField(
        auto_now_add=True,
        help_text="Data e hora em que a conversa foi criada."
    )

    modificado_em = models.DateTimeField(
        auto_now=True,
        help_text="Data e hora da última atualização da conversa."
    )

    excluida = models.BooleanField(
        default=False,
        help_text="Indica se a conversa foi excluída (soft delete)."
    )

    excluida_em = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Data e hora em que a conversa foi marcada como excluída."
    )

    # NOVO CAMPO: UUID para compartilhar a conversa de forma segura.
    uuid_compartilhamento = models.UUIDField(
        default=uuid.uuid4, 
        editable=False, 
        unique=True,
        help_text="Identificador único e não adivinhavel para links de compartilhamento."
    )

    # NOVO CAMPO: Indica se a conversa pode ser visualizada publicamente via link.
    compartilhavel = models.BooleanField(
        default=False,
        help_text="Se a conversa pode ser acessada através de um link de compartilhamento público."
    )

    class Meta:
        verbose_name = "conversa"
        verbose_name_plural = "conversas"
        ordering = ['-modificado_em']
        indexes = [
            models.Index(fields=['usuario', 'modificado_em']),
            models.Index(fields=['excluida', 'modificado_em']),
            models.Index(fields=['uuid_compartilhamento']), # Adicione um índice para buscas rápidas
        ]

    def __str__(self):
        return self.titulo or f"Conversa {self.id}"

    def delete(self, using=None, keep_parents=False):
        """Implementação de soft delete."""
        self.excluida = True
        self.excluida_em = timezone.now()
        self.save()

    def restaurar(self):
        """Restaura uma conversa excluída."""
        self.excluida = False
        self.excluida_em = None
        self.save()


class Mensagem(models.Model):
    """
    Representa uma única mensagem dentro de uma conversa.
    """
    ROLES = [
        ('user', 'Usuário'),
        ('assistant', 'Assistente'),
        ('system', 'Sistema'),
        ('tool', 'Ferramenta'),
    ]

    TIPOS_CONTEUDO = [
        ('text', 'Texto'),
        ('image', 'Imagem'),
        ('file', 'Arquivo'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Identificador único da mensagem."
    )

    conversa = models.ForeignKey(
        Conversa,
        on_delete=models.CASCADE,
        related_name='mensagens',
        help_text="A conversa à qual esta mensagem pertence."
    )

    parent_mensagem = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='respostas_alternativas',
        help_text="Mensagem 'pai' para respostas alternativas."
    )

    papel = models.CharField(
        max_length=10,
        choices=ROLES,
        help_text="O papel de quem enviou a mensagem (user, assistant ou system)."
    )

    tipo_conteudo = models.CharField(
        max_length=10,
        choices=TIPOS_CONTEUDO,
        default='text',
        help_text="Tipo de conteúdo da mensagem (ex: 'text', 'image')."
    )

    texto = models.TextField(
        help_text="O conteúdo da mensagem.",
        null=True,
        blank=True
    )

    dados_conteudo = models.FileField(
        upload_to='chat_uploads/',
        help_text="O arquivo associado a esta mensagem, se houver.",
        null=True,
        blank=True
    )

    tokens_utilizados = models.PositiveIntegerField(
        default=0,
        help_text="Número de tokens utilizados por esta mensagem."
    )

    custo_estimado = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        default=0.0,
        help_text="Custo estimado desta mensagem (em dólares)."
    )

    criado_em = models.DateTimeField(
        auto_now_add=True,
        help_text="Data e hora em que a mensagem foi criada."
    )

    metadados = models.JSONField(
        default=dict,
        blank=True,
        help_text="Metadados adicionais em formato JSON."
    )

    feedback = models.BooleanField(
        null=True,
        blank=True,
        help_text="Feedback do usuário sobre a mensagem (True = positivo, False = negativo)."
    )

    feedback_comentario = models.TextField(
        blank=True,
        help_text="Comentário adicional do usuário sobre o feedback."
    )

    ordem = models.PositiveIntegerField(
        default=0,
        help_text="Ordem da mensagem dentro da conversa."
    )

    class Meta:
        verbose_name = "mensagem"
        verbose_name_plural = "mensagens"
        ordering = ['ordem']
        indexes = [
            models.Index(fields=['conversa', 'ordem']),
            models.Index(fields=['papel', 'criado_em']),
        ]

    def __str__(self):
        if self.tipo_conteudo == 'text' and self.texto:
            return f"{self.get_papel_display()}: {self.texto[:50]}..."
        elif self.dados_conteudo:
            return f"{self.get_papel_display()}: {self.tipo_conteudo} ({self.dados_conteudo.name})"
        return f"{self.get_papel_display()}: Sem conteúdo"


class HistoricoTreinamento(models.Model):
    """
    Registra quando conversas são utilizadas para treinamento do modelo,
    mantendo um log de conformidade com as preferências de privacidade.
    """
    conversa = models.ForeignKey(
        Conversa,
        on_delete=models.CASCADE,
        related_name='historico_treinamento',
        help_text="A conversa utilizada para treinamento."
    )

    utilizado_em = models.DateTimeField(
        auto_now_add=True,
        help_text="Data e hora em que a conversa foi utilizada para treinamento."
    )

    modelo_destino = models.CharField(
        max_length=50,
        help_text="O modelo que foi treinado usando esta conversa."
    )

    anonimizada = models.BooleanField(
        default=True,
        help_text="Se os dados pessoais foram removidos antes do treinamento."
    )

    class Meta:
        verbose_name = "histórico de treinamento"
        verbose_name_plural = "históricos de treinamento"
        ordering = ['-utilizado_em']

    def __str__(self):
        return f"Treinamento {self.modelo_destino} em {self.utilizado_em.date()}"