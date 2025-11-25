# SIGO API

API REST desenvolvida com FastAPI seguindo o padrão arquitetural MVC (Model-View-Controller).

## 📋 Estrutura do Projeto

```
sigo-api/
├── controller/          # Controllers - Lógica de negócio
│   ├── auth_controller.py
│   └── user_controller.py
├── models/             # Models - Modelos de dados (ORM)
│   └── user.py
├── schemas/            # Schemas - Validação de dados (Pydantic)
│   └── user_schema.py
├── views/              # Views - Rotas e endpoints HTTP
│   ├── auth_view.py
│   └── user_view.py
├── database.py         # Configuração do banco de dados
├── main.py            # Aplicação principal
└── pyproject.toml     # Dependências do projeto
```

## 🏗️ Padrão MVC

### Model (Modelo)

- **Localização**: `models/`
- **Responsabilidade**: Define a estrutura dos dados e interage diretamente com o banco de dados
- **Exemplo**: `User` - modelo SQLAlchemy com métodos de negócio relacionados aos dados (hash de senha, verificação)

### View (Visão)

- **Localização**: `views/`
- **Responsabilidade**: Define as rotas HTTP, recebe requisições, valida dados de entrada via schemas Pydantic
- **Exemplo**: `router_auth` - endpoints REST que recebem requests e retornam responses HTTP

### Controller (Controlador)

- **Localização**: `controller/`
- **Responsabilidade**: Contém a lógica de negócio, processa dados entre View e Model
- **Exemplo**: `AuthController` - autentica usuários, gera tokens JWT

### Schemas (Pydantic)

- **Localização**: `schemas/`
- **Responsabilidade**: Valida dados de entrada/saída, serialização/deserialização
- **Exemplo**: `LoginRequest`, `UserResponse` - validação de tipos e estrutura de dados

## 🚀 Instalação

1. Clone o repositório:

```bash
git clone <repository-url>
cd sigo-api
```

2. Instale as dependências:

```bash
pip install -e .
```

## ⚙️ Configuração

Crie um arquivo `.env` na raiz do projeto:

```env
# Database
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_HOST=localhost
DB_NAME=sigo_db

# Server
SERVER_PORT=8000

# JWT
SECRET_KEY=sua-chave-secreta-super-segura
```

## 🎯 Endpoints

### Autenticação

- `POST /v1/login` - Autenticar usuário e obter token JWT

### Usuários

- `POST /v1/users` - Criar novo usuário
- `GET /v1/users` - Listar usuários (com paginação)
- `GET /v1/users/{user_id}` - Obter usuário por ID
- `PUT /v1/users/{user_id}` - Atualizar usuário
- `DELETE /v1/users/{user_id}` - Deletar usuário (soft delete)

## 🏃 Executando

```bash
python main.py
```

Ou com uvicorn diretamente:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Acesse a documentação interativa em: `http://localhost:8000/docs`

## 📚 Tecnologias

- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy** - ORM para Python
- **Pydantic** - Validação de dados
- **PostgreSQL** - Banco de dados
- **JWT** - Autenticação via tokens
- **Passlib + Bcrypt** - Hashing de senhas

## 🔐 Segurança

- Senhas são hasheadas usando bcrypt
- Autenticação via JWT tokens
- Validação de entrada com Pydantic
- Soft delete para usuários

## 📝 Exemplo de Uso

### Login

```bash
curl -X POST "http://localhost:8000/v1/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "senha123"}'
```

### Criar Usuário

```bash
curl -X POST "http://localhost:8000/v1/users" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "João Silva",
    "email": "joao@example.com",
    "password": "senha123",
    "userBusinessArea": "TI"
  }'
```
