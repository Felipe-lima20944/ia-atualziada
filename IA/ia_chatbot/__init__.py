import os
from celery import Celery

# Define a variável de ambiente para as configurações do Django.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ia_chatbot.settings')

# Cria uma instância da aplicação Celery.
# O nome 'ia_chatbot' é o nome da sua pasta de projeto.
app = Celery('ia_chatbot')

# Carrega as configurações do Celery do arquivo settings.py do Django.
# O namespace 'CELERY' garante que as configurações do Celery são prefixadas com 'CELERY_'.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodescobre tarefas assíncronas em todos os aplicativos instalados.
# O Celery procurará por um arquivo chamado tasks.py dentro de cada aplicativo.
app.autodiscover_tasks()

# Tarefa de depuração opcional, útil para verificar se o Celery está funcionando.
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
