# RAG Project

> **Tutorial de como este projeto foi desenvolvido, passo a passo.**

## Conteúdo

 - **Implementação**
   - [`Adicionando .editorconfig e .gitignore`](#editorconfig-gitignore)
   - [`Criando variáveis de Ambiente (.env.dev, .env.prod e .env.example)`](#env-variables)
   - [`Iniciando o projeto com "poetry init"`](#poetry-init)
   - [`Instalando e configurando o Taskipy`](#taskipy-settings-pyproject)
   - [`Instalando/Configurando/Exportando o Django + Uvicorn`](#django-settings)
   - [`Criando o container com PostgreSQL (db)`](#db-container)
   - [`Criando o container com Redis (redis_cache)`](#redis-container)
   - [`Script de inicialização do serviço web (entrypoint.sh)`](#entrypoint-sh)
   - [`Criando o Dockerfile do serviço web`](#web-dockerfiler)
   - [`Criando o docker compose para o container web`](#web-docker-compose)
   - [`Configurando o Django para reconhecer o PostgreSQL (+ .env) como Banco de Dados`](#django-postgresql-settings)
   - [`Criando o container Nginx (nginx | +Reverse Proxy)`](#nginx-container)
   - [`Instalando e configurando o Ruff`](#ruff-settings-pyproject)
   - [`Instalando e configurando o Pytest`](#pytest-settings-pyproject)
   - [`Instalando e configurando o pre-commit`](#precommit-settings)
   - [`Criando o diretório (pasta) .github/workflows/`](#github-workflows)
   - [`Criando o workflow lint.yml`](#github-workflows-lint-yml)
 - **Testes:**
   - [`Criando testes para o manage.py`](#manage-py-tests)
   - [`Testando se a URL /admin/ está registrada corretamente`](#test-admin-url-is-registered)
   - [`Testando se a aplicação ASGI do Django é criada corretamente`](#test-asgi-application-is-created)
<!---
[WHITESPACE RULES]
- Same topic = "40" Whitespace character.
- Different topic = "200" Whitespace character.
--->









































































































<!--- ( Implementação ) --->

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

<div id="entrypoint-sh"></div>

## `Script de inicialização do serviço web (entrypoint.sh)`

> O arquivo [entrypoint.sh](../entrypoint.sh) é o script de inicialização que *nós vamos utilizar dentro do container*.

Ele é executado *antes do Django subir (no container)*, garantindo que o ambiente esteja corretamente preparado para rodar a aplicação com segurança.

As responsabilidades principais desse script são:

 - Criar diretórios essenciais (static, media e staticfiles);
 - Ajustar permissões e ownership desses diretórios;
 - Garantir que a aplicação não rode como root, mas sim como um usuário não privilegiado (appuser);
 - Executar o comando final do container de forma segura.

Vamos começar adicionado `#!/bin/bash` no início do arquivo para dizer que ele é um script Bash:

[entrypoint.sh](../entrypoint.sh)
```bash
#!/bin/bash
```

Agora vamos adicionar `set -e` para garantir que o script encerre imediatamente se algum comando falhar:

[entrypoint.sh](../entrypoint.sh)
```bash
set -e
```

No container vai ser necessário nós criamos os diretórios `/code/static`, `/code/media`, `/code/staticfiles`:

[entrypoint.sh](../entrypoint.sh)
```bash
# Cria diretórios necessários se não existirem
mkdir -p /code/static /code/media /code/staticfiles
```

 - `-p`
   - O parâmetro `-p` no comando `mkdir` tem duas funções principais:
   - **1. Criar diretórios pais (parents):**
     - Se você especificar um caminho com vários níveis de diretórios que não existem, o `-p` cria todos os diretórios intermediários necessários.
     - Exemplo: `mkdir -p /code/static`
       - Se `/code` não existir, o `-p` cria primeiro `/code` e depois `/code/static`.
       - Sem o `-p`, você receberia um erro dizendo que `/code` não existe.
   - **2. Não dar erro se o diretório já existir:**
     - Se o diretório já existe, o `mkdir` normalmente retorna um erro.
     - Com `-p`, o comando simplesmente ignora e não retorna erro.
     - Sem `-p`:
       - `mkdir /tmp/teste`
       - `mkdir /tmp/teste`  # Erro: diretório já existe
     - Com `-p`:
       - `mkdir -p /tmp/teste`
       - `mkdir -p /tmp/teste`  # Sem erro
 - **NOTE:** Ou seja, o `-p` é importante para garantir que o script não gere errando, fazendo o `set -e` parar o script.

Agora, nós vamos fazer esses diretórios que foram criados dentro do container terem as seguintes permissõe:

[entrypoint.sh](../entrypoint.sh)
```bash
# Ajusta permissões e ownership dos diretórios
# Garante que o usuário appuser (UID 1000) possa escrever neles
chmod -R 755 /code/static /code/media /code/staticfiles
```

 - `-R  (Recursive)`
   - Aplica as permissões *recursivamente*, ou seja, no diretório e em *todos* os arquivos e subdiretórios dentro dele.
 - `755 (Permissões)`
   - Define as permissões em formato *octal*:
     - `7 (proprietário):` leitura + escrita + execução (4+2+1)
     - `5 (grupo):` leitura + execução (4+0+1)
     - `5 (outros):` leitura + execução (4+0+1)
   - Em termos práticos:
     - `rwxr-xr-x = 755`

### `Entendendo o "appuser"`

Dentro do contexto de Docker, o `appuser` é um **usuário não-root** que deve ser criado no [Dockerfile](../Dockerfile) para executar a aplicação com mais segurança.

> **Por que isso existe?**  

 - Por padrão, processos dentro de containers Docker rodam como **root (UID 0)**, o que é um risco de segurança. 
 - Uma boa prática é criar um usuário específico para rodar a aplicação.

Na prática, no [Dockerfile](../Dockerfile), vamos criar o `appuser` com o UID 1000 e o GID 1000:

[Dockerfile](../Dockerfile)
```dockerfile
# Cria o usuário appuser
RUN useradd -m -u 1000 appuser

# Mudar para esse usuário
USER appuser
```

Sabendo, que esse usuário será criado automaticamente quando o container for criado, nós vamos obter o `UID` e `GID` dele, com o script de inicialitação [entrypoint.sh](../entrypoint.sh):

[entrypoint.sh](../entrypoint.sh)
```bash
# Descobre o UID/GID do "appuser" que FOI CRIADO no Dockerfile
APPUSER_UID=$(id -u appuser 2>/dev/null || echo "1000")
APPUSER_GID=$(id -g appuser 2>/dev/null || echo "1000")
```

Continuando, no nosso script vamos criar um `if` que vai verificar se usuário **root (UID 0)** quem rodou o script:

[entrypoint.sh](../entrypoint.sh)
```bash
if [ "$(id -u)" = "0" ]; then
```

 - `id -u`
   - Retorna o UID (User ID) do usuário atual.
   - 0 → usuário root
   - 1000 → usuário comum
   - 999 → outro usuário não-root

Agora, se o usuário que rodou o script dentro do container for **root (UID 0)** vamos definir `appuser` como dono das pastas `/code/static`, `/code/media` e `/code/staticfiles`. Isso evita que `set -e` mate o container por erro de permissão.

[entrypoint.sh](../entrypoint.sh)
```bash
if [ "$(id -u)" = "0" ]; then
    chown -R ${APPUSER_UID}:${APPUSER_GID} \
        /code/static /code/media /code/staticfiles 2>/dev/null || true
```

Agora dentro do if nós vamos adicionar o seguinte comando:

[entrypoint.sh](../entrypoint.sh)
```bash
if [ "$(id -u)" = "0" ]; then
    ...
    exec gosu appuser "$@"
```

Este comando faz **duas coisas principais**: troca de usuário e executa um comando.

 - 1. **`exec`** - Substituição de processo
   - O `exec` é um comando **built-in do shell** que:
     - **Substitui** o processo atual (o script entrypoint.sh) pelo novo comando
     - **Não cria um processo filho**, ele literalmente substitui o processo
     - O script **termina aqui** e é substituído pelo novo comando
     - O novo comando herda o **PID do processo original** (geralmente PID 1 no Docker)
   - **Por que isso é importante no Docker?**
     - O processo com PID 1 é especial, ele recebe sinais do sistema (SIGTERM, SIGINT)
     - Com `exec`, sua aplicação recebe esses sinais diretamente
     - Sem `exec`, o script ficaria rodando e a aplicação seria um processo filho, podendo não receber os sinais corretamente
 - 2. `gosu` - Troca de usuário
   - O gosu é uma ferramenta leve para trocar de usuário, similar ao `sudo` ou `su`, mas:
     - Otimizada para containers Docker
     - Não cria processos desnecessários (mais limpo que `su -c`)
     - Mais simples e seguro que usar sudo dentro de containers
     - **NOTE:** Precisa ser instalado no Dockerfile: `RUN apt-get install -y gosu`

Ótimo, se o usuário que rodar o script dentro do container for **root (UID 0)**, ele vai ser trocado para o `appuser` e o comando vai ser executado.

> Mas e se o usuário que rodou o script dentro do container for **não root (UID 1000)**?

Nesse, caso nós vamos criar o `else` com o seguinte comando:

[entrypoint.sh](../entrypoint.sh)
```bash
if [ "$(id -u)" = "0" ]; then
  ...
else
    # Se já estiver rodando como "appuser", apenas executa
    exec "$@"
fi
```

Como o container **já está rodando como appuser** (não é root), o script:

 - NÃO precisa trocar de usuário (pula o gosu)
 - NÃO precisa ajustar permissões com chown (já foram ajustadas antes ou não são necessárias)
 - Apenas executa o comando passado ao container

### `Script completo`

No fim, nós vamos ter o seguinte script:

[entrypoint.sh](../entrypoint.sh)
```bash
#!/bin/bash

set -e

# Cria diretórios necessários se não existirem
mkdir -p /code/static /code/media /code/staticfiles

# Ajusta permissões e ownership dos diretórios
# Garante que o usuário appuser (UID 1000) possa escrever neles
chmod -R 755 /code/static /code/media /code/staticfiles

# Descobre o UID/GID do "appuser" que FOI CRIADO no Dockerfile
APPUSER_UID=$(id -u appuser 2>/dev/null || echo "1000")
APPUSER_GID=$(id -g appuser 2>/dev/null || echo "1000")

if [ "$(id -u)" = "0" ]; then
    chown -R ${APPUSER_UID}:${APPUSER_GID} \
        /code/static /code/media /code/staticfiles 2>/dev/null || true
    exec gosu appuser "$@"
else
    # Se já estiver rodando como "appuser", apenas executa
    exec "$@"
fi
```



















































---

<div id="web-dockerfiler"></div>

## `Criando o Dockerfile do serviço web`

Antes de criar o container contendo o *Django* e o *Uvicorn*, vamos criar o nosso Dockerfile...

> **Mas por que eu preciso de um Dockerfile para o Django + Uvicorn?**

**NOTE:**  
O Dockerfile é onde você diz **como** essa imagem será construída.

> **O que o Dockerfile faz nesse caso?**

 - Escolhe a imagem base (ex.: python:3.12-slim) para rodar o Python.
 - Instala as dependências do sistema (por exemplo, libpq-dev para PostgreSQL).
 - Instala as dependências Python (pip install -r requirements.txt).
 - Copia o código do projeto para dentro do container.
 - Define o diretório de trabalho (WORKDIR).
 - Configura o comando de entrada.
 - Organiza assets estáticos e outras configurações.

> **Quais as vantagens de usar o Dockerfile?**

 - **Reprodutibilidade:**
   - Qualquer pessoa consegue subir seu projeto com o mesmo ambiente que você usa.
 - **Isolamento:**
   - Evita conflitos de versão no Python e dependências.
 - **Customização:**
   - Você pode instalar pacotes de sistema ou bibliotecas específicas.
 - **Portabilidade:**
   - Mesma imagem funciona no seu PC, no servidor ou no CI/CD.

O nosso [Dockerfile](../Dockerfile) vai ficar da seguinte maneira:

[Dockerfile](../Dockerfile)
```bash
# ===============================
# 1️⃣ Imagem base
# ===============================
FROM python:3.12-slim

# ===============================
# 2️⃣ Configuração de ambiente
# ===============================
WORKDIR /code
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/code

# ===============================
# 3️⃣ Dependências do sistema
# ===============================
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    netcat-traditional \
    bash \
    gosu \
    && rm -rf /var/lib/apt/lists/*

# ===============================
# 4️⃣ Instalar dependências Python
# ===============================
COPY requirements-dev.txt /code/
RUN pip install --upgrade pip && pip install -r requirements-dev.txt

# ===============================
# 5️⃣ Copiar código do projeto
# ===============================
COPY . /code/

# ===============================
# 6️⃣ Ajustes de produção
# ===============================
# Criar usuário não-root para segurança
RUN adduser --disabled-password --no-create-home appuser && \
    chown -R appuser /code

# Copia e configura o entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Define o entrypoint (roda como root para ajustar permissões)
# O entrypoint vai mudar para appuser antes de executar o comando
ENTRYPOINT ["/entrypoint.sh"]

# Mantém como root no Dockerfile - o entrypoint gerencia a mudança de usuário
# Isso permite que o entrypoint ajuste permissões antes de mudar para appuser

# ===============================
# 7️⃣ Porta exposta (Uvicorn usa 8000 por padrão)
# ===============================
EXPOSE 8000

# ===============================
# 8️⃣ Comando padrão
# ===============================
# Mantém o container rodando e abre um shell se usado com
# `docker run` sem sobrescrever comando.
CMD ["bash"]
```

> **NOTE:**  
> Acredito que o [Dockerfile](../Dockerfile) está bem descritivo, por isso não vou comentar os comandos.



















































---

<div id="web-docker-compose"></div>

#### `Criando o docker compose para o container web`

> Aqui vamos entender e criar um container contendo o `Django` e o `Uvicorn`.

 - **Função:**
   - Executar a aplicação Django em produção.
 - **Quando usar:**
   - Sempre para servir sua aplicação backend.
 - **Vantagens:**
   - Uvicorn é um servidor WSGI otimizado para produção.
   - Separa lógica da aplicação da entrega de arquivos estáticos.
 - **Desvantagens:**
   - Não serve arquivos estáticos eficientemente.

Antes de criar nosso container contendo o *Django* e o *Uvicorn*, vamos criar as variáveis de ambiente para esse container:

[.env](../.env)
```bash
# ============================================================================
# CONFIGURAÇÃO DO DJANGO
# ============================================================================
DJANGO_SECRET_KEY=djangopass                      # Chave secreta do Django para criptografia e segurança
DJANGO_DEBUG=True                                 # Tru=Dev / False=Prod
DJANGO_ALLOWED_HOSTS=*                            # '*' = libera para qualquer host (apenas desenvolvimento)
DJANGO_SUPERUSER_USERNAME=drigols                 # Nome de usuário do superusuário
DJANGO_SUPERUSER_EMAIL=drigols.creative@gmail.com # Email do superusuário
DJANGO_SUPERUSER_PASSWORD=drigols                 # Senha do superusuário
# ID do site para o framework de sites do Django (usado pelo allauth)
DJANGO_SITE_ID=1
DJANGO_SITE_DOMAIN=localhost
DJANGO_SITE_NAME=Localhost



# ============================================================================
# CONFIGURAÇÃO DO UVICORN
# ============================================================================
UVICORN_HOST=0.0.0.0  # 0.0.0.0 = escutar em todas as interfaces (Docker)
UVICORN_PORT=8000     # Porta interna do app Django
```

Continuando, o arquivo [docker-compose.yml](../docker-compose.yml) para o nosso container *web* ficará assim:

[docker-compose.yml](../docker-compose.yml)
```yml
services:
  # Django/Uvicorn Service
    web:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: django
    restart: always
    env_file: .env
    environment:
      DJANGO_SETTINGS_MODULE: core.settings
    command: >
      sh -c "
      until nc -z ${POSTGRES_HOST} ${POSTGRES_PORT}; do
        echo '⏳ Waiting for Postgres...';
        sleep 2;
      done &&
      python manage.py migrate &&
      python manage.py collectstatic --noinput &&
      python manage.py runserver ${DJANGO_HOST:-0.0.0.0}:${DJANGO_PORT:-8000}
      "
    volumes:
      - .:/code
      - ./static:/code/staticfiles
      - ./media:/code/media
    depends_on:
      - db
      - redis
    ports:
      - "${UVICORN_PORT}:${UVICORN_PORT}"
    networks:
      - backend

networks:
  backend:
```

> **Uma dúvida... tudo que eu modifico no meu projeto principal é alterado no container?**

**SIM!**  
No nosso caso, sim — porque no serviço `web` você fez este mapeamento:

[docker-compose.yml](../docker-compose.yml)
```yaml
volumes:
  - .:/code
```

Isso significa que:

 - O diretório atual no seu `host (.)` é montado dentro do container em `/code`.
 - Qualquer alteração nos arquivos do seu projeto no host aparece instantaneamente no container.
 - E o inverso também vale: se você mudar algo dentro do container nessa pasta, muda no seu host.

Por fim, vamos subir o container web:

```bash
task start_compose
```

Se tudo ocorrer bem você pode abrir no navegador:

 - [http://localhost:8000/](http://localhost:8000/)

Aqui, você também pode ver os logs do container:

```bash
task logs django
```

**OUTPUT:**
```bash
docker logs django
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying auth.0010_alter_group_name_max_length... OK
  Applying auth.0011_update_proxy_permissions... OK
  Applying auth.0012_alter_user_first_name_max_length... OK
  Applying sessions.0001_initial... OK

130 static files copied to '/code/staticfiles'.
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
January 12, 2026 - 00:06:52
Django version 6.0.1, using settings 'core.settings'
Starting development server at http://0.0.0.0:8000/
Quit the server with CONTROL-C.

WARNING: This is a development server. Do not use it in a production setting. Use a production WSGI or ASGI server instead.
For more information on production servers see: https://docs.djangoproject.com/en/6.0/howto/deployment/
[12/Jan/2026 00:07:13] "GET / HTTP/1.1" 200 12068
Not Found: /favicon.ico
[12/Jan/2026 00:07:13] "GET /favicon.ico HTTP/1.1" 404 2206
```



























































---

<div id="django-postgresql-settings"></div>

## `Configurando o Django para reconhecer o PostgreSQL (+ .env) como Banco de Dados`

Antes de começar a configurar o Django para reconhecer o PostgreSQL como Banco de Dados, vamos fazer ele reconhecer as variáveis de ambiente dentro de [core/settings.py](../core/settings.py).

Primeiro, vamos instalar o `python-dotenv` e `psycopg2-binary`:

```bash
poetry add python-dotenv@latest
```

```bash
poetry add psycopg2-binary@latest
```

**NOTE:**  
Aqui também vai ser importante lembrar de exportar essas bibliotecas nos nossos [requirements.txt](../requirements.txt) e [requirements-dev.txt](../requirements-dev.txt):

```bash
task exportdev
```

```bash
task exportprod
```

Ótimo, agora vamos iniciar uma instância de `python-dotenv`:

[core/settings.py](../core/settings.py)
```python
import os

from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
```

> **E agora, como testar que está funcionando?**

Primeiro, imagine que nós temos as seguinte variáveis de ambiente:

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

Agora vamos abrir um **shell interativo do Django**, ou seja, um terminal Python (REPL) com o Django já carregado, permitindo testar código com acesso total ao projeto.

É parecido com abrir um python normal, mas com estas diferenças:

| Recurso                           | Python normal | `manage.py shell` |
| --------------------------------- | ------------- | ----------------- |
| Carrega o Django automaticamente  | ❌ Não       | ✅ Sim            |
| Consegue acessar `settings.py`    | ❌           | ✅                |
| Consegue acessar models           | ❌           | ✅                |
| Consegue consultar banco de dados | ❌           | ✅                |
| Lê o `.env` (se Django carregar)  | ❌           | ✅                |
| Útil para debugar                 | Razoável      | Excelente         |

```bash
python manage.py shell

6 objects imported automatically (use -v 2 for details).
Python 3.12.3 (main, Aug 14 2025, 17:47:21) [GCC 13.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)

>>> import os

>>> print(os.getenv("POSTGRES_HOST"))
db

>>> print(os.getenv("POSTGRES_PASSWORD"))
ragpass
```

> **NOTE:**  
> Vejam que realmente nós estamos conseguindo acessar as variáveis de ambiente.

Continuando, agora vamos dizer ao Django qual Banco de Dados vamos utilizar.

Por exemplo:

[core/settings.py](../core/settings.py)
```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_HOST", "localhost"),
        "PORT": os.getenv("POSTGRES_PORT", 5432),
    }
}
```

No exemplo acima nós temos um dicionário que informa ao Django como conectar ao banco de dados:

 - `ENGINE`
   - Qual backend/driver o Django usa — aqui, PostgreSQL.
 - `NAME`
   - Nome do banco.
 - `USER`
   - Usuário do banco.
 - `PASSWORD`
   - Senha do usuário.
 - `HOST`
   - Host/hostname do servidor de banco.
 - `PORT`
   - Porta TCP onde o Postgres escuta.

#### `O que os.getenv('VAR', 'default') faz, exatamente?`

`os.getenv` vem do módulo padrão `os` e faz o seguinte:

 - Tenta ler a variável de ambiente chamada 'VAR' (por exemplo POSTGRES_DB);
 - Se existir, retorna o valor da variável de ambiente;
 - Se não existir, retorna o valor padrão passado como segundo argumento ('default').

#### `Por que às vezes PASSAMOS um valor padrão (default) no código?`

 - *Conforto no desenvolvimento local:* evita quebrar o projeto se você esquecer de definir `.env`.
 - *Documentação inline:* dá uma ideia do nome esperado (easy_rag, 5432, etc.).
 - *Teste rápido:* você pode rodar `manage.py` localmente sem carregar variáveis.

> **NOTE:**  
> Mas atenção: os valores padrões não devem conter segredos reais (ex.: supersecret) no repositório público — isso é um risco de segurança.

#### `Por que você não deveria colocar senhas no código?`

 - Repositórios (Git) podem vazar ou ser lidos por terceiros.
 - Código pode acabar em backups, imagens Docker, etc.
 - Difícil rotacionar/chavear senhas se espalhadas pelo repositório.

> **Regra prática:**  
> - *"NUNCA"* colocar credenciais reais em `settings.py`.
> - Use `.env` (não comitado) ou um *"secret manager"*.



















































---

<div id="nginx-container"></div>

## `Criando o container Nginx (nginx | +Reverse Proxy)`

Para entender a necessidade do Nginx, vamos começar imaginando que nós criamos uma conta de **super usuário** no Django (pode ser na sua máquina local mesmo):

**Roda/Executa o comando "createsuperuser" a partir do serviçor "web":**
```bash
docker compose exec web python manage.py createsuperuser
```

Agora é só abrir o **Django Admin** e verificar se temos a tabela `users`:

 - [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

![img](images/nginx-01.png)  

Vejam que:

 - Está tudo mal formado;
 - Sem estilização (CSS)...

> **Por que isso?**

 - **Executando/Rodando na máquina local**:
   - Quando você roda o Django na sua máquina local (fora do container), ele serve os arquivos estáticos automaticamente porque:
     - `DEBUG=True`
     - O servidor de desenvolvimento (runserver) serve /static/ diretamente.
 - **Executando/Rodando no container**:
   - Mas dentro do Docker, o **servidor Uvicorn não serve arquivos estáticos por padrão**.
   - Uvicorn é um ASGI server puro, *não um servidor web completo (como o runserver do Django)*.
   - **NOTE:** Por isso, o Django Admin aparece sem CSS.

> **Como resolver isso? Usando Nginx**

Para ambientes de produção profissional, você deve:

 - Deixar o Uvicorn apenas para as requisições dinâmicas (ASGI);
 - Deixar o Nginx servir `/static/` e `/media/` diretamente.

Ou seja, o Nginx vai ter as seguintes características (nesse projeto):

 - **Função:**
   - Servir arquivos estáticos e atuar como *proxy reverso* para o Django.
 - **Quando usar:**
   - Sempre em produção para segurança e desempenho.
 - **Reverse proxy:**
   - Receber as requisições HTTP/HTTPS dos clientes.
   - Redirecionar (proxy_pass) para seu container Django (web).
   - Isso permite que seu backend fique “escondido” atrás do Nginx, ganhando segurança e performance.
 - **Servir arquivos estáticos e de mídia diretamente:**
   - Em Django, arquivos estáticos (/static/) e de upload (/media/) não devem ser servidos pelo Uvicorn (ineficiente).
   - O Nginx é muito melhor para isso, então ele entrega esses arquivos direto do volume.
 - **HTTPS (SSL/TLS):**
   - Configurar certificados (ex.: Let’s Encrypt) para rodar sua aplicação com HTTPS.
   - O Django não lida com certificados nativamente, então o Nginx faz esse papel.
 - **Balanceamento e cache (futuro):**
   - Se você crescer, pode colocar vários containers de Django e usar o Nginx como load balancer.
   - Também pode configurar cache de páginas ou de assets.
 - **Vantagens:**
   - Muito rápido para servir arquivos estáticos.
   - HTTPS e balanceamento de carga.
 - **Desvantagens:**
   - Exige configuração inicial extra.
 - **👉 Resumindo:**
   - O Nginx é a porta de entrada da sua aplicação, cuidando de performance, segurança e organização.

**NOTE:**  
Mas antes de criar e iniciar o nosso container com Nginx, vamos alterar uma configuração no nosso container `web`:

[docker-compose.yml](../docker-compose.yml)
```yaml
  web:

    ...

    expose:
      - "8000"

    ...
```

> **O que mudou?**

 - **Antes nós tinhamos:**
   - `ports: "${UVICORN_PORT}:${UVICORN_PORT}"`
   - ✅ Antes (ports) — Tornava a porta 8000 acessível externamente no host (ex.: http://localhost:8000).
 - **Agora nós temos:**
   - `expose: ["8000"]`
   - ✅ Agora (expose) — Deixa a porta 8000 visível apenas entre containers na rede Docker, invisível fora.

Com essa alteração feita, agora vamos criar/configurar o [docker-compose.yml](../docker-compose.yml) para o nosso container `nginx`:

[docker-compose.yml](../docker-compose.yml)
```yml
services:
  nginx:
    image: nginx:1.27
    container_name: nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf
      - ./static:/code/staticfiles
      - ./media:/code/media
    depends_on:
      - web
    networks:
      - backend

networks:
  backend:
```

 - `nginx:`
   - Nome do *serviço (container)* criado pelo docker-compose.
 - `image: nginx:1.27`
   - Pega a versão 1.27 oficial do Nginx no Docker Hub.
 - `container_name: nginx_reverse_proxy`
   - Nome fixo do container (para facilitar comandos como docker logs nginx_server).
 - `restart: always`
   - 🔹 O container vai voltar sempre que o Docker daemon subir, independente do motivo da parada.
   - 🔹 Mesmo se você der *docker stop*, quando o host reiniciar o container volta sozinho.
   - 👉 Bom para produção quando você quer *99% de disponibilidade*.
 - `ports:`
   - Mapeia portas do host para o container:
     - `80:80` → HTTP
     - `443:443` → HTTPS
 - `volumes:`
   - Pasta local `./nginx/conf` → onde ficam configs do Nginx.
   - Volumes `static` e `media` para servir arquivos.
 - `depends_on:`
   - Só inicia depois que o `Django (web)` estiver rodando.
 - `networks: backend`
   - Rede interna para conversar com Django sem expor a aplicação diretamente.

Agora, nós precisamos criar o arquivo de configuração do `Nginx`:

[nginx.conf](../nginx/nginx.conf)
```bash
# ============================================================================
# CONFIGURAÇÃO DO SERVIDOR WEB NGINX
# ============================================================================
#
# Este arquivo configura o Nginx como proxy reverso para a aplicação
# Django, servindo arquivos estáticos e mídia diretamente e repassando
# requisições dinâmicas para o servidor de aplicação (Uvicorn/Gunicorn).
#
# Estrutura:
# - Configurações gerais do servidor
# - Servir arquivos estáticos (CSS, JS, imagens)
# - Servir arquivos de mídia (uploads dos usuários)
# - Proxy reverso para aplicação Django
#
# ============================================================================
# CONFIGURAÇÃO DO SERVIDOR VIRTUAL
# ============================================================================

server {
    # Porta na qual o servidor escuta requisições HTTP
    listen 80;
    
    # Nome do servidor (aceita qualquer nome de domínio)
    # Em produção, substitua por um domínio específico
    server_name _;

    # ========================================================================
    # CONFIGURAÇÕES GLOBAIS DO SERVIDOR
    # ========================================================================
    
    # Tamanho máximo do corpo da requisição (0 = ilimitado)
    # Permite uploads de qualquer tamanho - a validação é feita pelo Django
    # Em produção, considere definir um limite adequado (ex: 100M)
    client_max_body_size 0;

    # ========================================================================
    # SERVIÇO DE ARQUIVOS ESTÁTICOS
    # ========================================================================
    
    # Localização para servir arquivos estáticos (CSS, JS, imagens)
    # Estes arquivos são coletados pelo Django via 'collectstatic'
    location /static/ {
        # Caminho no sistema de arquivos onde os estáticos estão
        alias /code/staticfiles/;
        
        # Cache do navegador por 30 dias
        expires 30d;
        
        # Desabilita logs de acesso para melhorar performance
        access_log off;
        
        # Habilita listagem de diretórios (útil para debug)
        autoindex on;
    }

    # ========================================================================
    # SERVIÇO DE ARQUIVOS DE MÍDIA
    # ========================================================================
    
    # Localização para servir arquivos de mídia (uploads dos usuários)
    # Estes arquivos são enviados pelos usuários e armazenados pelo Django
    location /media/ {
        # Caminho no sistema de arquivos onde os arquivos de mídia estão
        alias /code/media/;
        
        # Cache do navegador por 30 dias
        expires 30d;
        
        # Desabilita logs de acesso para melhorar performance
        access_log off;
        
        # Habilita listagem de diretórios (útil para debug)
        autoindex on;
    }

    # ========================================================================
    # PROXY REVERSO PARA APLICAÇÃO DJANGO
    # ========================================================================
    
    # Todas as outras requisições são repassadas para o servidor Django
    # O Nginx atua como proxy reverso, melhorando performance e segurança
    location / {
        # URL do servidor de aplicação (Django via Uvicorn/Gunicorn)
        # 'web' é o nome do serviço no Docker Compose
        proxy_pass http://web:8000;
        
        # Headers necessários para o Django funcionar corretamente
        # Preserva o host original da requisição
        proxy_set_header Host $host;
        
        # IP real do cliente (importante para logs e segurança)
        proxy_set_header X-Real-IP $remote_addr;
        
        # Cadeia de IPs em caso de múltiplos proxies
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # Protocolo original (http ou https)
        # Necessário para o Django detectar requisições HTTPS
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Por fim, vamos subir o container `nginx`:

```bash
task start_compose
```

 - **🧩 Fluxo de funcionamento**
   - `Uvicorn (web)` executa o Django e responde às rotas dinâmicas.
   - `Nginx` recebe todas as requisições HTTP externas:
     - `/static/` → servido diretamente da pasta staticfiles;
     - `/media/` → servido diretamente da pasta media;
     - outras rotas → redirecionadas para o container web (Uvicorn).
   - `PostgreSQL` e Redis são usados internamente via rede backend.

Agora tente abrir:

 - [http://localhost:8000/](http://localhost:8000/)
 - [http://localhost:8000/admin/](http://localhost:8000/admin/)

> **What? Não funcionou!**  
> 👉 Porque o Nginx está na porta 80 e o Uvicorn está atrás dele, **exposto (expose)** apenas internamente no Docker.

Agora para acessar nossa aplicação `web` primeiro nós devemos passar pelo container `nginx`:

 - [http://localhost/](http://localhost/)
 - [http://localhost/admin/](http://localhost/admin/)

> **Explicando brevemente:**  
> O container *nginx* atua como `reverse proxy`; ele recebe todas as requisições HTTP (nas portas 80/443) e as encaminha internamente para o container web (Uvicorn/Django).

Agora você pode abrir o seu Django Admin que estará tudo disponível pelo Nginx:

![img](images/nginx-02.png)  

> **Mas como eu testo se meu nginx está funcionando corretamente?**

Primeiro, vamos ver se há mensagem de erro dentor do container `nginx`:

```bash
docker logs nginx
```

**OUTPUT:**
```bash
/docker-entrypoint.sh: /docker-entrypoint.d/ is not empty, will attempt to perform configuration
/docker-entrypoint.sh: Looking for shell scripts in /docker-entrypoint.d/
/docker-entrypoint.sh: Launching /docker-entrypoint.d/10-listen-on-ipv6-by-default.sh
10-listen-on-ipv6-by-default.sh: info: Getting the checksum of /etc/nginx/conf.d/default.conf
10-listen-on-ipv6-by-default.sh: info: /etc/nginx/conf.d/default.conf differs from the packaged version
/docker-entrypoint.sh: Sourcing /docker-entrypoint.d/15-local-resolvers.envsh
/docker-entrypoint.sh: Launching /docker-entrypoint.d/20-envsubst-on-templates.sh
/docker-entrypoint.sh: Launching /docker-entrypoint.d/30-tune-worker-processes.sh
/docker-entrypoint.sh: Configuration complete; ready for start up
2025/11/10 13:10:11 [notice] 1#1: using the "epoll" event method
2025/11/10 13:10:11 [notice] 1#1: nginx/1.27.5
2025/11/10 13:10:11 [notice] 1#1: built by gcc 12.2.0 (Debian 12.2.0-14)
2025/11/10 13:10:11 [notice] 1#1: OS: Linux 6.6.87.2-microsoft-standard-WSL2
2025/11/10 13:10:11 [notice] 1#1: getrlimit(RLIMIT_NOFILE): 1048576:1048576
2025/11/10 13:10:11 [notice] 1#1: start worker processes
2025/11/10 13:10:11 [notice] 1#1: start worker process 28
2025/11/10 13:10:11 [notice] 1#1: start worker process 29
2025/11/10 13:10:11 [notice] 1#1: start worker process 30
2025/11/10 13:10:11 [notice] 1#1: start worker process 31
2025/11/10 13:10:11 [notice] 1#1: start worker process 32
2025/11/10 13:10:11 [notice] 1#1: start worker process 33
2025/11/10 13:10:11 [notice] 1#1: start worker process 34
2025/11/10 13:10:11 [notice] 1#1: start worker process 35
172.18.0.1 - - [10/Nov/2025:13:10:28 +0000] "GET / HTTP/1.1" 200 12068 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36" "-"
172.18.0.1 - - [10/Nov/2025:13:10:28 +0000] "GET /favicon.ico HTTP/1.1" 404 2201 "http://localhost/" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36" "-"
172.18.0.1 - - [10/Nov/2025:13:10:39 +0000] "GET /admin/ HTTP/1.1" 302 0 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36" "-"
172.18.0.1 - - [10/Nov/2025:13:10:39 +0000] "GET /admin/login/?next=/admin/ HTTP/1.1" 200 4173 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36" "-"
172.18.0.1 - - [10/Nov/2025:13:15:32 +0000] "GET / HTTP/1.1" 200 12068 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36" "-"
172.18.0.1 - - [10/Nov/2025:13:18:29 +0000] "GET / HTTP/1.1" 200 12068 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36" "-"
172.18.0.1 - - [10/Nov/2025:13:18:29 +0000] "GET /favicon.ico HTTP/1.1" 404 2201 "http://localhost/" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36" "-"
172.18.0.1 - - [10/Nov/2025:13:18:30 +0000] "GET /admin/ HTTP/1.1" 302 0 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36" "-"
172.18.0.1 - - [10/Nov/2025:13:18:30 +0000] "GET /admin/login/?next=/admin/ HTTP/1.1" 200 4173 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36" "-"
```

Ótimo, agora vamos fazer alguns testes no navegador:

 - http://localhost/static/ → deve(ria) exibir arquivos estáticos.
 - http://localhost/media/ → deve(ria) exibir uploads.

**OUTPUT:**
```bash
403 Forbidden
nginx/1.27.5
```

> **What? Não funcionou!**

Agora vamos tentar acessar um arquivo específico:

 - http://localhost/static/admin/css/base.css
 - http://localhost/static/admin/img/inline-delete.svg

> **What? Agora funcionou!**

 - Esse comportamento indica que o *Nginx* está conseguindo servir arquivos existentes, mas não consegue listar diretórios.
 - **NOTE:** Por padrão, o Nginx não habilita autoindex (listagem de diretórios).

Então:

 - http://localhost/static/admin/css/base.css → Funciona porque você está acessando um arquivo específico.
 - http://localhost/static/ → Dá *403 Forbidden* porque você está acessando o diretório, e o Nginx não lista o conteúdo (diretório) por padrão.

> **Como resolver isso?**

#### Habilitar autoindex (não recomendado para produção, só para teste):

[nginx.conf](../nginx/conf/nginx.conf)
```bash
location /static/ {
    alias /code/staticfiles/;
    autoindex on;
}

location /media/ {
    alias /code/media/;
    autoindex on;
}
```

**Força recriar o container `nginx`**:
```
docker compose up -d --force-recreate nginx
```

> **NOTE:**  
> Isso permite ver os arquivos listados no navegador, mas não é seguro em produção, porque expõe todos os arquivos publicamente.

Agora, abra diretamente algum arquivo, como:

 - [http://localhost/static/admin/css/base.css](http://localhost/static/admin/css/base.css)
 - [http://localhost/media/example.txt](http://localhost/media/example.txt)
   - Crie esse arquivo em `/media (host)` antes de tentar acessar (testar).

Se esses arquivos carregarem, significa que tudo está correto para servir conteúdo estático e uploads, mesmo que a listagem do diretório não funcione.

> **💡 Resumo:**  
> O erro `403` ao acessar `/static/` ou `/media/` é normal no Nginx quando você não habilita `autoindex`. Para produção, você normalmente não quer listar diretórios, apenas servir arquivos diretamente.

Outra maneira de testar se o Nginx está funcionando corretamente seria usar o `curl`:

```bash
curl http://localhost/static/admin/css/base.css -I
```

**OUTPUT:**
```bash
HTTP/1.1 200 OK
Server: nginx/1.27.5
Date: Tue, 19 Aug 2025 02:29:18 GMT
Content-Type: text/css
Content-Length: 22120
Last-Modified: Tue, 19 Aug 2025 01:58:34 GMT
Connection: keep-alive
ETag: "68a3da4a-5668"
Accept-Ranges: bytes
```

```bash
curl http://localhost/media/example.txt -I
```

**OUTPUT:**
```bash
HTTP/1.1 200 OK
Server: nginx/1.27.5
Date: Tue, 19 Aug 2025 02:30:17 GMT
Content-Type: text/plain
Content-Length: 15
Last-Modified: Tue, 19 Aug 2025 02:26:29 GMT
Connection: keep-alive
ETag: "68a3e0d5-f"
Accept-Ranges: bytes
```

```bash
curl http://localhost/static/admin/img/inline-delete.svg -I
```

**OUTPUT:**
```bash
HTTP/1.1 200 OK
Server: nginx/1.27.5
Date: Tue, 19 Aug 2025 02:33:07 GMT
Content-Type: image/svg+xml
Content-Length: 537
Last-Modified: Tue, 19 Aug 2025 01:58:34 GMT
Connection: keep-alive
ETag: "68a3da4a-219"
Accept-Ranges: bytes
```

 - Vejam que quem está servindo os dados é o servidor Nginx e não o Django (container web).
 - Além, disso nós também estamos vendo algumas informações interessantes sobre os arquivos:
   - tipo: `text/css`, `text/plain`, `image/svg+xml`, etc.



















































---

<div id="ruff-settings-pyproject"></div>

## `Instalando e configurando o Ruff`

 - Antes de cair de cobeça na codificação do nosso projeto é interessante criar um mecanismo de verificação de qualidade de código.
 - Para isso vamos utilizar a ferramenta [Ruff](https://github.com/astral-sh/ruff)

De início, vamos instalar e configurar o **Ruff** no nosso `pyproject.toml`:

```bash
poetry add --group dev ruff@latest
```

Agora, vamos atualizar essa bibliota nos nossos [requirments.txt](../requirements.txt) e [requirments-dev.txt](../requirements-dev.txt):

```bash
task exportdev
```

```bash
task exportprod
```

#### `[tool.ruff]`

> Esse bloco define às *Regras Gerais de funcionamento do (Ruff)*.

[pyproject.toml](../pyproject.toml)
```toml
[tool.ruff]
line-length = 79
exclude = [
    "core/settings.py",
]
```

 - `line-length = 79`
   - Define que nenhuma linha de código deve ultrapassar 79 caracteres *(seguindo o padrão tradicional do PEP 8)*.
   - É especialmente útil para manter legibilidade em terminais com largura limitada.
   - Ruff irá avisar (e, se possível, corrigir) quando encontrar linhas mais longas.
 - `exclude = ["core/settings.py"]`
   - Define quais arquivos o Ruff deve ignorar:
     - Nesse caso, ele vai ignorar o arquivo `core/settings.py`.

#### `[tool.ruff.lint]`

Esse é o sub-bloco principal de configuração de linting do Ruff, ou seja, onde você define como o Ruff deve analisar o código quanto a erros, estilo, boas práticas etc.

[pyproject.toml](../pyproject.toml)
```toml
[tool.ruff.lint]
preview = true
select = ['I', 'F', 'E', 'W', 'PL', 'PT']
```

 - `preview = true`
   - Ativa regras experimentais (em fase de teste, mas estáveis o suficiente).
   - Pode incluir novas verificações que ainda não fazem parte do conjunto padrão.
   - Útil se você quer estar sempre com o Ruff mais “rigoroso” e atualizado.
 - `select = ['I', 'F', 'E', 'W', 'PL', 'PT']`
   - Define quais conjuntos de regras (lints) o Ruff deve aplicar ao seu código. Cada uma dessas letras corresponde a um grupo de regras:
     - `I` ([Isort](https://pycqa.github.io/isort/)): Ordenação de imports em ordem alfabética.
     - `F` ([Pyflakes](https://github.com/PyCQA/pyflakes)): Procura por alguns erros em relação a boas práticas de código.
     - `E` ([pycodestyle](https://pycodestyle.pycqa.org/en/latest/)): Erros de estilo de código.
     - `W` ([pycodestyle](https://pycodestyle.pycqa.org/en/latest/)): Avisos sobre estilo de código.
     - `PL` ([Pylint](https://pylint.pycqa.org/en/latest/index.html)): "erros" em relação a boas práticas de código.
     - `PT` ([flake8-pytest](https://pypi.org/project/flake8-pytest-style/)): Boas práticas do Pytest.

#### `[tool.ruff.format]`

O bloco [tool.ruff.format] é usado para configurar o formatador interno do Ruff, que foi introduzido recentemente como uma alternativa ao Black — mas com a vantagem de ser muito mais rápido.

```toml
[tool.ruff.format]
preview = true
quote-style = "double"
```

 - `preview = true`
   - Ativa regras experimentais (em fase de teste, mas estáveis o suficiente).
 - `quote-style = "double"`
   - Define o estilo de aspas (duplas no nosso caso) usadas pelo formatador.

Por fim, vamos adicionar o comando Taskipy responsável por executar o Ruff:

[pyproject.toml](../pyproject.toml)
```toml
[tool.taskipy.tasks]
# ------------------------ ( Linting ) ----------------------
pre_lint = 'ruff check --fix'
lint = 'ruff check'
```



















































---

<div id="pytest-settings-pyproject"></div>

## `Instalando e configurando o Pytest`

 - Nós também vamos precisar de um mecanismo para verificação de qualidade de código referente a testes.
 - Para isso vamos utilizar a biblioteca [Pytest](https://github.com/pytest-dev/pytest).

De início, vamos *instalar* e *configurar* o **Pytest** no nosso `pyproject.toml`.

```bash
poetry add --group dev pytest@latest
```

```bash
poetry add --group dev pytest-cov@latest
```

```bash
poetry add --group dev pytest-django@latest
```

Agora, vamos atualizar essa bibliota nos nossos [requirments.txt](../requirements.txt) e [requirments-dev.txt](../requirements-dev.txt):

```bash
task exportdev
```

```bash
task exportprod
```

Agora, vamos criar uma seção no nosso [pyproject.toml](../pyproject.toml) que é equivalente a ter um arquivo `pytest.ini` separado:

[pyproject.toml](../pyproject.toml)
```toml
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "core.settings"
python_files = ["tests.py", "test_*.py", "*_tests.py"]
```

 - `DJANGO_SETTINGS_MODULE = "core.settings"`
   - Define qual arquivo de configuração do Django o pytest deve usar durante os testes
   - É o equivalente a fazer `export DJANGO_SETTINGS_MODULE=core.settings` no terminal
   - **Por que é necessário?**
     - O Django precisa saber qual settings.py usar para configurar o banco de dados, apps instalados, middlewares, etc.
     - Sem isso, você receberia erros tipo: "Django is not configured"
 - `python_files = ["tests.py", "test_*.py", "*_tests.py"]`
   - Define quais arquivos o pytest deve considerar como arquivos de teste
   - Aceita 3 padrões de nomenclatura:
     - `tests.py` - arquivo único chamado exatamente "tests.py"
     - `test_*.py` - qualquer arquivo começando com "test_" (ex: test_models.py, test_views.py)
     - `*_tests.py` - qualquer arquivo terminando com "_tests" (ex: models_tests.py, views_tests.py)

**EXEMPLO NA PRÁTICA:**
```bash
myapp/
├── tests.py          ✅ Será executado
├── test_models.py    ✅ Será executado
├── test_views.py     ✅ Será executado
├── models_tests.py   ✅ Será executado
├── views.py          ❌ NÃO será executado (não segue os padrões)
└── my_test.py        ❌ NÃO será executado (não segue os padrões)
```

Continuando, agora vamos ativar a descoberta automática de projetos Django pelo [pytest-django](https://github.com/pytest-dev/pytest-django):

[pyproject.toml](../pyproject.toml)
```toml
[tool.pytest.ini_options]
django_find_project = true
```

 - `django_find_project = true`
   - Diz ao [pytest-django](https://github.com/pytest-dev/pytest-django) para procurar automaticamente a raiz do projeto Django
   - Ele sobe na hierarquia de diretórios até encontrar o [manage.py](../manage.py)

**Sem django_find_project = true:**
```bash
# Você precisa estar EXATAMENTE na raiz do projeto
cd /projeto/
pytest  # ✅ Funciona

cd /projeto/myapp/
pytest  # ❌ Erro: Django is not configured
```

**Com django_find_project = true:**
```bash
# Funciona de QUALQUER subdiretório
cd /projeto/myapp/tests/
pytest  # ✅ Funciona! Encontra o manage.py automaticamente

cd /projeto/myapp/
pytest  # ✅ Funciona!

cd /projeto/
pytest  # ✅ Funciona!
```

Agora, vamos adicionar algumas configurações na seção que mede a cobertura de testes: `[tool.coverage.run]`

[pyproject.toml](../pyproject.toml)
```toml
[tool.coverage.run]
omit = [
    "*/__init__.py",
    "*/migrations/*",
]
```

> **NOTE:**  
> Na verdade, o que estamos dizendo é que não vamos medir a cobertura de arquivos `__init__.py` ou `migrations/`

Por fim, vamos adicionar o comando Taskipy responsável por executar o Pytest:

[pyproject.toml](../pyproject.toml)
```toml
[tool.taskipy.tasks]
# ------------------------ ( Testing ) ----------------------
test = "docker compose exec -T web pytest -s -x --cov=. -vv"
post_test = 'docker compose exec -T web coverage html'
```



















































---

<div id="precommit-settings"></div>

## `Instalando e configurando o pre-commit`

Para garantir que antes de cada commit seu projeto passe por:

 - ✅ lint (usando Ruff)
 - ✅ test (com pytest)
 - ✅ coverage

Você deve usar o pre-commit — uma ferramenta leve e ideal para isso. Vamos configurar passo a passo:

```bash
poetry add --group dev pre-commit
```

Novamente, vamos atualizar essa bibliota nos nossos [requirments.txt](../requirements.txt) e [requirments-dev.txt](../requirements-dev.txt):

```bash
task exportdev
```

```bash
task exportprod
```

Agora, vamos inciar o arquivo [.pre-commit-config.yaml](../.pre-commit-config.yaml) com a seguinte configuração:

[.pre-commit-config.yaml](../.pre-commit-config.yaml)
```yaml
repos:
  - repo: local
    hooks:
```

### `repos:`

 - A lista de repositórios de onde os hooks do pre-commit virão
 - Um arquivo .pre-commit-config.yaml pode ter vários repositórios configurados

**EXEMPLO:**
```yaml
repos:
  - repo: https://github.com/psf/black
    # hooks do black aqui
  
  - repo: https://github.com/pycqa/flake8
    # hooks do flake8 aqui
  
  - repo: local
    # hooks locais aqui
```

### `repo: local`

 - Define um repositório do tipo "local"
 - Os hooks NÃO vêm de um repositório externo do GitHub
 - Os hooks são definidos no próprio projeto

**Repositório Externo (padrão):**
```yaml
- repo: https://github.com/psf/black
  rev: 23.12.1  # Versão específica
  hooks:
    - id: black
```

 - ✅ Hooks prontos da comunidade
 - ✅ Versionados e testados
 - ❌ Menos flexibilidade

**Repositório Local (local):**
```yaml
- repo: local
  hooks:
    - id: meu-hook-customizado
      name: Meu Hook
      entry: ./meu-script.sh
      language: system
```

 - ✅ Total controle e customização
 - ✅ Usa ferramentas já instaladas no projeto
 - ✅ Pode rodar comandos específicos do seu workflow
 - ❌ Você mantém o código

### `hooks:`

 - Lista de hooks (ganchos) que serão executados
 - Cada hook é uma verificação ou ação que roda antes do commit

**Estrutura de um hook:**
```yaml
hooks:
  - id: nome-unico-do-hook
    name: Nome legível para humanos
    entry: comando a ser executado
    language: system
    types: [python]
    pass_filenames: false
```

### `Hook do Ruff no Pre-commit`

[.pre-commit-config.yaml](../.pre-commit-config.yaml)
```yaml
repos:
  - repo: local
    hooks:

      # ---------------------------------------------
      #  LINT (somente quando arquivos Python mudarem)
      # ---------------------------------------------
      - id: ruff-lint
        name: ruff check
        entry: task lint
        language: system
        types: [python]
        pass_filenames: false
        exclude: >
          ^(
            .*/migrations/.*|
          )
```

> **O que este hook faz?**

Toda vez que você tentar fazer um `git commit`, ANTES do commit ser criado, este hook:

 - Roda o comando `task lint` (que executa o Ruff)
 - Verifica se há problemas de estilo/qualidade no código Python
 - Bloqueia o commit se encontrar erros
 - Permite o commit se tudo estiver OK

 - `id: ruff-lint`
   - Identificador único do hook dentro do arquivo de configuração
   - Usado para referenciar este hook especificamente
   - Você pode rodar só este hook com: `pre-commit run ruff-lint`
   - **NOTE:** Deve ser único dentro do arquivo
 - `name: ruff check`
   - Nome legível que aparece no terminal quando o hook executa
   - É o que você vê na saída: `ruff check........Passed`
   - Pode ser qualquer texto descritivo
   - Não precisa ser igual ao id
 - `entry: task lint`
   - Comando que será executado quando o hook rodar
   - No seu caso, chama `task lint` (definido no [pyproject.toml](../pyproject.toml))
   - task lint provavelmente executa ruff check ou similar
 - `language: system`
   - **Qual "ambiente" usar para executar o comando:**
     - system = usar o ambiente do sistema operacional atual
     - Não cria ambiente virtual isolado
     - Usa o Python/ferramentas já instaladas na sua máquina
   - **Outras opções:**
     - python = cria venv isolado e instala dependências
     - node = usa Node.js
     - docker = roda em container
     - script = executa script shell
   - **Por que system no nosso caso:**
     - Nós já temos task e ruff instalados
     - Mais rápido (não cria ambientes isolados)
     - Usa a versão do Ruff do nosso projeto
 - `types: [python]`
   - Filtro de tipos de arquivos que ativam este hook
   - Só executa se arquivos Python forem modificados
   - Ignora commits que só alteram `.md`, `.txt`, `.json`, `etc`.
   - **Poderia ser mais de um tipo? SIM!**
     - `types: [python, yaml, toml]`
     - **NOTE:** Nesse caso, o hook será acionado se qualquer arquivo *Python*, *YAML* ou *TOML* for modificado.
 - `pass_filenames: false`
   - Com `pass_filenames: false`, vocé NÃO passar os nomes dos arquivos modificados para o comando.
   - **Com pass_filenames: true (padrão):**
     - `# Pre-commit passaria os arquivos modificados:`
     - `task lint myapp/views.py myapp/models.py`
   - **Com pass_filenames: false:**
     - `# Pre-commit roda sem argumentos:`
     - `task lint`
     - `# E o Ruff verifica TODO o projeto, não só arquivos modificados`
   - **Por que usar false?**
     - ✅ Garante consistência em TODO o código
     - ✅ Ruff é rápido o suficiente para verificar tudo
     - ✅ Evita que erros antigos passem despercebidos
     - ❌ Pode ser mais lento em projetos grandes
 - `exclude:`
   - Arquivos ou pastas que devem ser ignorados pelo hook

> **NOTE:**  
> Não vou mais explicar os demais hooks linh a linha porque a partir deste já dá para entender a maioria dos comandos.

### `.pre-commit-config.yaml completo`

[.pre-commit-config.yaml](../.pre-commit-config.yaml)
```yaml
repos:
  - repo: local
    hooks:

      # ---------------------------------------------
      #  LINT (somente quando arquivos Python mudarem)
      # ---------------------------------------------
      - id: ruff-lint
        name: ruff check
        entry: task lint
        language: system
        types: [python]
        pass_filenames: false
        exclude: >
          ^(
            .*/migrations/.*|
          )

      # --------------------------------------------------------
      #  PYTEST (executado dentro do container web)
      #  • Só roda se arquivos Python mudarem
      #  • Usa -T para evitar erro "not a TTY"
      # --------------------------------------------------------
      - id: pytest-test
        name: run pytest inside docker
        entry: docker compose run -T --rm web pytest -s -x --cov=. -vv
        language: system
        types: [python]
        pass_filenames: false
        exclude: >
          ^(
            .*/migrations/.*|
          )

      # --------------------------------------------------------
      #  COVERAGE MINIMUM (falha se < 70%)
      # --------------------------------------------------------
      - id: pytest-coverage
        name: coverage threshold
        entry: docker compose run -T --rm web pytest --cov=. --cov-fail-under=70
        language: system
        types: [python]
        pass_filenames: false
        exclude: >
          ^(
            .*/migrations/.*|
          )
```

Agora nós precisamos instalar o pre-commit para esses hooks funcionarem corretamente:

```bash
pre-commit install
```

#### Dica extra: Se quiser rodar manualmente

```bash
pre-commit run --all-files
```

Por fim, vamos adicionar o comando Taskipy responsável por executar o pre-commit:

[pyproject.toml](../pyproject.toml)
```toml
[tool.taskipy.tasks]
# ---------------------- ( Pre-Commit ) ---------------------
precommit = 'pre-commit run --all-files'
```





















































---

<div id="github-workflows"></div>

## `Criando o diretório (pasta) .github/workflows/`

Aqui vamos criar o diretório (pasta) [.github/workflows](.github/workflows) que é uma pasta especial que fica dentro do seu repositório no GitHub.

> 👉 É aqui onde você vai definir os fluxos de automação que o GitHub deve executar automaticamente — chamados de workflows.

Esses workflows são escritos em `YAML (.yml)`, e dizem ao GitHub:

 - Quando executar algo (gatilhos/triggers como push, pull request, etc.);
 - Em qual ambiente executar (como Ubuntu, Windows, etc.);
 - O que deve ser executado (os comandos, scripts ou jobs).

Por exemplo:

```bash
your-repo/
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
```

Cada arquivo `.yml` dentro de [.github/workflows](.github/workflows) representa um workflow independente.

Por exemplo:

 - `ci.yml` → Faz testes automáticos e checa o código (CI = Continuous Integration);
 - `deploy.yml` → Envia o código para o servidor (CD = Continuous Deployment).

#### `O que é um “workflow” no GitHub Actions?`

Um *workflow* é composto de:

 - **Trigger (gatilho)** → Quando ele deve rodar;
 - **Jobs (tarefas)** → O que ele faz (como rodar testes, buildar imagem, etc.);
 - **Steps (passos)** → Os comandos de cada tarefa

#### `Cobrindo os testes com codecov.io`

 - **Acesse: https://app.codecov.io/gh**
   - Selecione seu repositório.
 - **"Select a setup option"**:
   - Selecione -> Using GitHub Actions
 - **"Step 1: Output a Coverage report file in your CI"**
   - Selecione -> Pytest
   - ...
 - **Step 3: add token as repository secret**
   - Copie -> CODECOV_TOKEN
   - Copie -> SUA-CHAVE-SECRETA
   - **NOTE:** Você vai utilizar eles no workflow `.github/workflows/ci.yml` (ex: [env](#env)).

Ótimo, agora você já tem a chave secreta para o Codecov, vá em:

 - Seu projeto/settings;
 - secrets and variables:
   - Actions.

Continuando, agora você vai clicar em `New repository secret` e adicionar:

 - Name: `CODECOV_TOKEN`
 - Secret: `YOUR-CODECOV-TOKEN`
 - Finalmente, clicar em "Add Secret".

Por fim, vamos adicionar os badges do **Codecov** e do **Pipeline**:

 - Para obter um *Pipeline badge*, altere o link abaixo para o repositório/CI-CD do seu projeto:
   - `[![CI](https://github.com/rodrigols89/ragproject/actions/workflows/ci.yml/badge.svg)](https://github.com/rodrigols89/ragproject/actions/workflows/ci.yml)`
 - Para obter um *Codecov badge*:
   - Acesse [https://app.codecov.io/gh/](https://app.codecov.io/gh/)
   - Selecione o projeto que está sendo monitorado pela cobertura de testes.
   - Vá em **Settings > Badges & Graphs > Markdown** e copie o badge gerado:



















































---

<div id="github-workflows-lint-yml"></div>

## `Criando o workflow lint.yml`

> Aqui nós vamos cria o *workflow* que vai fazer a *verificação* de *lint* no código.

De início, vamos começar dando um nome a esse workflow:

[lint.yml](../.github/workflows/lint.yml)
```yaml
name: Lint
```

Agora, nós vamos adicionar os gatilhos (triggers) que acionarão esse workflow:

[lint.yml](../.github/workflows/lint.yml)
```yaml
on:
  push:
    branches: [ ci-cd ]
    paths:
      - "**/*.py"
      - "requirements*.txt"
      - "pyproject.toml"
  pull_request:
    branches: [ ci-cd ]
    paths:
      - "**/*.py"
      - "requirements*.txt"
      - "pyproject.toml"
```

 - `on:`
   - Você pode pensar no comando `on`, como:
     - "Toda vez que o repositório receber o comando *x ("push" e "pull_request" no nosso caso)*.
 - `push:`
     - Gatilho (trigger) do workflow.
   - `branches: [ ci-cd ]`
     - Branches que executarão as tarefas, no nosso caso, é *"ci-cd"*;
     - ci-cd já garante a qualidade do código;
     - *"main"* normalmente só recebe merges já validados.
   - `paths:`
     - Só executa quando houver mudanças em `arquivos Python`, `requirements*.txt`, `pyproject.toml`.
 - `pull_request:`
   - Outro gatilho gatilho (trigger) do workflow.
   - `branches: [ ci-cd ]`
     - Novamente, só será acionado na branch *"ci-cd"*
   - `paths:`
     - Novamente, só é executado quando houver mudanças em `arquivos Python`, `requirements*.txt`, `pyproject.toml`.

> **NOTE:**  
> Essas configurações aqui são referentes aos gatilhos que forçam o workflow a rodar.

Continundo, agora nós vamos criar uma seção para `jobs`:

[lint.yml](../.github/workflows/lint.yml)
```yaml
jobs:
  ...
```

 - `jobs:`
   - Um workflow pode ter vários **"jobs"** (testar, build, deploy, lint, etc.).
   - Mas, nesse nosso exemplo só vamos ter o *"lint"*.

Agora nós vamos criar uma tarefa (job) com o nome `lint-ci` que vai ser executada no SO `ubuntu-latest`:

[lint.yml](../.github/workflows/lint.yml)
```yaml
jobs:
  lint-ci:
    runs-on: ubuntu-latest
```

 - `lint-ci`
   - É o nome da tarefa (job).
 - `runs-on: ubuntu-latest`
   - A *runner (SO)* que vai rodar essa tarefa.

Agora, dentro dessa `tarefa (lint-ci)`, na máquina `ubuntu-latest`, nós vamos ter alguns `passos (steps)` que serão executados:

[lint.yml](../.github/workflows/lint.yml)
```yaml
jobs:
  lint-ci:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.12"

      - name: Install dependencies for lint
        run: |
          python -m venv .venv
          source .venv/bin/activate
          python -m pip install --upgrade pip
          pip install ruff
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

      - name: Run Ruff (lint)
        run: |
          source .venv/bin/activate
          ruff check .
```

 - `steps`
   - Uma lista de passos que vão ser executados na runner.
 - `name: Checkout`
 - `uses: actions/checkout@v4`
   - Diz ao GitHub que queremos usar a Action oficial para clonar o repositório.
 - `name: Set up Python`
 - `uses: actions/setup-python@v4`
   - `with:`
     - `python-version: "3.12"`
     - Action oficial de instalação do Python (com a versão 3.12).

> **NOTE:**  
> Não vou explicar os demais `steps` linh a linha porque a partir deste ponto acredito que seja possivel entender a maioria dos comandos.

> **O comando `name:` pode ser qualquer texto.**  
> Ele serve apenas como identificador visual no *GitHub Actions*, para você conseguir ler no painel.

### `Workflow completo`

[lint.yml](../.github/workflows/lint.yml)
```yaml
name: Lint

on:
  push:
    branches: [ ci-cd ]
    paths:
      - "**/*.py"
      - "requirements*.txt"
      - "pyproject.toml"
  pull_request:
    branches: [ ci-cd ]
    paths:
      - "**/*.py"
      - "requirements*.txt"
      - "pyproject.toml"

jobs:
  lint-ci:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.12"

      - name: Install dependencies for lint
        run: |
          python -m venv .venv
          source .venv/bin/activate
          python -m pip install --upgrade pip
          pip install ruff
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

      - name: Run Ruff (lint)
        run: |
          source .venv/bin/activate
          ruff check .
```

> **NOTE:**  
> Continuando, agora é só fazer o commit e push ou pull_request na branche ci-cd que o workflow será acionado.









































































































<!--- ( Testes ) --->

---

<div id="manage-py-tests"></div>

## `Criando testes para o manage.py`

> Aqui nós vamos criar alguns testes simples (só para o nosso Pytest passar no pre-commit) para o [manage.py](../manage.py).

### `test_main_sets_django_settings_module_when_not_set()`

De início, vamos criar um arquivo chamado [test_manage.py](../tests/test_manage.py) e importar a função `main()` do arquivo [manage.py](../manage.py):

[test_manage.py](../tests/test_manage.py)
```python
"""Tests for manage.py."""
import manage

main = manage.main
```

Agora vamos implementar uma função de teste chamada `test_main_sets_django_settings_module_when_not_set` que vai ser responsável por:

 - Verificar se a função `main()` do [manage.py](../manage.py) configura corretamente a variável de ambiente `DJANGO_SETTINGS_MODULE` quando ela ainda não existe;
 - E se o Django é executado com os argumentos certos.

> **Em outras palavras:**  
> 👉 Queremos ter certeza de que o manage.py funciona mesmo quando o ambiente ainda não está configurado.

Vamos começar criando uma função que começa com `test_` e que recebe `monkeypatch` como argumento:

[test_manage.py](../tests/test_manage.py)
```python
def test_main_sets_django_settings_module_when_not_set(monkeypatch):
    ...
```

 - **O nome da função começa com `test_` → pytest reconhece automaticamente**
 - **monkeypatch é uma ferramenta do pytest que permite:**
   - alterar variáveis de ambiente
   - substituir funções
   - simular comportamentos
   - **NOTE:** 💡 Pense no `monkeypatch` como um *"controle remoto do ambiente durante o teste"*.

Agora, vamos criar um **“registrador de chamadas”**:

[test_manage.py](../tests/test_manage.py)
```python
def test_main_sets_django_settings_module_when_not_set(monkeypatch):

    called_args = []
```

 - Criamos uma lista vazia para guardar informações depois.
 - 👉 Vamos usá-la para verificar:
   - se uma função foi chamada
   - com quais argumentos ela foi chamada

Continuando, agora nós vamos criar uma **função falsa (mock)**: 

[test_manage.py](../tests/test_manage.py)
```python
def test_main_sets_django_settings_module_when_not_set(monkeypatch):

    ...

    def mock_execute(args):
        called_args.append(args)
```

 - **Aqui estamos criando uma função falsa que vai substituir:**
   - `execute_from_command_line`
 - **Em vez de:**
   - iniciar o Django
   - rodar comandos reais
 - **Ela apenas:**
   - recebe os argumentos
   - guarda esses argumentos em called_args (com .append())

> **NOTE:**  
> ✅ Isso deixa o teste rápido e seguro.

Continuando, no arquivo [manage.py](../manage.py) dentro da função `main()`, nós temos a variável de ambiente `DJANGO_SETTINGS_MODULE`:

[manage.py](../manage.py)
```python
def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

    ...
```

Agora, nós vamos garantir que essa variável de ambiente (`DJANGO_SETTINGS_MODULE`) não exista no nosso teste:

[test_manage.py](../tests/test_manage.py)
```python
def test_main_sets_django_settings_module_when_not_set(monkeypatch):

    ...

    monkeypatch.delenv('DJANGO_SETTINGS_MODULE', raising=False)
```

Continuando, agora nós vamos substituir a `função real (execute_from_command_line)` pela `função falsa (mock_execute)`:

[test_manage.py](../tests/test_manage.py)
```python
import manage

def test_main_sets_django_settings_module_when_not_set(monkeypatch):

    ...

    monkeypatch.setattr(manage, 'execute_from_command_line', mock_execute)
```

Aqui acontece a mágica:

 - **Onde o código original (import manage) chamaria:**
   - `execute_from_command_line`
 - **Agora ele chamará:**
   - `mock_execute(...)`

> **NOTE:**  
> 👉 Assim conseguimos observar o comportamento sem efeitos colaterais.

Agora, nós vamos simular um comando digitado no terminal:

[test_manage.py](../tests/test_manage.py)
```python
def test_main_sets_django_settings_module_when_not_set(monkeypatch):

    ...

    monkeypatch.setattr(sys, 'argv', ['manage.py', 'help'])
```

 - **Isso simula o comando:**
   - `python manage.py help`
 - Ou seja:
   - `sys.argv[0]` → manage.py
   - `sys.argv[1]` → help

> **NOTE:**  
> 💡 É como se o usuário tivesse rodado o comando no terminal.

Agora, nós vamos executar a função testada:

[test_manage.py](../tests/test_manage.py)
```python
def test_main_sets_django_settings_module_when_not_set(monkeypatch):

    ...

    main()
```

Neste momento a função `main()`:

 - percebe que `DJANGO_SETTINGS_MODULE` não existe
 - define essa variável
 - chama `execute_from_command_line`
 - que agora está mockada

Lembram, que no arquivo [manage.py](../manage.py) nós criamos a variável de ambiente `DJANGO_SETTINGS_MODULE` que recebeu o valor `core.settings`?

[manage.py](../manage.py)
```python
def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
```

Então, agora nós vamos criar um `assert` que vai ser verificar se a variável de ambiente `DJANGO_SETTINGS_MODULE` é igual a `core.settings`:

[test_manage.py](../tests/test_manage.py)
```python
def test_main_sets_django_settings_module_when_not_set(monkeypatch):

    ...

    assert os.environ.get('DJANGO_SETTINGS_MODULE') == 'core.settings'
```

Se você rodar esse teste agora, obrigatoriamente ele deve passar:

**OUTPUT:**
```bash
tests/test_manage.py::test_main_sets_django_settings_module_when_not_set PASSED
```

Mas ainda falta um `assert` que verificar se o Django foi chamado corretamente:

[test_manage.py](../tests/test_manage.py)
```python
def test_main_sets_django_settings_module_when_not_set(monkeypatch):

    ...

    assert called_args == [['manage.py', 'help']]
```

Aqui confirmamos que:

 - `execute_from_command_line` foi chamado
 - recebeu exatamente os argumentos simulados

**OUTPUT:**
```bash
tests/test_manage.py::test_main_sets_django_settings_module_when_not_set PASSED
```

> **NOTE:**  
> Essa minha função tem 2 `asserts` o que **não é ideal** o interessante é ter um teste por vez.





















































---

<div id="test-admin-url-is-registered"></div>

## `Testando se a URL /admin/ está registrada corretamente`

> Aqui, nós vamos criar um teste automatizado simples para garantir que a URL `/admin/` está corretamente registrada no sistema de rotas do Django.

Vamos começar criando uma **função de teste** chamada `test_admin_url_is_registered()`:

[tests/test_urls.py](../tests/test_urls.py)
```python
def test_admin_url_is_registered():
    """
    Testa se a URL /admin/ está registrada no sistema de rotas do Django.
    """
    ...
```

### `🅰️ Arrange — Preparando o cenário`

Continuando, nesta etapa (Arrange), nós não vamos precisar preparar quase nada, porque:

 - o Django já carrega automaticamente o `ROOT_URLCONF`
 - o arquivo `core/urls.py` já está configurado no projeto

Mesmo assim, precisamos importar a função que será usada para testar URLs:

[tests/test_urls.py](../tests/test_urls.py)
```python
from django.urls import resolve
```

 - A função `resolve()`:
   - recebe uma URL como string
   - tenta encontrar essa URL no `urlpatterns = [...]`
   - retorna informações sobre a rota encontrada

### `🅰️🅰️ Act — Executando a ação`

Agora vamos executar a ação (Act) principal do teste que vai ser **pedir para o Django resolver a URL `/admin/`**:

[tests/test_urls.py](../tests/test_urls.py)
```python
from django.urls import resolve


def test_admin_url_is_registered():
    """
    Testa se a URL /admin/ está registrada no sistema de rotas do Django.
    """

    # Arrange
    # (não é necessário preparar nada além do carregamento do Django)

    # Act
    match = resolve('/admin/')
```

 - **O que a função `resolve()` faz?**
   - Ela serve para descobrir qual view o Django executaria ao receber uma determinada URL.
   - Em outras palavras:
     - 👉 “Se um usuário acessasse essa URL no navegador, qual código (view) seria chamado?”
 - **Quais parâmetros `resolve()` recebe?**
   - 1️⃣ `path (obrigatório)`
     - É o caminho da URL, exatamente como o Django receberia na requisição HTTP
     - Por exemplo, `/admin/`
   - 2️⃣ `urlconf (opcional)`
     - Permite especificar manualmente um conjunto de URLs
     - Normalmente não é usado em testes comuns
 - **O que a função resolve() retorna?**
   - Se a URL for encontrada, resolve() retorna um objeto do tipo:
     - `django.urls.resolvers.ResolverMatch`
   - Principais atributos retornados:
     - `match.func` → A view que será chamada
     - `match.view_name` → Nome da view (se houver)
     - `match.args` → Argumentos posicionais da URL
     - `match.kwargs` → Argumentos nomeados da URL
     - `match.route` → Padrão da rota que deu match

### `🅰️🅰️🅰️ Assert — Verificando o resultado`

Continuando, agora vamos criar um único `assert` que verifique se a URL `/admin/` foi encontrada:

[tests/test_urls.py](../tests/test_urls.py)
```python
from django.urls import resolve


def test_admin_url_is_registered():
    """
    Testa se a URL /admin/ está registrada no sistema de rotas do Django.
    """

    # Arrange
    # (não é necessário preparar nada além do carregamento do Django)

    # Act
    match = resolve('/admin/')

    # Assert
    assert match is not None
```

 - **O que esse assert garante?**
   - Que o Django conseguiu resolver a URL /admin/
   - Que essa rota está registrada
   - Que o arquivo core/urls.py está funcionando corretamente
   - 👉 Se a URL for removida, alterada ou quebrada, esse teste falha.

### `📄 Código final completo do teste`

[tests/test_urls.py](../tests/test_urls.py)
```python
from django.urls import resolve


def test_admin_url_is_registered():
    """
    Testa se a URL /admin/ está registrada no sistema de rotas do Django.
    """

    # Arrange
    # (não é necessário preparar nada além do carregamento do Django)

    # Act
    match = resolve('/admin/')

    # Assert
    assert match is not None
```

### `Testando`

Se você desejar rodar esse teste específico você pode executar o seguinte comando:

```bash
pytest -s -x --cov=. -vv tests/test_urls.py::test_admin_url_is_registered
```





















































---

<div id="test-asgi-application-is-created"></div>

## `Testando se a aplicação ASGI do Django é criada corretamente`

Aqui, nós vamos criar um teste automatizado simples para garantir que o arquivo `core/asgi.py` está configurado corretamente e que o Django consegue criar a aplicação ASGI do projeto.

> **👉 Em termos simples:**  
> “Esse teste garante que o Django conseguiu inicializar a aplicação ASGI sem erros.”

Esse teste é importante porque:

 - o ASGI é usado por servidores como Daphne, Uvicorn e Hypercorn
 - qualquer erro nesse arquivo impede o projeto de subir em produção

Vamos começar criando uma **função de teste** chamada `test_asgi_application_is_created()`:

[tests/test_asgi.py](../tests/test_asgi.py)
```python
def test_asgi_application_is_created():
    """
    Testa se a aplicação ASGI do Django é criada corretamente.
    """
```

### `🅰️ Arrange — Preparando o cenário`

Nesta etapa, nós não precisamos preparar quase nada manualmente.

Isso porque:

 - o Django já carrega automaticamente as configurações
 - o arquivo `core/asgi.py` já define:

```python
os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'core.settings',
)
```

O que precisamos fazer aqui é importar o objeto que será testado.

[tests/test_asgi.py](../tests/test_asgi.py)
```python
from core.asgi import application


def test_asgi_application_is_created():
    """
    Testa se a aplicação ASGI do Django é criada corretamente.
    """
```

> **🔍 O que acontece nesse import?**

 - O Python executa o arquivo core/asgi.py
 - O Django:
   - garante que `DJANGO_SETTINGS_MODULE` está definido
 - chama `get_asgi_application()` (que está em `core/asgi.py`)
 - O objeto `application` é criado

### `🅰️🅰️ Act — Executando a ação`

Aqui a ação é mínima, mas ainda existe:

> 👉 Nós simplesmente acessamos o objeto application.

[tests/test_asgi.py](../tests/test_asgi.py)
```python
from core.asgi import application


def test_asgi_application_is_created():
    """
    Testa se a aplicação ASGI do Django é criada corretamente.
    """

    # Arrange
    # (nenhuma preparação manual é necessária)

    # Act
    app = application
```

Isso confirma que:

 - o import foi bem-sucedido
 - o objeto existe em memória

### `🅰️🅰️🅰️ Assert — Verificando o resultado`

Agora vamos criar um único `assert`, focando em uma coisa só:

[tests/test_asgi.py](../tests/test_asgi.py)
```python
from core.asgi import application


def test_asgi_application_is_created():
    """
    Testa se a aplicação ASGI do Django é criada corretamente.
    """

    # Arrange
    # (nenhuma preparação manual é necessária)

    # Act
    app = application

    # Assert
    assert callable(app)
```

> **O que esse assert garante?**

 - **Que application:**
   - existe
   - é um objeto chamável
 - **Ou seja:**
   - o Django criou corretamente a aplicação ASGI
 - **Se houver erro em:**
   - settings
   - imports
   - middleware
   - apps instalados
   - **NOTE:** esse teste falha automaticamente.

### `📄 Código final completo do teste`

[tests/test_asgi.py](../tests/test_asgi.py)
```python
from core.asgi import application


def test_asgi_application_is_created():
    """
    Testa se a aplicação ASGI do Django é criada corretamente.
    """

    # Arrange
    # (nenhuma preparação manual é necessária)

    # Act
    app = application

    # Assert
    assert callable(app)
```


### `Testando`

Se você desejar rodar esse teste específico você pode executar o seguinte comando:

```bash
pytest -s -x --cov=. -vv tests/test_asgi.py::test_asgi_application_is_created
```

---

**Rodrigo** **L**eite da **S**ilva - **rodrigols89**
