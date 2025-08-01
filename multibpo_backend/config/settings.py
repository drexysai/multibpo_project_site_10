import os
import sys
from pathlib import Path
from datetime import timedelta  # ← NOVO: Import para JWT

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ===================================================================
# CARREGAR ARQUIVO .ENV
# ===================================================================

# Carregar variáveis do arquivo .env
try:
    from dotenv import load_dotenv
    
    # Tentar múltiplos caminhos possíveis
    possible_paths = [
        BASE_DIR.parent.parent / '.env',  # /app/.env
        BASE_DIR.parent / '.env',         # /app/multibpo_backend/.env
        Path('/app') / '.env',            # /app/.env (absoluto)
        Path('.env'),                     # .env (relativo)
    ]
    
    env_loaded = False
    for env_path in possible_paths:
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)
            print(f"✅ Arquivo .env carregado de: {env_path}")
            env_loaded = True
            break
    
    if not env_loaded:
        print(f"⚠️  Arquivo .env não encontrado nos caminhos: {[str(p) for p in possible_paths]}")
        
except ImportError:
    print("⚠️  python-dotenv não instalado, usando apenas variáveis de ambiente do sistema")
except Exception as e:
    print(f"⚠️  Erro ao carregar .env: {e}")

# ===================================================================

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'dev-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost').split(',')

# Application definition
INSTALLED_APPS = [
    # Django Core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third Party Apps
    'rest_framework',
    'corsheaders',
    'rest_framework_simplejwt',
    'django_extensions',
    'phonenumber_field',
    
    # Local Apps
    'apps.authentication',
    'apps.contadores',
    'apps.receita',
    'apps.whatsapp_users', 
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # ← NOVO: CORS middleware
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database - AGORA USANDO AS VARIÁVEIS CORRETAS!
DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DATABASE_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.environ.get('DATABASE_NAME', 'multibpo_db'),
        'USER': os.environ.get('DATABASE_USER', 'multibpo'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD', 'multibpo123'),
        'HOST': os.environ.get('DATABASE_HOST', 'db'),
        'PORT': os.environ.get('DATABASE_PORT', '5432'),
    }
}

# ========== CONFIGURAÇÃO DE CACHE CORRIGIDA ==========
# Cache configuration - Usando DummyCache para desenvolvimento
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        'LOCATION': '',
    }
}

# Para reabilitar django-ratelimit no futuro (quando tivermos Redis):
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.redis.RedisCache',
#         'LOCATION': 'redis://127.0.0.1:6379/1',
#     }
# }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ========== CONFIGURAÇÕES DA FASE 2.1 ==========

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),      # Token expira em 1 hora
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),      # Refresh em 7 dias
    'ROTATE_REFRESH_TOKENS': True,                    # Rotaciona refresh tokens
    'BLACKLIST_AFTER_ROTATION': True,                # Blacklist tokens antigos
    'UPDATE_LAST_LOGIN': True,                        # Atualiza last_login
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': 'MultiBPO',                             # Identificador do sistema
    
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# Phone Number Configuration
PHONENUMBER_DEFAULT_REGION = 'BR'  # Brasil como região padrão

CSRF_TRUSTED_ORIGINS = [
    origin.strip() for origin in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',') if origin.strip()
]

# CORS Configuration (para desenvolvimento)
CORS_ALLOWED_ORIGINS = [
    origin.strip() for origin in os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',') if origin.strip()
]

CORS_ALLOW_CREDENTIALS = True

# Database Schema Configuration
# Configuração para uso dos schemas PostgreSQL definidos na Fase 1

# Apps que usarão schema 'contadores'
CONTADORES_APPS = ['authentication', 'contadores']

# Apps que usarão schema 'ia_data' (futuro - Fase 5)
IA_DATA_APPS = []

# Apps que usarão schema 'servicos' (futuro - Fase 3)
SERVICOS_APPS = []

# Logging Configuration (para desenvolvimento)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'apps.authentication': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'apps.contadores': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}


# ========== CONFIGURAÇÕES DA SUB-FASE 2.2.1 ==========

# Swagger/OpenAPI Configuration
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
    'SUPPORTED_SUBMIT_METHODS': [
        'get',
        'post',
        'put',
        'delete',
        'patch'
    ],
    'OPERATIONS_SORTER': 'alpha',
    'TAGS_SORTER': 'alpha',
    'DOC_EXPANSION': 'none',
    'DEEP_LINKING': True,
    'SHOW_EXTENSIONS': True,
    'DEFAULT_MODEL_RENDERING': 'model',
}

REDOC_SETTINGS = {
    'LAZY_RENDERING': False,
    'HIDE_HOSTNAME': False,
    'EXPAND_RESPONSES': 'all',
    'PATH_IN_MIDDLE': True,
}


# Coverage Configuration para Testes
COVERAGE_MODULE_EXCLUDES = [
    'tests$', 
    'settings$', 
    'urls$', 
    'locale$',
    '__pycache__$', 
    'migrations$', 
    'venv$'
]

COVERAGE_REPORT_HTML_OUTPUT_DIR = 'htmlcov'

# Django Extensions Configuration
DJANGO_EXTENSIONS_RESET_DB = True

