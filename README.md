# gab_bookstore_api

Este documento fornece um guia completo para configuração, execução e uso da API de livraria (gab_bookstore_api). Serve como um README técnico pronto para uso em produção, com exemplos de código e instruções passo a passo.

---

## 1. Configuração de Variáveis de Ambiente (.env)

Para rodar via Docker Compose, crie dois arquivos de ambiente em `docker/local/`:

- **python_api.env** (API)
- **python_admin.env** (Admin)

> **Importante:**  
> - Adicione ambos ao `.gitignore`.  
> - Mantenha um `.env.example` sem valores sensíveis para referência.

### Exemplo: `docker/local/python_api.env`
```env
# Configurações Django (API)
DJANGO_SECRET_KEY=django-insecure-123
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Configurações do Banco de Dados (Postgres)
POSTGRES_DB=gab_bookstore
POSTGRES_USER=gab_user
POSTGRES_PASSWORD=super-secret-pwd
POSTGRES_PORT=5432
DATABASE_HOST=database

# Broker do Celery (Redis)
CELERY_BROKER_URL=redis://redis:6379/1
```

### Exemplo: `docker/local/python_admin.env`
```env
# Configurações Django (Admin)
DJANGO_SECRET_KEY=local_development_admin_secret_key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
DJANGO_SETTINGS_MODULE=gab_bookstore.settings.admin_local

# Banco de Dados (mesmos valores da API)
POSTGRES_DB=gab_bookstore
POSTGRES_USER=gab_user
POSTGRES_PASSWORD=super-secret-pwd
POSTGRES_PORT=5432
DATABASE_HOST=database

# Tipo de servidor
SERVER_TYPE=admin

# Config de desenvolvimento (ex: toolbar)
DEBUG_TOOLBAR=True
```

- **`DJANGO_SETTINGS_MODULE`** define quais settings usar.  
- **`SERVER_TYPE`** controla roteamento (API vs Admin).  
- As variáveis `POSTGRES_*` devem ser idênticas nos serviços `database`, `api` e `admin`.

---

