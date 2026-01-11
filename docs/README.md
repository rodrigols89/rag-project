# RAG Project

> **Tutorial de como este projeto foi desenvolvido, passo a passo.**

## Conteúdo

 - [`Adicionando .editorconfig e .gitignore`](#editorconfig-gitignore)
 - [`Iniciando o projeto com "poetry init"`](#poetry-init)
 - [`Instalando e configurando o Taskipy`](#taskipy-settings-pyproject)
 - [`Instalando/Configurando/Exportando o Django + Uvicorn`](#django-settings)
 - [`Criando o container com PostgreSQL (db)`](#db-container)
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

Antes de criar nosso container contendo o *PostgreSQL* vamos criar as variáveis de ambiente para esse container:

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

Agora nós vamos criar o compose `base` que vai ter as configurações base dos nossos containers:

[docker-compose.yml](../docker-compose.yml)
```yml

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

Continuando, agora nós vamos criar o compose de `desenvolvimento` que terá as configurações de *desenvolvimento*:

[docker-compose.dev.yml](../docker-compose.dev.yml)
```yml

```

Por fim, vamos criar o compose de `produção` que terá as configurações de *produção*:

[docker-compose.prod.yml](../docker-compose.prod.yml)
```yml
# --------------- ( Docker (dev) Management ) ---------------
start_dev = "docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d"
down_dev = "docker compose -f docker-compose.yml -f docker-compose.dev.yml down"
restart_dev = "docker compose -f docker-compose.yml -f docker-compose.dev.yml restart"
build_dev = "docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d"
# -------------- ( Docker (prod) Management ) ---------------
start_prod = "docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d"
down_prod = "docker compose -f docker-compose.yml -f docker-compose.prod.yml down"
restart_prod = "docker compose -f docker-compose.yml -f docker-compose.prod.yml restart"
build_prod = "docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d"
```

Ótimo, agora é só subir o container:

```bash
task start_dev
```

Agora, vamos ver o log do container para ver se está tudo ok:

```bash
docker logs rag-project-db-1
```

**OUTPUT:**
```bash
2026-01-11 16:06:12.671 UTC [1] LOG:  listening on IPv4 address "0.0.0.0", port 5432
2026-01-11 16:06:12.671 UTC [1] LOG:  listening on IPv6 address "::", port 5432
2026-01-11 16:06:12.675 UTC [1] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
2026-01-11 16:06:12.680 UTC [64] LOG:  database system was shut down at 2026-01-11 16:06:12 UTC
2026-01-11 16:06:12.684 UTC [1] LOG:  database system is ready to accept connections
2026-01-11 16:06:21.782 UTC [75] FATAL:  database "raguser" does not exist
2026-01-11 16:06:30.376 UTC [83] FATAL:  database "raguser" does not exist
2026-01-11 16:06:40.466 UTC [91] FATAL:  database "raguser" does not exist
```

> **What?**

 - 👉 O PostgreSQL está tentando conectar a um banco chamado raguser
 - 👉 mas o banco que deveria existir é rag_db (pelo seu .env)

Para resolver esse problema, primeiro vamos entender como o PostgreSQL decide qual banco conectar:

 - **1️⃣ Como o Postgres decide qual banco conectar?**
   - Quando nenhum banco é especificado, o Postgres tenta conectar em:
     - `database = username`
   - Ou seja:
     - `POSTGRES_USER=raguser`
   - Ele tenta abrir automaticamente:
     - `database = raguser`
   - Mas você configurou (.env):
     - `POSTGRES_DB=rag_db`
   - Então:
     - ✅ Banco criado: `rag_db`
     - ❌ Banco tentado: `raguser`
   - Resultado:
     - *"database "raguser" does not exist"*
 - **2️⃣ O detalhe MAIS IMPORTANTE: volume persistente:**
   - Você está usando:
     - `volumes: postgres_data:/var/lib/postgresql/data`
     - ⚠️ O Postgres só cria o banco (POSTGRES_DB) na PRIMEIRA inicialização do volume.
   - Se o volume já existia antes:
     - Ele IGNORA completamente:
       - `POSTGRES_DB`
       - `POSTGRES_USER`
       - `POSTGRES_PASSWORD`
   - 👉 As variáveis não são reaplicadas.

> **Ok, mas como eu posso resolver isso de uma maneira simples?**

**⚠️ APAGA TODOS OS DADOS:**
```bash
docker compose down -v
docker compose up -d
```

 - ✔️ Volume recriado
 - ✔️ `POSTGRES_DB=rag_db` criado corretamente
 - ✔️ Erro desaparece

> **NOTE:**  
> 👉 Essa é a solução recomendada para desenvolvimento.

Agora, vamos subir o container novamente e ver o log:

```bash
task start_dev
```

```bash
docker logs rag-project-db-1
```

**OUTPUT:**
```bash
PostgreSQL init process complete; ready for start up.

2026-01-11 16:36:11.730 UTC [1] LOG:  starting PostgreSQL 15.15 (Debian 15.15-1.pgdg13+1) on x86_64-pc-linux-gnu, compiled by gcc (Debian 14.2.0-19) 14.2.0, 64-bit
2026-01-11 16:36:11.730 UTC [1] LOG:  listening on IPv4 address "0.0.0.0", port 5432
2026-01-11 16:36:11.730 UTC [1] LOG:  listening on IPv6 address "::", port 5432
2026-01-11 16:36:11.864 UTC [1] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
2026-01-11 16:36:11.871 UTC [64] LOG:  database system was shut down at 2026-01-11 16:36:11 UTC
2026-01-11 16:36:11.976 UTC [1] LOG:  database system is ready to accept connections
```

Ótimo, agora se você desejar se conectar nesse Banco de Dados via *bash* utilize o seguinte comando (As vezes é necessário esperar o container/banco de dados subir):

**Entrar no container "postgres_db" via bash:**
```bash
docker exec -it rag-project-db-1 bash
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

**Rodrigo** **L**eite da **S**ilva - **rodrigols89**
