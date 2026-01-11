# RAG Project

> **Tutorial de como este projeto foi desenvolvido, passo a passo.**

## Conteúdo

 - [`Adicionando .editorconfig e .gitignore`](#editorconfig-gitignore)
 - [`Criando variáveis de Ambiente (.env.dev, .env.prod e .env.example)`](#env-variables)
 - [`Iniciando o projeto com "poetry init"`](#poetry-init)
 - [`Instalando e configurando o Taskipy`](#taskipy-settings-pyproject)
 - [`Instalando/Configurando/Exportando o Django + Uvicorn`](#django-settings)
 - [`Criando o container com PostgreSQL (db)`](#db-container)
 - [`Criando o container com Redis (redis_cache)`](#redis-container)
<!---
[WHITESPACE RULES]
- "40" Whitespace character.
--->



















































---

<div id="editorconfig-gitignore"></div>

## `Adicionando .editorconfig e .gitignore`

De início vamos adicionar os arquivos `.editorconfig` e `.gitignore` na raiz do projeto:

[.editorconfig](../.editorconfig)
```conf
# top-most EditorConfig file
root = true

# Unix-style newlines with a newline ending every file
[*]
end_of_line = lf
insert_final_newline = true
charset = utf-8

# 4 space indentation
[*.{py,html, js}]
indent_style = space
indent_size = 4

# 2 space indentation
[*.{json,y{a,}ml,cwl}]
indent_style = space
indent_size = 2
```

[.gitignore](../.gitignore)
```conf
É muito grande não vou exibir...
```




















































---

<div id="env-variables"></div>

## `Criando variáveis de Ambiente (.env.dev, .env.prod e .env.example)`

> **Nunca reutilize o mesmo `.env` para *dev* e *prod*.**

 - Mesmo em projeto pessoal.
 - Isso evita 90% dos acidentes.

### `🎯 Objetivo`

Ter:

 - Variáveis claramente separadas por ambiente
 - Zero risco de misturar dev ↔ prod
 - Fácil uso no Docker Compose, Django e CI

**✅ Estrutura recomendada de arquivos:**
```bash
.env.dev
.env.prod
.env.example
```

 - `.env.dev (desenvolvimento)`
   - Nomes explícitos
   - Senha fraca OK (local)
   - DEBUG=True
   - Ambiente identificado
 - `.env.prod (produção)`
   - Senhas fortes
   - DEBUG=False
   - Nada que sugira dev
 - `.env.example (para versionar)`
   - Pode ser comitado como exemplo

### `Como usar isso no Django?`

[core/settings.py](../core/settings.py)
```python
import os

DJANGO_ENV = os.getenv("DJANGO_ENV", "dev")
DEBUG = os.getenv("DEBUG") == "True"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["POSTGRES_DB"],
        "USER": os.environ["POSTGRES_USER"],
        "PASSWORD": os.environ["POSTGRES_PASSWORD"],
        "HOST": os.environ["POSTGRES_HOST"],
        "PORT": os.environ["POSTGRES_PORT"],
    }
}
```

 - 📌 Simples
 - 📌 Explícito
 - 📌 Sem mágica

### `🔐 Segurança (nota importante)`

Mesmo em produção:

 - Não coloque `.env.prod` no repositório
 - Em cloud:
   - Use secrets (GitHub Actions, Docker secrets, etc.)
 - Local prod (VPS):
   - Arquivo `.env.prod` fora do repo

### `📄 .env.example`

O [.env.example](../.env.example) é o contrato do projeto, então ele precisa ser didático, completo e seguro.

> **👉 Esse arquivo PODE e DEVE ser versionado.**

[.env.example](../.env.example)
```bash
# ============================================================================
# CONFIGURAÇÃO DO POSTGRESQL
# ============================================================================
POSTGRES_DB=                # Nome do banco de dados a ser criado (ex: rag_dev, rag_prod)
POSTGRES_USER=              # Usuário do banco de dados
POSTGRES_PASSWORD=          # Senha do banco de dados
POSTGRES_HOST=db            # Nome do serviço (container) do banco no docker-compose
POSTGRES_PORT=5432          # Porta padrão do PostgreSQL


# ============================================================================
# CONFIGURAÇÃO DO REDIS
# ============================================================================
REDIS_HOST=redis            # Nome do serviço (container) do Redis no docker-compose
REDIS_PORT=6379             # Porta padrão do Redis


# ============================================================================
# CONFIGURAÇÃO DO DJANGO
# ============================================================================
DJANGO_SECRET_KEY=          # Chave secreta do Django (NUNCA versionar valores reais)
DJANGO_DEBUG=               # True = Desenvolvimento | False = Produção
DJANGO_ALLOWED_HOSTS=       # Hosts permitidos (ex: *, localhost, dominio.com)

# ID do site para o framework de sites do Django (usado pelo django-allauth)
DJANGO_SITE_ID=1            # Geralmente 1
DJANGO_SITE_DOMAIN=         # Dominio do site (ex: localhost ou seu-dominio.com)
DJANGO_SITE_NAME=           # Nome exibido do site


# ============================================================================
# CONFIGURAÇÃO DO UVICORN
# ============================================================================
UVICORN_HOST=0.0.0.0        # 0.0.0.0 = escutar em todas as interfaces (Docker)
UVICORN_PORT=8000           # Porta interna do app Django


# ============================================================================
# CONFIGURAÇÃO DO CELERY
# ============================================================================
CELERY_BROKER_URL=          # URL do broker do Celery (ex: redis://redis:6379/0)
CELERY_RESULT_BACKEND=      # URL do backend de resultados (ex: redis://redis:6379/1)

# Executa tasks de forma síncrona (sem fila) quando True
# Útil para testes unitários
CELERY_TASK_ALWAYS_EAGER=   # True ou False

# Propaga exceções quando tasks são executadas de forma eager
# Útil para debugging em testes
CELERY_TASK_EAGER_PROPAGATES=  # True ou False


# ============================================================================
# CONFIGURAÇÕES DO SUPERUSUÁRIO INICIAL
# ============================================================================
DJANGO_SUPERUSER_USERNAME=  # Nome de usuário do superusuário inicial
DJANGO_SUPERUSER_EMAIL=     # Email do superusuário inicial
DJANGO_SUPERUSER_PASSWORD=  # Senha do superusuário inicial


# ============================================================================
# CONFIGURAÇÕES DE AUTENTICAÇÃO SOCIAL (OAUTH2)
# ============================================================================
# Client ID do Google OAuth2
GOOGLE_CLIENT_ID=           # Client ID fornecido pelo Google

# Client Secret do Google OAuth2
GOOGLE_CLIENT_SECRET=       # Client Secret fornecido pelo Google

# Client ID do GitHub OAuth2
GITHUB_CLIENT_ID=           # Client ID fornecido pelo GitHub

# Client Secret do GitHub OAuth2
GITHUB_CLIENT_SECRET=       # Client Secret fornecido pelo GitHub
```

### `Vendo as variáveis de ambiente dentro do container`

Uma coisa interessante é verificar se essas variáveis de ambiente estão sendo reconhecidas dentro do container:

```bash
docker inspect <container-name> --format='{{.Config.Env}}'
```

**OUTPUT:**
```bash
[DJANGO_SITE_ID=1 DJANGO_SUPERUSER_USERNAME=drigols REDIS_HOST=redis POSTGRES_HOST=db DJANGO_SUPERUSER_PASSWORD=drigols GOOGLE_CLIENT_SECRET=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 CELERY_TASK_ALWAYS_EAGER=False GOOGLE_CLIENT_ID=265398246169-0eppnll3l45mhkppo08r02lapoj0a35i.apps.googleusercontent.com CELERY_BROKER_URL=redis://redis:6379/0 GITHUB_CLIENT_SECRET=fabc42b71aef3341ac8693d680b3c756ac82d03d CELERY_TASK_EAGER_PROPAGATES=True UVICORN_PORT=8000 POSTGRES_USER=rag_user_dev REDIS_PORT=6379 UVICORN_HOST=0.0.0.0 GITHUB_CLIENT_ID=Ov23lidBPkHBQ0NCKEM2 DJANGO_SECRET_KEY=django-insecure-dev-key POSTGRES_PORT=5432 CELERY_RESULT_BACKEND=redis://redis:6379/1 DJANGO_SUPERUSER_EMAIL=drigols.creative@gmail.com DJANGO_SITE_DOMAIN=localhost POSTGRES_PASSWORD=rag_pass_dev DJANGO_ALLOWED_HOSTS=* DJANGO_DEBUG=True DJANGO_SITE_NAME=Localhost POSTGRES_DB=rag_dev PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/lib/postgresql/15/bin GOSU_VERSION=1.19 LANG=en_US.utf8 PG_MAJOR=15 PG_VERSION=15.15-1.pgdg13+1 PGDATA=/var/lib/postgresql/data]
```

> **NOTE:**  
> Uma observação aqui é que vamos continuar utilizando só um [.env](../.env) porque nosso projeto por agora só vai utilizar um único [docker-compose.yml](../docker-compose.yml.




















































---

<div id="poetry-init"></div>

## `Iniciando o projeto com "poetry init"`

Agora vamos iniciar nosso projeto com `poetry init`:

```bash
poetry init
```




















































---

<div id="taskipy-settings-pyproject"></div>

## `Instalando e configurando o Taskipy`

> Aqui, nós vamos *instalar* e *configurar* o **Taskipy** no nosso projeto.

De início vamos atualizar a versão do Python no nosso [pyproject.toml](../pyproject.toml) para que o Taskipy funcione corretamente:

[pyproject.toml](../pyproject.toml)
```toml
requires-python = ">=3.12,<4.0"
```

Ótimo, agora vamos de fato instala o Taskipy na sua última versão com o comando:

```bash
poetry add --group dev taskipy@latest
```



















































---

<div id="django-settings"></div>

## `Instalando/Configurando/Exportando o Django + Uvicorn`

 - Antes de criar um container contendo o Django, vamos instalar e configurar o `Django` + `Uvicorn` na nossa máquina local (host).
 - **NOTE:** Vai ser como um modelo que nós vamos utilizar dentro do container.

#### `Instalações iniciais`

De início, vamos instalar as bibliotecas necessárias:

```bash
poetry add django@latest
```

```bash
poetry add uvicorn@latest
```

#### `Criando o projeto Django (core)`

Agora vamos criar o projeto (core) que vai ter as configurações iniciais do Django:

```bash
django-admin startproject core .
```

#### `Configurando os arquivos: templates, static e media`

> Aqui nós também vamos fazer as configurações iniciais do Django que serão.

Fazer o Django identificar onde estarão os arquivos `templates`, `static` e `media`:

[core/settings.py](../core/settings.py)
```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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



STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

Até aqui está quase tudo ok para criarmos um Container com `Django` e `Uvicorn`...

> Mas, antes de criar nossos containers, precisamos gerar os `requirements.txt (produção)` e `requirements-dev.txt (desenvolvimento)`.

**Mas, primeiro devemos instalar o plugin "export" do Poetry:**
```bash
poetry self add poetry-plugin-export
```

Agora vamos gerar o `requirements.txt` de *produção*:

**Produção:**
```bash
task exportprod
```

Continuando, agora vamos gerar `requirements-dev.txt` (esse é mais utilizado durante o desenvolvimento para quem não usa o Poetry):

**Desenvolvimento:**
```bash
poetry export --without-hashes --with dev --format=requirements.txt --output=requirements-dev.txt
```

Agora, vamos gerar o `requirements.txt` de *produção*:

**Produção:**
```bash
poetry export --without-hashes --format=requirements.txt --output=requirements.txt
```

Também seria interessante criar comandos Taskipy para esse processo de exportar as dependências:

[pyproject.toml](../pyproject.toml)
```toml
[tool.taskipy.tasks]
# ------------------ ( Project Management ) -----------------
exportdev = "poetry export --without-hashes --with dev --format=requirements.txt --output=requirements-dev.txt"
exportprod = "poetry export --without-hashes --format=requirements.txt --output=requirements.txt"
```




















































---

<div id="db-container"></div>

## `Criando o container com PostgreSQL (db)`

> Aqui nós vamos entender e criar um container contendo o `Banco de Dados PostgreSQL`.

 - **Função:**
   - Armazenar dados persistentes da aplicação (usuários, arquivos, prompts, etc.).
 - **Quando usar:**
   - Sempre que precisar de um banco de dados relacional robusto.
 - **Vantagens:**
   - ACID (consistência e confiabilidade).
   - Suporte avançado a consultas complexas.
 - **Desvantagens:**
   - Mais pesado que bancos NoSQL para dados muito simples.

Antes de criar nosso container contendo o PostgreSQL vamos criar as variáveis de ambiente para esse container:

[.env](../.env)
```bash
# ============================================================================
# CONFIGURAÇÃO DO POSTGRESQL
# ============================================================================
POSTGRES_DB=rag_db         # Nome do banco de dados a ser criado
POSTGRES_USER=raguser      # Usuário do banco de dados
POSTGRES_PASSWORD=ragpass  # Senha do banco de dados
POSTGRES_HOST=db           # Nome do serviço (container) do banco no docker-compose
POSTGRES_PORT=5432         # Porta padrão do PostgreSQL
```

 - `POSTGRES_DB` → nome do banco criado automaticamente ao subir o container.
 - `POSTGRES_USER` → usuário administrador do banco.
 - `POSTGRES_PASSWORD` → senha do usuário do banco.
 - `POSTGRES_HOST` → para o Django se conectar, usamos o nome do serviço (db), não localhost, pois ambos estão na mesma rede docker.
 - `POSTGRES_PORT` → porta padrão 5432.

Continuando, o arquivo [docker-compose.yml](../docker-compose.yml) para o nosso container *PostgreSQL* ficará assim:

[docker-compose.yml](../docker-compose.yml)
```yml
services:
  # PostgreSQL Service
  db:
    image: postgres:15
    container_name: postgresql
    restart: always
    env_file: .env
    ports:
      - 5432:5432
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - backend

volumes:
  postgres_data:

networks:
  backend:
```

 - `db`
   - Nome do *serviço (container)* criado pelo docker-compose.
 - `image: postgres:15`
   - Pega a versão 15 oficial do PostgreSQL no Docker Hub.
 - `container_name: postgresql`
   - Nome fixo do container (para facilitar comandos como docker logs postgresql).
 - `restart: always`
   - 🔹 O container vai voltar sempre que o Docker daemon subir, independente do motivo da parada.
   - 🔹 Mesmo se você der *docker stop*, quando o host reiniciar o container volta sozinho.
   - 👉 Bom para produção quando você quer *99% de disponibilidade*.
 - `env_file: .env`
   - Carrega variáveis de ambiente do arquivo `.env`.
 - `volumes:`
     - `postgres_data:` → Volume docker (Named Volume).
     - `/var/lib/postgresql/data` → pasta interna do container onde o Postgres armazena os dados.
 - `ports: 5432:5432`
   - `Primeiro 5432:` → porta no host (sua máquina).
   - `Segundo 5432:` → porta dentro do container onde o Postgres está rodando.
   - **NOTE:** Isso permite que você use o psql ou qualquer ferramenta de banco de dados (DBeaver, TablePlus, etc.) diretamente do seu PC.
 - `volumes:`
   - `postgres_data:` → Volume docker (Named Volume).
 - `networks: backend`
   - Coloca o container na rede backend para comunicação interna segura.

Aqui, também seria interessante ter comando Taskipy para gerenciar nossos containers:

[pyproject.toml](../pyproject.toml)
```toml
[tool.taskipy.tasks]
# -------------- ( General Docker Management ) --------------
start_compose = 'docker compose up -d'
down_compose = 'docker compose down'
restart_compose = 'docker restart $(docker ps -q)'
build_compose = 'docker compose up --build -d'
clean_compose = """
docker stop $(docker ps -aq) 2>/dev/null || true &&
docker rm $(docker ps -aq) 2>/dev/null || true &&
docker rmi -f $(docker images -aq) 2>/dev/null || true &&
docker volume rm $(docker volume ls -q) 2>/dev/null || true &&
docker system prune -a --volumes -f
"""
```

Ótimo, agora vamos subir o container:

```bash
task start_compose
```

Ótimo, agora se você desejar se conectar nesse Banco de Dados via *bash* utilize o seguinte comando (As vezes é necessário esperar o container/banco de dados subir):

**Entrar no container "postgresql" via bash:**
```bash
docker exec -it postgresql bash
```

**Entra no banco de sados a partir das variáveis de ambiente:**
```bash
psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"
```

**Ver em qual Banco de Dados e usuário está conectado:**
```bash
\c
```

**OUTPUT:**
```bash
You are now connected to database "rag_db" as user "raguser".
```

> **E os volumes como eu vejo?**

```bash
docker volume ls
```

**OUTPUT:**
```bash
DRIVER    VOLUME NAME
local     rag-project_postgres_data
```

Nós também podemos inspecionar esse volume:

```bash
docker volume inspect rag-project_postgres_data
```

**OUTPUT:**
```bash
[
    {
        "CreatedAt": "2026-01-11T13:35:59-03:00",
        "Driver": "local",
        "Labels": {
            "com.docker.compose.config-hash": "5dc3d628a7c7fc208c1a083f74bde3e0acba02c0a3a313cd96bc1e1ecaa7ba3a",
            "com.docker.compose.project": "rag-project",
            "com.docker.compose.version": "2.39.1",
            "com.docker.compose.volume": "postgres_data"
        },
        "Mountpoint": "/var/lib/docker/volumes/rag-project_postgres_data/_data",
        "Name": "rag-project_postgres_data",
        "Options": null,
        "Scope": "local"
    }
]
```

 - `Mountpoint`
   - O *Mountpoint* é onde os arquivos realmente ficam, mas não é recomendado mexer manualmente lá.
   - Para interagir com os dados, use o *container* ou ferramentas do próprio serviço (por exemplo, psql no Postgres).



















































---

<div id="redis-container"></div>

## `Criando o container com Redis (redis_cache)`

> Aqui nós vamos entender e criar um container contendo o `Redis`.

 - **Função:**
   - Armazenar dados temporários (cache, sessões, filas de tarefas).
 - **Quando usar:**
   - Quando for necessário aumentar velocidade de acesso a dados temporários ou usar filas.
 - **Vantagens:**
   - Muito rápido (em memória).
   - Perfeito para cache e tarefas assíncronas.
 - **Desvantagens:**
   - Não indicado para dados críticos (pode perder dados em caso de reinício)

Antes de criar nosso container contendo o *Redis* vamos criar as variáveis de ambiente para esse container:

[.env](../.env)
```bash
# ============================================================================
# CONFIGURAÇÃO DO REDIS
# ============================================================================
REDIS_HOST=redis  # Nome do serviço (container) do Redis no docker-compose
REDIS_PORT=6379   # Porta padrão do Redis
```

 - `REDIS_HOST` → nome do serviço no docker-compose.
 - `REDIS_PORT` → porta padrão 6379.
 - **NOTE:** O Redis será usado como cache em possivelmente fila de tarefas (com Celery, RQ ou outro).

Continuando, o arquivo [docker-compose.yml](../docker-compose.yml) para o nosso container *Redis* ficará assim:

[docker-compose.yml](../docker-compose.yml)
```yml
services:
  # Redis Service
  redis:
    image: redis:7
    container_name: redis_cache
    restart: always
    env_file: .env
    volumes:
      - redis_data:/data
    networks:
      - backend

volumes:
  redis_data:

networks:
  backend:
```

 - `redis:`
   - Nome do *serviço (container)* criado pelo docker-compose.
 - `image: redis:7`
   - Pega a versão 7 oficial do Redis no Docker Hub.
 - `container_name: redis_cache`
   - Nome fixo do container (para facilitar comandos como docker logs redis_cache).
 - `restart: always`
   - 🔹 O container vai voltar sempre que o Docker daemon subir, independente do motivo da parada.
   - 🔹 Mesmo se você der *docker stop*, quando o host reiniciar o container volta sozinho.
   - 👉 Bom para produção quando você quer *99% de disponibilidade*.
 - `env_file: .env`
   - Carrega variáveis de ambiente do arquivo `.env`.
 - `volumes:`
     - `redis_data:` → Volume docker (Named Volume).
     - `/data` → pasta interna do container onde o Redis armazena os dados.
 - `networks: backend`
   - Só está acessível dentro da rede interna backend (não expõe porta para fora).

Agora é só subir o container, igual fizemos com o PostgreSQL:

```bash
task start_compose
```

> **E os volumes como eu vejo?**

```bash
docker volume ls
```

**OUTPUT:**
```bash
DRIVER    VOLUME NAME
local     ragproject_redis_data
```

Nós também podemos inspecionar esse volume:

```bash
docker volume inspect ragproject_redis_data
```

**OUTPUT:**
```bash
[
    {
        "CreatedAt": "2025-11-10T07:35:18-03:00",
        "Driver": "local",
        "Labels": {
            "com.docker.compose.config-hash": "75e82217f9045c1c51074e1c927a0ba2be71af9e784263a59e10d6bfb25e12e6",
            "com.docker.compose.project": "ragproject",
            "com.docker.compose.version": "2.39.1",
            "com.docker.compose.volume": "redis_data"
        },
        "Mountpoint": "/var/lib/docker/volumes/ragproject_redis_data/_data",
        "Name": "ragproject_redis_data",
        "Options": null,
        "Scope": "local"
    }
]
```

 - `Mountpoint`
   - O *Mountpoint* é onde os arquivos realmente ficam, mas não é recomendado mexer manualmente lá.
   - Para interagir com os dados, use o *container* ou ferramentas do próprio serviço (por exemplo, psql no Postgres).

---

**Rodrigo** **L**eite da **S**ilva - **rodrigols89**