## 2. Instalação do Docker e Docker Compose

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin
sudo systemctl start docker
sudo systemctl enable docker
# Opcional: rodar Docker sem sudo
sudo usermod -aG docker $USER
# Faça logout/login após adicionar ao grupo
docker compose version
```

### Windows
1. Instale o **Docker Desktop** (inclui Engine + Compose).  
2. Habilite WSL2 ou Hyper‑V conforme instruções do instalador.  
3. Verifique:
```powershell
docker --version
docker compose version
```

> **Observação:** este projeto usa `docker compose` (plugin v2). Se precisar, ainda existe `docker‑compose` via pip, mas prefira o plugin oficial.

---

## 3. Executando a Aplicação com Docker Compose

1. **Build das imagens** (na raiz do projeto):
   ```bash
   docker compose build
   ```

2. **Subir containers**:
   ```bash
   docker compose up
   ```
   - Serviço `database` (PostGIS)
   - Serviço `redis`
   - Serviço `api` (Django API, porta 8000)
   - Serviço `admin` (Django Admin, porta 9000)
   - `celery`, `celery-beat`, `flower` (opcionais)

3. **Detached mode**:
   ```bash
   docker compose up -d
   ```

4. **Verificação**:
   - Swagger UI: http://localhost:8000/swagger/  
   - Django Admin: http://localhost:9000/admin/  
   - Flower: http://localhost:5555/  

5. **Parar e remover containers**:
   ```bash
   docker compose down
   ```

> **Dicas de troubleshooting:**  
> - `docker compose logs <serviço>` para ver erros.  
> - Cheque formatação dos arquivos `.env` (sem aspas).  
> - Em Windows, verifique firewall e WSL2.

---

## 4. Fluxo de Autenticação JWT (`/api/v1/auth/login/`)

A API usa **djangorestframework-simplejwt**:

### 4.1 Login
- **Endpoint:** `POST /api/v1/auth/login/`
- **Request Body**:
  ```json
  {
    "username": "seu_usuario",
    "password": "sua_senha"
  }
  ```
- **Response (200)**:
  ```json
  {
    "refresh": "<token_refresh>",
    "access":  "<token_access>"
  }
  ```
- **Uso:**  
  ```http
  Authorization: Bearer <seu_token_access>
  ```

### 4.2 Refresh Token
- **Endpoint:** `POST /api/v1/auth/refresh/`
- **Body**:
  ```json
  { "refresh": "<token_refresh>" }
  ```

### 4.3 Blacklist (Logout)
- **Endpoint:** `POST /api/v1/auth/blacklist/`
- **Body**:
  ```json
  { "refresh": "<token_refresh>" }
  ```

### 4.4 Swagger UI
1. Acesse `/swagger/`.  
2. Faça login via `POST /auth/login/`.  
3. Clique em **Authorize**, cole `Bearer <access>`.

---

## 5. Sistema de Usuários

Modelo `users.models.User` estende `AbstractUser` com campo adicional:

- **`user_type`** (`CharField`):  
  - `"client"` (padrão)  
  - `"staff"`

- **`is_staff`** (padrão do Django) controla acesso ao Admin e permissões.

### 5.1 Criação de Usuários
- **Endpoint:** `POST /api/v1/auth/create/`
- **Body**:
  ```json
  {
    "username": "novo_user",
    "password": "senha",
    "user_type": "client"  // opcional
  }
  ```
- **Respostas**:
  - `201 Created` → usuário criado.
  - `200 OK` → já existia (`{"detail":"User already exists","id":<id>}`).

> **Permissões:**  
> - Qualquer um pode criar **client**.  
> - Para criar **staff**, ative `is_staff` manualmente (via Admin).

---

## 6. API de Livros – Rotas e Comportamento

Prefixo: `/api/v1/books/books/`

### 6.1 Listar livros (GET)
- **GET** `/api/v1/books/books/`  
- **Acesso:** público  
- **Cache:** 1 hora  
- **Response 200**: lista de objetos:
  ```json
  [
    {
      "id": 1,
      "isbn": "9780007458424",
      "title": "The Hobbit",
      "author": "J. R. R. Tolkien",
      "description": "...",
      "published_date": "2012-06-01",
      "cover_thumbnail": "...",
      "publisher": "...",
      "page_count": 368,
      "copies": 1
    },
    
  ]
  ```

### 6.2 Detalhar livro (GET)
- **GET** `/api/v1/books/books/{id}/`  
- **Acesso:** público  
- **Response 200**: objeto livro ou `404 Not Found`.

### 6.3 Criar livro (POST)
- **POST** `/api/v1/books/books/`  
- **Acesso:** **staff**  
- **Body mínimo**:
  ```json
  { "isbn": "9780007458424" }
  ```
- **Enriquecimento:** busca no Google Books para preencher campos faltantes.  
- **Response 201**: objeto criado.  
- **Erros**:  
  - `400 Bad Request` (ISBN inválido ou título não encontrado)  
  - `403 Forbidden` (não staff)


### 6.5 Deletar livro (DELETE)
- **DELETE** `/api/v1/books/books/{id}/`  
- **Acesso:** **staff**  
- **Response 204**: sem conteúdo.

### 6.6 Emprestar livro (POST)
- **POST** `/api/v1/books/books/{id}/borrow/`  
- **Acesso:** **client** autenticado  
- **Negócio:**  
  - Decrementa `copies` atomically.  
  - Cria `Borrow` com `due_date = hoje + 14 dias`.  
- **Response 201**: dados do empréstimo.  
- **Erros**:  
  - `400 Bad Request` (sem cópias)  
  - `401/403` (não autenticado ou staff)

### 6.7 Devolver livro (POST)
- **POST** `/api/v1/books/books/{id}/return_it/`  
- **Acesso:** **client**  
- **Negócio:**  
  - Marca `Borrow` como `returned`.  
  - Incrementa `copies` do livro.  
- **Response 200**: dados do empréstimo atualizado.  
- **Erros**:  
  - `400 Bad Request` (nenhum empréstimo ativo)  
  - `401/403`


### 7 Seed Data
- **docker compose exec api python manage.py populate_book**: método criado para popular  a criação de seed data a partir de faker
- **já incluído na migração**

### 8 Pagination
é possível escolher o limite por página e o offset manualmente, tendo-se um padrão de 20 items por pagina

---

### Observações Finais

- **Validação ISBN**: não há validação estrita além de `unique`.  
- **Cache Google Books**: resultados em Redis por 7 dias.  
- **Cache de página**: listagem e detalhe de livros em Redis por 1 hora.  
- **Exemplos**: use Swagger UI em `/swagger/` para testar todos os endpoints.