# Debug Toolbar Configuration (apenas em DEBUG=True E não em testes)
if DEBUG and 'test' not in sys.argv:
    INSTALLED_APPS += [
        'debug_toolbar',
    ]
    
    MIDDLEWARE = [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ] + MIDDLEWARE
    
    INTERNAL_IPS = [ip.strip() for ip in os.environ.get('DJANGO_INTERNAL_IPS', '127.0.0.1').split(',')]


    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
        'SHOW_COLLAPSED': True,
        'IS_RUNNING_TESTS': False,  # Desabilita durante testes
    }

# Factory Boy Configuration
FACTORY_FOR_DJANGO_SILENCE_ROOT_WARNING = True

# ========== CONFIGURAÇÕES DE PRODUÇÃO WEB ==========

# SSL/HTTPS Configuration (CloudFlare como proxy)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = False  # Só redireciona em produção
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Session Security
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# Security Headers
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Staticfiles configuration (sempre necessário)
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
] if os.path.exists(os.path.join(BASE_DIR, 'static')) else []

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Configurações específicas para produção
if not DEBUG:
    # Configurações adicionais para produção podem ir aqui
    pass

# Logging para produção
if not DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'file': {
                'level': 'INFO',
                'class': 'logging.FileHandler',
                'filename': '/app/logs/django.log',
            },
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['file', 'console'],
                'level': 'INFO',
                'propagate': True,
            },
            'apps': {
                'handlers': ['file', 'console'],
                'level': 'INFO',
                'propagate': True,
            },
        },
    }

# CloudFlare IP Trust
CLOUDFLARE_IPS = [
    '103.21.244.0/22', '103.22.200.0/22', '103.31.4.0/22', '104.16.0.0/13',
    '104.24.0.0/14', '108.162.192.0/18', '131.0.72.0/22', '141.101.64.0/18',
    '162.158.0.0/15', '172.64.0.0/13', '173.245.48.0/20', '188.114.96.0/20',
    '190.93.240.0/20', '197.234.240.0/22', '198.41.128.0/17',
]

# INTERNAL_IPS - DEFINIR PRIMEIRO, DEPOIS CONCATENAR
INTERNAL_IPS = [ip.strip() for ip in os.environ.get('DJANGO_INTERNAL_IPS', '127.0.0.1').split(',')]

# Trust CloudFlare IPs for real IP detection (TEMPORARIAMENTE DESABILITADO)
# if not DEBUG:
#     INTERNAL_IPS.extend(CLOUDFLARE_IPS)

# ========== CONFIGURAÇÃO EMAIL GMAIL SMTP (FASE 1) ==========
# Adicionado em 01/07/2025 para sistema mobile de verificação de email
# Configuração temporária com Gmail, depois migrar para Mailgun

from datetime import timedelta

# Backend de email Gmail SMTP
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Credenciais Gmail (configurar via variáveis de ambiente)
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'seu-email@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'sua-senha-de-app-google')

# Email remetente padrão
DEFAULT_FROM_EMAIL = f'MultiBPO <{EMAIL_HOST_USER}>'
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# URLs do frontend para verificação de email
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'https://multibpo.com.br')
EMAIL_VERIFICATION_URL = f'{FRONTEND_URL}/m/verificar-email'

# Configurações de token de verificação
EMAIL_VERIFICATION_TOKEN_LIFETIME = timedelta(hours=1)  # Token expira em 1 hora

# Configurações de segurança para email
EMAIL_TIMEOUT = 30  # Timeout de conexão SMTP em segundos
EMAIL_SSL_KEYFILE = None
EMAIL_SSL_CERTFILE = None

# Debug de email (apenas em desenvolvimento)
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Para testes locais
    # Para usar Gmail em desenvolvimento, comentar a linha acima

# ========== LOGGING PARA EMAIL ==========
# Adicionar logging específico para sistema de email
LOGGING['loggers']['email'] = {
    'handlers': ['file', 'console'],
    'level': 'INFO',
    'propagate': False,
}

# ========== CONFIGURAÇÕES MOBILE ESPECÍFICAS ==========
# URLs específicas para sistema mobile
MOBILE_CADASTRO_URL = f'{FRONTEND_URL}/m/cadastro'
MOBILE_LOGIN_URL = f'{FRONTEND_URL}/m/login'
MOBILE_POLITICA_URL = f'{FRONTEND_URL}/m/politica'
MOBILE_SUCESSO_URL = f'{FRONTEND_URL}/m/sucesso'

# Configurações de segurança para APIs mobile
MOBILE_API_RATE_LIMIT = '10/min'  # 10 tentativas por minuto por IP
MOBILE_TOKEN_MAX_AGE = 3600  # 1 hora em segundos

# ========== CONFIGURAÇÕES WHATSAPP INTEGRATION ==========
# URLs para integração com WhatsApp (atualizadas para mobile)
WHATSAPP_CADASTRO_URL = MOBILE_CADASTRO_URL
WHATSAPP_LOGIN_URL = MOBILE_LOGIN_URL
WHATSAPP_POLITICA_URL = MOBILE_POLITICA_URL

# ===================================================================
# ASAAS CONFIGURATION - Sistema de Pagamento
# ===================================================================

# Configurações do Asaas
ASAAS_API_KEY = os.environ.get('ASAAS_API_KEY', '')
ASAAS_BASE_URL = os.environ.get('ASAAS_BASE_URL', 'https://www.asaas.com/api/v3')
ASAAS_WEBHOOK_TOKEN = os.environ.get('ASAAS_WEBHOOK_TOKEN', '')
SITE_URL = os.environ.get('SITE_URL', 'https://multibpo.com.br')