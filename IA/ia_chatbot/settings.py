"""
Django settings for ia_chatbot project.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- CONFIGURAÇÕES DE SEGURANÇA ---
# ATENÇÃO: MANTER A SECRET_KEY NO CÓDIGO É MUITO INSEGURO!
# NUNCA ENVIE ESTE ARQUIVO PARA UM REPOSITÓRIO PÚBLICO (COMO GITHUB).
SECRET_KEY = 'django-insecure-)v17u+9=pfsj^01lbrlj)grmfxmg#6rm&$i-si%b)h9^9*vo*('

# ATENÇÃO: NUNCA RODE COM DEBUG=True EM PRODUÇÃO.
DEBUG = True

# Em produção, substitua '*' por seu domínio específico. Ex: ['meusite.com', 'www.meusite.com']
ALLOWED_HOSTS = ["*", "*.ngrok-free.app"]

# Para uso com ngrok ou outros proxies seguros.
CSRF_TRUSTED_ORIGINS = [
    "https://*.ngrok-free.app",
    "http://localhost",
    "http://127.0.0.1",
]


# --- APLICAÇÕES INSTALADAS ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Suas Apps
    'chat',
]

# --- MIDDLEWARE ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --- URLs E TEMPLATES ---
ROOT_URLCONF = 'ia_chatbot.urls'
WSGI_APPLICATION = 'ia_chatbot.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')], # Forma mais robusta de definir o caminho
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# --- BANCO DE DADOS ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --- AUTENTICAÇÃO E AUTORIZAÇÃO ---
AUTH_USER_MODEL = 'chat.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- INTERNACIONALIZAÇÃO ---
# Ajustado para o Brasil
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# --- ARQUIVOS ESTÁTICOS E DE MÍDIA ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') # Descomente e use em produção

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Garante que o diretório de mídia existe
os.makedirs(MEDIA_ROOT, exist_ok=True)

# --- CONFIGURAÇÕES DE SERVIÇOS EXTERNOS (API GEMINI) ---
# ATENÇÃO: MANTER A API KEY NO CÓDIGO É MUITO INSEGURO!
# RISCO DE ROUBO E GERAÇÃO DE CUSTOS EM SUA CONTA GOOGLE.
GEMINI_API_KEY = "AIzaSyAG8uU2QNFAR6L332z-LCQ6EAOs5gJ9hxo"
GEMINI_MODEL_NAME = "gemini-1.5-flash-latest"
GEMINI_TIMEOUT = 100

# --- CONFIGURAÇÕES DO CELERY (PARA TAREFAS EM BACKGROUND) ---
# Se você usar Redis, o ideal é que a senha também não fique aqui.
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE # Usa o mesmo timezone do Django